
from enum import Enum
from typing import Annotated, Any, TypeVar

from pydantic import BaseModel, PlainValidator, ConfigDict, PlainSerializer, Field as PydanticField 

"""
Roughly speaking, it hsould look like this:
{
    "~:version": 2,
    "~:templates": {
        "~#list": [
            {
                "~:id": "~:9buMPDAw",
                "~:pos": "A",
                ...
                "~:fields": {
                    "~:name": {
                        "~:id": "~:name",
                        "~:pos": "k0",
                        "~:name": "Front",
                        "~:type": "~:text"
                    },
                    ...
        ]
    },
    "~:schema/version": 35,
    "~:decks": [
        {
            "~:name": "deck name",
            "~:settings": {
                "~:settings.pages.deck/show-filters-section?": true
            },
            "~:id": "~:owyrHDjk",
            "~:cards": {
                "~#list": [
                    {
                        "~:tags": {
                            "~#set": []
                        },
                        "~:anki/note-id": 1785780888543,
                        "~:content": "",
                        "~:cloze/reviews": {},
                        "~:name": "thing",
                        "~:deck-id": "~:owyrHDjk",
                        "~:fields": {
                            "~:name": {
                                "~:id": "~:name",
                                "~:value": "thing"
                            },
                            
# https://mochi.cards/docs/import-and-export/mochi-format-reference/
# Keys: need ~: prefix
# Values: sometimes need '~#list: []` nesting.
# 
"""


def name_to_edn_tilde_thing(actual_name: str) -> str:
    # Also change underscores to hyphens.
    name_hyphen = actual_name
    if name_hyphen.endswith("_"):
        name_hyphen = name_hyphen[0:-1]
    name_hyphen = name_hyphen.replace("_", "-")
    return f"~:{name_hyphen}"

class MyBaseModel(BaseModel):
    """Custom base model that automatically strips None values on dump."""
    # This configuration makes aliases the automatic default everywhere
    model_config : ConfigDict = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=name_to_edn_tilde_thing,
    )
    

        
    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        # Force exclude_none to True unless explicitly overridden
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("mode", "json")
        return super().model_dump(**kwargs)

    def model_dump_json(self, **kwargs: Any) -> str:
        # Force exclude_none to True unless explicitly overridden
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("mode", "json")
        return super().model_dump_json(**kwargs)


"""

    #@field_validator("timestamp", mode="before")
    @classmethod
    def deserialize_list(cls, value: Any) -> Any:
        raise ValueError("Invalid timestamp format")
 
    def serialize_list(self, value: list[Any]) -> str: 
        return value.strftime("%Y-%m-%d %H:%M:%S")
"""

"""

        {
            "~:name": "deck name",
            "~:settings": {
                "~:settings.pages.deck/show-filters-section?": true
            },
            "~:id": "~:owyrHDjk",
            "~:cards": {
                "~#list": [
                    {
                        "~:tags": {
                            "~#set": []
                        },
                        "~:anki/note-id": 1785780888543,
                        "~:content": "",
"""


def edn_keyword_serialize(value: str) -> str:
    print(f"serializing {value}")
    return f"~:{value}"

def edn_keyword_deserialize(value: str) -> str:
    # SUPER GROSS... but this gets called twice for validation with nested structs.
    if value.startswith("~:"):
        return value[2:]
    else:
        return value
 
EDNKeyword = Annotated[str, PlainValidator(edn_keyword_deserialize), PlainSerializer(edn_keyword_serialize)]
 

def make_list_deserializer(our_type: Any) -> Any:  # pyright: ignore[reportAny, reportExplicitAny]
    def edn_list_deserialize(v: Any) -> Any:   # pyright: ignore[reportAny, reportExplicitAny]
        #{ "~#list": [a,b]} 
        return [our_type.model_validate(x) for x in v["~#list"]] # pyright: ignore[reportAny]
    return edn_list_deserialize

def edn_list_serialize(v: list[Any] ) -> Any:  # pyright: ignore[reportAny, reportExplicitAny]
    return {"~#list":v}
    


class FieldType(str, Enum):
    Text = ":text"
    Boolean = ":boolean"
    Speech = ":speech"
    Image = ":image"
    Translate = ":translate"

class Field(MyBaseModel):
    id: EDNKeyword
    name: str
    # optional
    type: FieldType | None = None 
    pos: EDNKeyword | None = None
    # options... some map of keyword to values, don't know how this looks yet.
    lang: str | None = None
    from_: str | None = None
    to: str | None = None
    boolean_default: bool | None = None
    
def test_field():
    t = Field(name="superfield", id="thing", from_="this", type=FieldType.Image)
    v = t.model_dump( )
    print(v)
    assert {'~:id': '~:thing', '~:name': 'superfield', '~:from': 'this', "~:type":":image"} == v  
    r = Field.model_validate(v)
    print(r) 
    assert r == t

class Review(MyBaseModel):
    pass
EDNListReview = Annotated[list[Review], PlainValidator(make_list_deserializer(Review)), PlainSerializer(edn_list_serialize)]


def field_value_dict_deserializer(complex_field_values_dict: Any) -> Any:  # pyright: ignore[reportAny, reportExplicitAny]
    if len(complex_field_values_dict) and not "~:value" in  list(complex_field_values_dict.values())[0]:
        return complex_field_values_dict
    s = {}
    for k, v in complex_field_values_dict.items():
        s[k[2:]] = v["~:value"]
    return s

def field_value_dict_serializer(simple_dict: dict[str, str] ) -> Any:  # pyright: ignore[reportAny, reportExplicitAny]
    res = {}
    for k, v in simple_dict.items():
        k_keyword = f"~:{k}"
        res[k_keyword] = {"~:id":k_keyword, "~:value": v}
    return res
    

EDNFieldValueDict = Annotated[dict[str, str], PlainValidator(field_value_dict_deserializer), PlainSerializer(field_value_dict_serializer)]


class Card(MyBaseModel):
    content: str # Normal field. 
    deck_id: EDNKeyword
    # Optional
    id: EDNKeyword | None = None
    name: EDNKeyword | None = None
    pos: EDNKeyword | None = None
    reviews: EDNListReview| None = None
    fields: EDNFieldValueDict | None = None
    

    

# 3. Define the parameterized Type Alias
# Note: The type variable T must be placed in brackets after the alias name
EDNListCard = Annotated[list[Card], PlainValidator(make_list_deserializer(Card)), PlainSerializer(edn_list_serialize)]

class Deck(MyBaseModel):
    name: str # Normal field. 
    # optional
    id: EDNKeyword | None = None
    cards: EDNListCard | None = None


def test_deck():
    t = Deck(name="our deck")
    deck_id = "abc"
    t.cards = [Card(content="hello", deck_id=deck_id, fields={"name": "hello"})]
    t.id = deck_id
    v = t.model_dump()
    print(v)
    assert {
        '~:name': 'our deck',
        '~:id': '~:abc',
        '~:cards': {
            '~#list': [
                {'~:content': 'hello', '~:deck-id': '~:abc', 
                                     '~:fields': {
                                         '~:name': {
                                             '~:id': '~:name',
                                             '~:value': 'hello',
                                         },
                                     },
}
            ]
        }} == v 
    # Validate deck
    
    r = Deck.model_validate(v)
    print(r)
    assert r.name == "our deck"
    assert r.id == "abc"
    assert r == t

class Template(MyBaseModel):
    pass


class TopLevelMap(MyBaseModel):
    version: int = 2
    decks: None | list[Deck] = None
    templates: None | list[Template] = None


def test_toplevel():
    t = TopLevelMap()
    v = t.model_dump()
    assert "~:version" in v
    assert v["~:version"] == 2 
    assert len(v.keys()) == 1
    v["~:version"] = 5
    r = TopLevelMap.model_validate(v)
    print(r)
    assert r.version == 5
