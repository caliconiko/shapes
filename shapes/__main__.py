import argparse
from shapes.interpreter import Interpreter
from shapes.parser import Parser
from time import time
import cProfile

def main():
    arg_parser = argparse.ArgumentParser(description="Shapes Interpreter for Python 3.10")
    
    subparsers = arg_parser.add_subparsers(dest="command")
    interpret_parser = subparsers.add_parser("interpret", help="interpret a shapes program")
    profile_parser = subparsers.add_parser("profile", help="profile the parsing of a shpaes program with cprofile")

    interpret_parser.add_argument("path", type=str, help="path of file to interpret. if the given path doesn't have a file format, it defaults to .png")
    interpret_parser.add_argument("-t", '--time', type=float, help="seconds to wait for every step")
    interpret_parser.add_argument("-v", '--verbose', action='store_true',help="print extra stuff (good for debugging)")
    interpret_parser.add_argument("-d", '--debug', action='store_true',help="shows what the interpreter sees (also good for debugging)")
    
    profile_parser.add_argument("path", type=str, help="path of file to profile. if the given path doesn't have a file format, it defaults to .png")
    profile_parser.add_argument("-d", '--debug', action='store_true',help="shows what the interpreter sees")
    
    args = arg_parser.parse_args()

    path = args.path
    if args.path[-4:] != ".png":
        path = args.path+".png"
    
    match args.command:
        case "profile":
            print("|profiling...|")
            cProfile.runctx("Parser(path, args.debug).parse_shapes()", globals(), locals(), sort="tottime")
            print("|profiled!|")

        case "interpret":
            print(f"|parsing {path}...|")
            parser = Parser(path, args.debug)
            parse_start = time()
            shapes = parser.parse_shapes()
            parse_end = time()
            print(f"|parsed! {round(parse_end-parse_start, 3)} seconds elapsed|")
            if args.debug:
                print(f"|shapes found: {[f'{s.get_shape_type().name} : {[len(h.points) for h in s.get_holes()]}' for s in shapes if s.outer is None]}|")
            print("--------------------------------------")
            t=args.time
            if args.time is None:
                t=0

            interpreter = Interpreter(shapes, args.verbose, t)
            interpreter.run()


if __name__ == "__main__":
    main()
