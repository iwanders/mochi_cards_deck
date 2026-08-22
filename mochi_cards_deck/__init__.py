import zipfile
from pathlib import Path
import io

from .model import TopLevelMap
import json


from dataclasses import dataclass

@dataclass
class MochiAttachment:
    filename: str
    content: bytes

class MochiFile:
    DATA_JSON: str = "data.json"
    def __init__(self):
        self._root = TopLevelMap()
        self._files: dict[str, MochiAttachment] = {}

    def add_attachment(self, filename: str, content: bytes):
        # Could do a content addressed storage here to get free dedup and avoiding duplicate files...
        attachment = MochiAttachment(filename=filename, content=content)
        self._files[filename] = attachment

    def to_bytes(self) -> bytes: 
        buffer = io.BytesIO()
        data_json_contents = self._root.model_dump()
        json_str = json.dumps(data_json_contents, indent=1, ensure_ascii=False)
        
        
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("data.json", json_str)
            for k, v in self._files.items():
                zf.writestr(v.filename, v.content)
        return buffer.getvalue()

    def write_file(self, path: Path):
        # Convert first, then write, such that if conversion fails we don't end up with a 0 sized file.
        content = self.to_bytes()
        with path.open("wb") as f:
            f.write(content)
         
        

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
