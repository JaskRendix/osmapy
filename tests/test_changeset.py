from unittest.mock import MagicMock, patch

import lxml.etree as ET
import pytest

from osmapy.Changeset.Changeset import Changeset


@pytest.fixture
def mock_parent():
    parent = MagicMock()
    parent.element_viewer = MagicMock()
    parent.elements_loader = MagicMock()
    parent.viewer = MagicMock()
    return parent


@pytest.fixture
def changeset(mock_parent):
    with patch("osmapy.Changeset.Changeset.config") as mock_cfg:
        mock_cfg.osm_api_url = "https://api.openstreetmap.org"
        mock_cfg.user_agent = "OsmapyTestAgent"
        instance = Changeset(mock_parent)
        return instance


@patch("requests.put")
def test_create_changeset_success(mock_put, changeset):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "12345"
    mock_put.return_value = mock_response

    changeset.username = "test_user"
    changeset.password = "test_pass"

    status = changeset.create_changeset("Test comment")

    assert status == 200
    assert changeset.changeset_id == 12345
    mock_put.assert_called_once()


@patch("requests.post")
def test_upload_diff(mock_post, changeset):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    changeset.changeset_id = 12345
    changeset.username = "test_user"
    changeset.password = "test_pass"

    xml_data = "<osmChange></osmChange>"
    status = changeset.upload_diff(xml_data)

    assert status == 200
    mock_post.assert_called_once()


@patch("requests.put")
def test_close_changeset(mock_put, changeset):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_put.return_value = mock_response

    changeset.changeset_id = 12345
    changeset.username = "test_user"
    changeset.password = "test_pass"

    status = changeset.close()

    assert status == 200
    mock_put.assert_called_once()


def test_create_osmChange(changeset, mock_parent):
    mock_node_created = MagicMock()
    mock_node_created.create_xml.return_value = ET.Element("node", id="-1")

    mock_node_deleted = MagicMock()
    mock_node_deleted.id = 101
    mock_node_deleted.create_xml.return_value = ET.Element("node", id="101")

    mock_node_modified_orig = MagicMock()
    mock_node_modified_new = MagicMock()
    mock_node_modified_new.id = 102
    mock_node_modified_new.create_xml.return_value = ET.Element("node", id="102")

    mock_parent.elements_loader.elements = {
        "new_1": mock_node_created,
        "mod_1": mock_node_modified_new,
    }
    mock_parent.elements_loader.elements_copy = {
        "del_1": mock_node_deleted,
        "mod_1": mock_node_modified_orig,
    }

    tree = changeset.create_osmChange(changeset_id=12345)
    root = tree.getroot()

    assert root.tag == "osmChange"
    assert len(root.find("create")) == 1
    assert len(root.find("delete")) == 1
    assert len(root.find("modify")) == 1


@patch("requests.put")
@patch("requests.post")
def test_submit_full_workflow(mock_post, mock_put, changeset, mock_parent):
    # First put (create), second put (close)
    mock_put.side_effect = [
        MagicMock(status_code=200, text="999"),
        MagicMock(status_code=200),
    ]
    # Post (upload diff)
    mock_post.return_value = MagicMock(status_code=200)

    mock_parent.elements_loader.elements = {}
    mock_parent.elements_loader.elements_copy = {}

    status = changeset.submit("Full workflow test", "user", "pass")

    assert status == 200
    mock_parent.element_viewer.clear.assert_called_once()
    mock_parent.elements_loader.clear.assert_called_once()
    mock_parent.viewer.update.assert_called_once()
