#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path

import mochi_cards_deck

from . import MochiFile
from textwrap import dedent


def run_load_test(args):
    f = MochiFile.load_file(args.file)
    f.write_file(Path("/tmp/foo.mochi"))
    pass

def run_create_deck(args):
    f = MochiFile()
    decimal_field = mochi_cards_deck.MochiField(name="decimal", field_type=mochi_cards_deck.FieldType.Text)
    hex_field =  mochi_cards_deck.MochiField(name="hexadecimal", field_type=mochi_cards_deck.FieldType.Text)
    print(hex_field)
    
    dec_to_hex_template = f.add_template(name="dec to hex", content=dedent("""
    << decimal >>
    ---
    << hexadecimal >>
    """), fields=[decimal_field, hex_field])


    deck = f.add_deck("lower 16")
    f.add_card(deck, fields={hex_field: "0x01", decimal_field:"1"}, template=dec_to_hex_template)

    
    f.write_file(args.output)
    pass

if __name__ == "__main__":
    # Create a parser with some subcommands
    parser = argparse.ArgumentParser(description="mochi_thing")
    _ = parser.add_argument(
        "-v",
        "--verbose",
        help="Enable verbose output",
        action="store_true",
        default=False,
    ) 
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="sub-command help")
    
    
    parser_run_load_test = subparsers.add_parser("load", help="Test loading a deck.") 
    parser_run_load_test.add_argument("file", type=Path, help="Path to the file to load.", )
    parser_run_load_test.set_defaults(func=run_load_test)
     
    
    parser_run_create_deck = subparsers.add_parser("create", help="Test creating a deck")
    parser_run_create_deck.add_argument("output", type=Path, help="Path to the output path.")
    parser_run_create_deck.set_defaults(func=run_create_deck)
     
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Execute the selected command's function
    if args.command:
        args.func(args)
    else:
        parser.print_help()
