import argparse


def main():
    arg_parser = argparse.ArgumentParser(
        description="Rewrite of shapes interpreter for Python 3.9+"
    )
    subparsers = arg_parser.add_subparsers(dest="command")

    parse_parser = subparsers.add_parser(
        "parse", help="parse a shapes program"
    )
    parse_parser.add_argument(
        "path",
        type=str,
        help="path of file to parse",
    )

    args = arg_parser.parse_args()
    path = args.path

    print(path)