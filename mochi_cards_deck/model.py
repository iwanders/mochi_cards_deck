
from typing import Annotated, Any, TypeVar

from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer

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
    name_hyphen = actual_name.replace("_", "-")
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
        return super().model_dump(**kwargs)

    def model_dump_json(self, **kwargs: Any) -> str:
        # Force exclude_none to True unless explicitly overridden
        kwargs.setdefault("exclude_none", True)
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
    return f"~:{value}"

def edn_keyword_deserialize(value: str) -> str:
    return value[2:]
 
EDNKeyword = Annotated[str, BeforeValidator(edn_keyword_deserialize), PlainSerializer(edn_keyword_serialize)]

T = TypeVar('T')




def edn_list_deserialize(v: Any) -> Any: 
    #{ "~#list": [a,b]}
    return v["~#list"]

def edn_list_serialize(v: list[Any]) -> Any:
    #{ "~#list": [a,b]}
    return {"~#list":v}

# 3. Define the parameterized Type Alias
# Note: The type variable T must be placed in brackets after the alias name
EDNList = Annotated[list[T], BeforeValidator(edn_list_deserialize), PlainSerializer(edn_list_serialize)]


class Card(MyBaseModel):
    content: str # Normal field. 
    deck_id: EDNKeyword
    # Optional
    id: EDNKeyword | None = None
    name: EDNKeyword | None = None
    pos: EDNKeyword | None = None
    

class Deck(MyBaseModel):
    name: str # Normal field. 
    # optional
    id: EDNKeyword | None = None
    cards: EDNList[Card]| None = None


def test_deck():
    t = Deck(name="our deck")
    deck_id = "abc"
    t.cards = [Card(content="hello", deck_id=deck_id)]
    t.id = deck_id
    v = t.model_dump(by_alias=True)
    print(v)
    #assert 1 == 2
    assert "~:name" in v
    assert "~:id" in v
    assert v["~:name"] == "our deck"
    assert v["~:id"] == "~:abc"
    # Validate deck
    
    r = Deck.model_validate(v)
    print(r)
    assert r.name == "our deck"
    assert r.id == "abc"

class Template(MyBaseModel):
    pass


class TopLevelMap(MyBaseModel):
    version: int = 2
    decks: None | list[Deck] = None
    templates: None | list[Template] = None


def test_toplevel():
    t = TopLevelMap()
    v = t.model_dump(by_alias=True)
    assert "~:version" in v
    assert v["~:version"] == 2 
    assert len(v.keys()) == 1
    v["~:version"] = 5
    r = TopLevelMap.model_validate(v)
    print(r)
    assert r.version == 5
