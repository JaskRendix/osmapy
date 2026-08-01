from unittest.mock import MagicMock, patch

import pytest

from osmapy.Changeset.ChangesetForm import ChangesetForm


class MockConfigDict(dict):

    def __getattr__(self, item):
        if item in self:
            return self[item]
        raise AttributeError(f"'dict' object has no attribute '{item}'")

    def __setattr__(self, key, value):
        self[key] = value


@pytest.fixture
def mock_parent():
    parent = MagicMock()
    parent.changeset.create_osmChange.return_value = MagicMock()
    parent.changeset.submit.return_value = 200
    return parent


@pytest.fixture
def changeset_form(qapp, mock_parent):
    return ChangesetForm(mock_parent)


@patch("osmapy.Changeset.ChangesetForm.config", new_callable=MockConfigDict)
@patch("lxml.etree.tostring")
def test_form_show_initialization(mock_tostring, mock_cfg, changeset_form, mock_parent):
    mock_tostring.return_value = b"<osmChange></osmChange>"
    mock_cfg["login_name"] = "test_user"
    mock_cfg["password"] = "secret_pass"

    changeset_form.show()

    assert changeset_form.windowTitle() == "Upload changes"
    assert changeset_form.username.text() == "test_user"
    assert changeset_form.password.text() == "secret_pass"
    assert changeset_form.layout() is not None
    mock_parent.changeset.create_osmChange.assert_called_once_with(-1)


@patch("lxml.etree.tostring")
def test_click_validation_missing_username(mock_tostring, changeset_form):
    mock_tostring.return_value = b"<osmChange></osmChange>"
    changeset_form.show()

    changeset_form.username.setText("")
    changeset_form.password.setText("pass")
    changeset_form.comment.setText("comment")

    with patch("PySide6.QtWidgets.QMessageBox.exec") as mock_exec:
        changeset_form.click()
        mock_exec.assert_called_once()


@patch("lxml.etree.tostring")
def test_click_validation_missing_password(mock_tostring, changeset_form):
    mock_tostring.return_value = b"<osmChange></osmChange>"
    changeset_form.show()

    changeset_form.username.setText("user")
    changeset_form.password.setText("")
    changeset_form.comment.setText("comment")

    with patch("PySide6.QtWidgets.QMessageBox.exec") as mock_exec:
        changeset_form.click()
        mock_exec.assert_called_once()


@patch("lxml.etree.tostring")
def test_click_validation_missing_comment(mock_tostring, changeset_form):
    mock_tostring.return_value = b"<osmChange></osmChange>"
    changeset_form.show()

    changeset_form.username.setText("user")
    changeset_form.password.setText("pass")
    changeset_form.comment.setText("")

    with patch("PySide6.QtWidgets.QMessageBox.exec") as mock_exec:
        changeset_form.click()
        mock_exec.assert_called_once()


@patch("lxml.etree.tostring")
def test_click_successful_submission(mock_tostring, changeset_form, mock_parent):
    mock_tostring.return_value = b"<osmChange></osmChange>"
    mock_parent.changeset.submit.return_value = 200

    changeset_form.show()
    changeset_form.username.setText("user")
    changeset_form.password.setText("pass")
    changeset_form.comment.setText("Update data")

    with patch("PySide6.QtWidgets.QMessageBox.exec") as mock_exec:
        changeset_form.click()
        mock_parent.changeset.submit.assert_called_once_with(
            "Update data", "user", "pass"
        )
        mock_parent.viewer.load_elements.assert_called_once()
        assert mock_exec.call_count == 1


@patch("lxml.etree.tostring")
def test_click_error_submission(mock_tostring, changeset_form, mock_parent):
    mock_tostring.return_value = b"<osmChange></osmChange>"
    mock_parent.changeset.submit.return_value = 401

    changeset_form.show()
    changeset_form.username.setText("user")
    changeset_form.password.setText("wrong_pass")
    changeset_form.comment.setText("Update data")

    with patch("PySide6.QtWidgets.QMessageBox.exec") as mock_exec:
        changeset_form.click()
        mock_parent.changeset.submit.assert_called_once_with(
            "Update data", "user", "wrong_pass"
        )
        assert mock_exec.call_count == 1
