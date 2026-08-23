from uuid import uuid4
import zipfile
from pathlib import Path
import io

from .model import Template, TopLevelMap, FieldType, Review, Field
import json


from dataclasses import dataclass

@dataclass
class MochiAttachment:
    filename: str
    content: bytes

@dataclass
class MochiField:
    name: str
    field_type:  FieldType 
    id: str | None = None


@dataclass
class MochiCard:
    content: str # Normal field.
    name: str
    fields: dict[str, str]
    attachments: dict[str, MochiAttachment]
    reviews: list[Review]| None = None
    id: str | None = None

    
class MochiFile:
    DATA_JSON: str = "data.json"
    def __init__(self):
        self._root = TopLevelMap()
        self._files: dict[str, MochiAttachment] = {}

    def _safe_id(self):
        return str(uuid4()).replace("-", "")

    def add_attachment(self, filename: str, content: bytes):
        # Could do a content addressed storage here to get free dedup and avoiding duplicate files...
        attachment = MochiAttachment(filename=filename, content=content)
        self._files[filename] = attachment

    def add_template(self, name: str, content: str, fields=list[MochiField], template_id: str | None = None):
        if template_id is None:
            template_id = self._safe_id()
        if self._root.templates is None:
            self._root.templates = []
        fields_typed: list[Field] = []
        for f in fields:
            field_id = f.id
            if field_id is None:
                field_id = self._safe_id()
                
            fields_typed.append(Field(id=field_id, name=f.name, type=f.field_type))
        self._root.templates.append(Template(
            name=name,
            content=content,
            fields = fields_typed,
            id = template_id,
        ))

    def to_bytes(self) -> bytes: 
        buffer = io.BytesIO()
        data_json_contents = self._root.model_dump()
        json_str = json.dumps(data_json_contents, indent=1, ensure_ascii=False)
        
        
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("data.json", json_str)
            for v in self._files.values():
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
