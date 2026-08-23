from uuid import uuid4
import zipfile
from pathlib import Path
import io

from .model import Card, EDNFieldValueDict, EDNListCard, Template, TopLevelMap, FieldType, Review, Field, Deck
import json


from dataclasses import dataclass

def _safe_id() -> str:
    return str(uuid4()).replace("-", "")
@dataclass
class MochiAttachment:
    filename: str
    content: bytes

@dataclass
class MochiField:
    name: str
    field_type:  FieldType 
    id: str | None = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = _safe_id()
            
    def __hash__(self):
        return hash(self.id)
        
    def __eq__(self, other):
        if not isinstance(other, MochiField):
            return NotImplemented
        return self.id == other.id



@dataclass
class MochiCard:
    content: str # Normal field.
    name: str
    fields: dict[str, str]
    attachments: dict[str, MochiAttachment]
    reviews: list[Review]| None = None
    id: str | None = None

    
@dataclass
class MochiTemplateRef:
    id: str

@dataclass
class MochiDeckRef:
    id: str

    
class MochiFile:
    DATA_JSON: str = "data.json"
    def __init__(self):
        self._root = TopLevelMap()
        self._files: dict[str, MochiAttachment] = {}


    def add_attachment(self, filename: str, content: bytes):
        # Could do a content addressed storage here to get free dedup and avoiding duplicate files...
        attachment = MochiAttachment(filename=filename, content=content)
        self._files[filename] = attachment

    def add_template(self, name: str, content: str, fields:list[MochiField] = [], template_id: str | None = None) -> MochiTemplateRef:
        if template_id is None:
            template_id =  _safe_id()
        if self._root.templates is None:
            self._root.templates = []
        fields_typed: list[Field] = []
        for f in fields: 
            fields_typed.append(Field(id=f.id, name=f.name, type=f.field_type))
        self._root.templates.append(Template(
            name=name,
            content=content,
            fields = fields_typed,
            id = template_id,
        ))
        return MochiTemplateRef(id=template_id)

    def add_deck(self, name: str, deck_id: str | None = None, cards: None | EDNListCard = None) -> MochiDeckRef:
        if self._root.decks is not None:
            for v in self._root.decks:
                if v.name == name:
                    raise KeyError(f"deck by name {name} already exists")
        else:
            self._root.decks = []
        if deck_id is None:
            deck_id =  _safe_id()
        self._root.decks.append(Deck(name=name, id=deck_id, cards=cards))
        return MochiDeckRef(id=deck_id)


    def _get_deck_by_ref(self, ref: MochiDeckRef) -> Deck:
        if self._root.decks is not None:
            for v in self._root.decks:
                if v.id == ref.id:
                    return v
        else:
            raise KeyError(f"deck {ref} does not exist")
        


    def add_card(self, deck: MochiDeckRef, fields: dict[MochiField, str], name: str | None = None, card_id: None | str  = None, content: str = "", template: MochiTemplateRef | None = None):
        if card_id is None:
            card_id =  _safe_id()
        deck_mod = self._get_deck_by_ref(deck)
        
        # CHeck if card id already exists, if so raise.
        if deck_mod.cards is not None:
            for v in deck_mod.cards:
                if v.id == card_id:
                    raise KeyError(f"card with id {card_id} already exists (in this deck)")
        else:
            deck_mod.cards = []

        # Munge the fields

        card_fields: EDNFieldValueDict = {}
        for field, value in fields.items():
            card_fields[field.id] = value

        template_id = None
        if template is not None:
            template_id = template.id

        deck_mod.cards.append(Card(fields=card_fields, id=card_id, name=name, content=content, deck_id = deck.id, template_id=template_id))
        
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
