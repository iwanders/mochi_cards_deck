
# https://mochi.cards/docs/import-and-export/mochi-format-reference/
# 
#
from socket import timeout

from pydantic import BaseModel, Field, ConfigDict, field_serializer, field_validator, field_serializer
from typing import Any

def to_tilde_thing(actual_name: str) -> str:
    return f"~:{actual_name}"

class MyBaseModel(BaseModel):
    """Custom base model that automatically strips None values on dump."""
    # This configuration makes aliases the automatic default everywhere
    model_config : ConfigDict = ConfigDict(
        populate_by_name=True,      # Optional: Allows loading via 'user_name' OR 'username'
        serialize_by_alias=True,     # Eliminates needing 'by_alias=True' when exporting
        alias_generator=to_tilde_thing,
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


class Deck(MyBaseModel):
    pass


class TopLevelMap(MyBaseModel):
    version: int = 2 # Actually '~:version' as key.
    decks: None | list[Deck] = None # '~:decks' as key.


if __name__ == "__main__":
    t = TopLevelMap()
    v = t.model_dump_json(by_alias=True)
    print(v)
    r = TopLevelMap.model_validate_json(v)
    print(r)
