import argparse
from shapes39.shapes.interpreter import Interpreter
from shapes39.shapes.parser import Parser


def main():
    arg_parser = argparse.ArgumentParser(description="Shapes Interpreter")
    arg_parser.add_argument("path", type=str, help="path of file to interpret")
    arg_parser.add_argument("-t", '--time', type=float, help="seconds to wait for every step")
    arg_parser.add_argument("-v", '--verbose', action='store_true',help="print extra stuff (good for debugging)")
    arg_parser.add_argument("-d", '--debug', action='store_true',help="shows what the program sees (also good for debugging)")

    args = arg_parser.parse_args()
    
    print("|parsing...|")
    parser = Parser(args.path, args.debug)
    shapes = parser.parse_shapes()
    print("|parsed!|")
    print("--------------------------------------")
    t=args.time
    if args.time is None:
        t=0

    interpreter = Interpreter(shapes, args.verbose, t)
    interpreter.run()


if __name__ == "__main__":
    main()
