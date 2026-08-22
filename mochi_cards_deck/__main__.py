#!/usr/bin/env python3

from . import MochiFile
import argparse
import logging
from pathlib import Path

def run_load_test(args):
    f = MochiFile.load_file(args.file)
    
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
    parser_run_load_test.add_argument("--allow-download", dest="local_files_only", default=True, action="store_false")

    parser_run_load_test.add_argument("file",
         type=Path,
         help="Paths to operate on, retrieve https://huggingface.co/datasets/bezzam/audio_samples/resolve/main/librispeech_mr_quilter.wav as an example",
    )
     
    parser_run_load_test.set_defaults(func=run_load_test)
     
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
