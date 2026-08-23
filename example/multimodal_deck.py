#!/usr/bin/env python3
 
from pathlib import Path
from textwrap import dedent

from mochi_cards_deck import FieldType, MochiField, MochiFile


def get_audio_content() -> bytes:
    import os
    use_mp3_file = "../440hz_1s.mp3"
    if not "AUDIO_MP3_FILE" in os.environ:
        print(f"Could not find 'AUDIO_MP3_FILE' in environment, falling back to {use_mp3_file}")
    else:
        use_mp3_file = os.environ["AUDIO_MP3_FILE"]
    with open(use_mp3_file, "rb") as f:
        return f.read()
        

if __name__ == "__main__":
    f = MochiFile()

    # Create two fields, both are text fields.
    audio_fragment = MochiField(name="audio_fragment", field_type=FieldType.Text)
    text_field =  MochiField(name="accompanying_text", field_type=FieldType.Text)

    # lets do a canvas as well.
    draw_field =  MochiField(name="draw_canvas", field_type=FieldType.Draw)
    
    audio_to_text_template = f.add_template(name="audio to text", content=dedent("""
    << audio_fragment >>
    << draw_canvas >>
    ---
    << accompanying_text >>
    """), fields=[audio_fragment, text_field, draw_field])
    
    
    # Create a deck.
    deck = f.add_deck("audio_test")

    f.add_attachment("my_audio_file.mp3", get_audio_content())

    # Add cards to the deck using fields and the template.
    f.add_card(deck, fields={audio_fragment: "![](my_audio_file.mp3)", text_field:"some dummy text", draw_field:""}, template=audio_to_text_template)
    
    # Save the deck.
    f.write_file(Path("/tmp/test_multimodal_deck.mochi"))
