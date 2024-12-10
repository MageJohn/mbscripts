import argparse
import sys

from .hugo_html import dump
from .import_midnight_burger import import_transcript

parser = argparse.ArgumentParser()
parser.add_argument("infile")
parser.add_argument("-o", "--outfile", default=sys.stdout.buffer)


def main(infile, outfile):
    doc = import_transcript(infile)
    dump(doc, outfile)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.infile, args.outfile)
