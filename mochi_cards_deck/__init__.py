import zipfile
from pathlib import Path

from .model import TopLevelMap


class MochiFile:
    def __init__(self):
        self._root = TopLevelMap()

    @staticmethod
    def load_file(path: Path) -> "MochiFile":
        r = MochiFile()
        with zipfile.ZipFile(path, 'r') as deck_zip, deck_zip.open('data.json') as data_file:
                text = data_file.read().decode("utf-8")
        parsed = TopLevelMap.model_validate_json(text)
        r._root = parsed
        return r
