import base64
from enum import Enum
import mimetypes
import os


class EmailAttachmentType(Enum):
    PDF = "application/pdf"
    PNG = "image/png"
    JPG = "image/jpeg"
    BIN = "application/octet-stream"

    @classmethod
    def from_mime(cls, mime: str):
        for item in cls:
            if item.value == mime:
                return item
        return cls.BIN


class EmailAttachment:
    def __init__(self, filepath: str, type: EmailAttachmentType = None, filename: str = None):
        """
        Docstring for __init__

        :param filepath: filepath to the attachment
        :type filepath: str
        :param type: attachment type, if `None` - determine automatically
        :type type: EmailAttachmentType
        :param filename: filename (with/without extension) of the attachment. If `None` - use from `filepath`
        :type filename: str
        """

        self.filepath = filepath

        # auto determine type if needed
        if type:
            self.type = type
        else:
            mime, _ = mimetypes.guess_type(filepath)
            self.type = EmailAttachmentType.from_mime(mime) if mime else EmailAttachmentType.BIN

        # auto determine filename if needed (and handle if it is given without extension)
        if filename:
            _, name_ext = os.path.splitext(filename)

            # if given without extension
            if not name_ext:
                _, ext = os.path.splitext(filepath)
                filename = f"{filename}{ext}"
            self.filename = filename
        else:
            self.filename = os.path.basename(filepath)

    def get_base64_content(self):
        with open(self.filepath, "rb") as file:
            binary_file_data = file.read()
            base64_data = base64.b64encode(binary_file_data).decode("UTF-8")
            return str(base64_data)
