# mochi_cards_deck

A Python module to make decks for [mochi.cards](https://mochi.cards/).

Looks like this:
```python

from pathlib import Path
from textwrap import dedent

from mochi_cards_deck import FieldType, MochiField, MochiFile

if __name__ == "__main__":
    f = MochiFile()

    # Create two fields, both are text fields.
    decimal_field = MochiField(name="decimal", field_type=FieldType.Text)
    hex_field =  MochiField(name="hexadecimal", field_type=FieldType.Text)

    # Create the template for one direction, do NOT forget dedent, it is important to make valid markdown.
    dec_to_hex_template = f.add_template(name="dec to hex", content=dedent("""
    << decimal >>
    ---
    << hexadecimal >>
    """), fields=[decimal_field, hex_field])
    
    
    # Create the template for the other direction
    hex_to_dec_template = f.add_template(name="dec to hex", content=dedent("""
    << hexadecimal >>
    ---
    << decimal >>
    """), fields=[decimal_field, hex_field])

    # Create a deck.
    deck = f.add_deck("lower 16")

    # Add cards to the deck using fields and the template.
    f.add_card(deck, fields={hex_field: "0x01", decimal_field:"1"}, template=dec_to_hex_template)
    f.add_card(deck, fields={hex_field: "0x01", decimal_field:"1"}, template=hex_to_dec_template)
    f.add_card(deck, fields={hex_field: "0x0F", decimal_field:"15"}, template=dec_to_hex_template)
    f.add_card(deck, fields={hex_field: "0x0F", decimal_field:"15"}, template=hex_to_dec_template)

    # Save the deck.
    f.write_file(Path("/tmp/test_deck.mochi"))

```

Taken from one of the examples in [./example](./example), attachments are also supported, see the `multimodal_deck.py` example.

License is [BSD-3-Clause](./LICENSE).
