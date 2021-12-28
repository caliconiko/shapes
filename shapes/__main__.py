import argparse
from typing import List
from shapes.interpreter import Interpreter
from shapes.parser import Parser
from shapes.shape import Shape
from time import time
import cProfile


def print_shapes_found(shapes:List[Shape]):
    print(
        f"|shapes found: {[f'{s.get_shape_type().name}({len(s.points)} {s.circular}) : {[(len(h.points), h.circular)  for h in s.get_holes()]}' for s in shapes if s.outer is None]}|"
    )
    print("|shape type(number of points  circularness) : [(number of points  circularness) for each hole the shape has]|")


def main():
    # start parsers
    arg_parser = argparse.ArgumentParser(
        description="Shapes Interpreter for Python 3.10"
    )

    subparsers = arg_parser.add_subparsers(dest="command")
    interpret_parser = subparsers.add_parser(
        "interpret", help="interpret a shapes program"
    )
    profile_parser = subparsers.add_parser(
        "profile", help="profile the parsing of a shpaes program with cprofile"
    )
    parse_parser = subparsers.add_parser(
        "parse", help="parse a shapes program in debug mode without interpreting it"
    )

    # interpret command
    interpret_parser.add_argument(
        "path",
        type=str,
        help="path of file to interpret. if the given path doesn't have a file format, it defaults to .png",
    )
    interpret_parser.add_argument(
        "-t", "--time", type=float, help="seconds to wait for every step"
    )
    interpret_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print extra stuff (good for debugging)",
    )
    interpret_parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="shows what the interpreter sees (also good for debugging)",
    )

    # profile command
    profile_parser.add_argument(
        "path",
        type=str,
        help="path of file to profile. if the given path doesn't have a file format, it defaults to .png",
    )
    profile_parser.add_argument(
        "-d", "--debug", action="store_true", help="shows what the interpreter sees"
    )

    # parse command
    parse_parser.add_argument(
        "path",
        type=str,
        help="path of file to parse. if the given path doesn't have a file format, it defaults to .png",
    )

    args = arg_parser.parse_args()

    if not args.command:
        arg_parser.error("No commands whatsoever given")

    path = args.path
    if args.path[-4:] != ".png":
        path = args.path + ".png"

    match args.command:
        case "profile":
            print("|profiling...|")
            cProfile.runctx(
                "Parser(path, args.debug).parse_shapes()",
                globals(),
                locals(),
                sort="tottime",
            )
            print("|profiled!|")

        case "interpret":
            print(f"|parsing {path}...|")
            parser = Parser(path, args.debug)
            parse_start = time()
            shapes = parser.parse_shapes()
            parse_end = time()
            print(f"|parsed! {round(parse_end-parse_start, 3)} seconds elapsed|")
            if args.debug:
                print_shapes_found(shapes)
            print("--------------------------------------")
            t = args.time
            if args.time is None:
                t = 0

            interpreter = Interpreter(shapes, args.verbose, t, home_dir=parser.home_dir)
            interpreter.run()

        case "parse":
            print(f"|parsing {path}...|")
            parser = Parser(path, True)
            parse_start = time()
            shapes = parser.parse_shapes()
            parse_end = time()
            print(f"|parsed! {round(parse_end-parse_start, 3)} seconds elapsed|")
            print_shapes_found(shapes)


if __name__ == "__main__":
    main()
