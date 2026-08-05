from typing import Any

import lxml.etree as ET
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
)

from osmapy.utils.config import load_config

config = load_config()


class ChangesetForm(QDialog):
    """Dialog form to handle changeset commentary, authentication, and submission."""

    def __init__(self, parent: Any) -> None:
        super(ChangesetForm, self).__init__()
        self.parent: Any = parent

        self.status_codes: dict[int, str] = {
            200: "Success",
            400: "Bad request",
            401: "Login was unsuccessful",
            404: "Not found",
            403: "User has been blocked",
            405: "Method Not Allowed",
            409: "Conflict",
        }

        self.comment: QLineEdit = QLineEdit()
        self.username: QLineEdit = QLineEdit()
        self.password: QLineEdit = QLineEdit()

    def show(self) -> None:
        # reset layout
        if self.layout() is not None:
            QDialog().setLayout(self.layout())

        osm_change = ET.tostring(
            self.parent.changeset.create_osmChange(-1), pretty_print=True
        ).decode()

        self.setWindowTitle("Upload changes")

        label1 = QLabel("osmChange file:")
        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(osm_change)

        label2 = QLabel("Comment:")
        self.comment = QLineEdit()

        label3 = QLabel("Username:")
        self.username = QLineEdit()

        label4 = QLabel("Password:")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        button = QPushButton("Submit Changes")

        layout = QGridLayout()
        layout.addWidget(label1, 0, 0, 1, 2)
        layout.addWidget(text, 1, 0, 1, 2)
        layout.addWidget(label2, 2, 0, 1, 1)
        layout.addWidget(self.comment, 2, 1, 1, 1)
        layout.addWidget(label3, 3, 0, 1, 1)
        layout.addWidget(self.username, 3, 1, 1, 1)
        layout.addWidget(label4, 4, 0, 1, 1)
        layout.addWidget(self.password, 4, 1, 1, 1)
        layout.addWidget(button, 5, 0, 1, 2)
        self.setLayout(layout)

        login = getattr(config, "login_name", None)
        if login:
            self.username.setText(login)

        pwd = getattr(config, "password", None)
        if pwd:
            self.password.setText(pwd)

        button.clicked.connect(self.click)
        super().show()

    def click(self) -> None:
        if self.username.text() == "":
            box = QMessageBox()
            box.setText("Please enter your username!")
            box.setIcon(QMessageBox.Icon.Warning)
            box.exec()
            return
        if self.password.text() == "":
            box = QMessageBox()
            box.setText("Please enter your password!")
            box.setIcon(QMessageBox.Icon.Warning)
            box.exec()
            return
        if self.comment.text() == "":
            box = QMessageBox()
            box.setText("Please enter a comment!")
            box.setIcon(QMessageBox.Icon.Warning)
            box.exec()
            return

        status_codes = self.parent.changeset.submit(
            self.comment.text(), self.username.text(), self.password.text()
        )

        self.parent.viewer.load_elements()
        self.hide()

        if status_codes == 200:
            box = QMessageBox()
            box.setWindowTitle("Success")
            box.setText("Successfully uploaded changes!")
            box.setIcon(QMessageBox.Icon.Information)
            box.exec()
        else:
            box = QMessageBox()
            box.setWindowTitle("ERROR")
            box.setText(
                f"Error:\n{self.status_codes.get(status_codes, 'Unknown error')}"
            )
            box.setIcon(QMessageBox.Icon.Critical)
            box.exec()
