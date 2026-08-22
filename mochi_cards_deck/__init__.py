import zipfile
from pathlib import Path

from .model import TopLevelMap


class MochiAttachment:
    def __init__(self, filename: str, content: bytes):
        self._filename = filename
        self._content = content

class MochiFile:
    DATA_JSON: str = "data.json"
    def __init__(self):
        self._root = TopLevelMap()
        self._files: dict[str, MochiAttachment] = {}

    def add_attachment(self, filename: str, content: bytes):
        # Could do a content addressed storage here to get free dedup and avoiding duplicate files...
        attachment = MochiAttachment(filename=filename, content=content)
        self._files[filename] = attachment

    @staticmethod
    def load_file(path: Path) -> "MochiFile":
        r = MochiFile()
        with zipfile.ZipFile(path, 'r') as deck_zip:
            with deck_zip.open(MochiFile.DATA_JSON) as data_file:
                text = data_file.read().decode("utf-8")
            parsed = TopLevelMap.model_validate_json(text)
            r._root = parsed
            # Only if we could parse this, do we continue with reading the attachments.
            for file_name in  deck_zip.namelist():
                if file_name == MochiFile.DATA_JSON:
                    continue 
                file_bytes = deck_zip.read(file_name)
                r.add_attachment(file_name, file_bytes)
                
        return r
