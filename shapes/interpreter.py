from shapes.shape import Shape, ShapeEnum
from typing import List
from time import sleep
from shapes.utils import distance
from pathlib import Path


class InterpreterError(Exception):
    pass


class Interpreter:
    def __init__(self, shapes: List[Shape], verbose=False, time=0.3, home_dir=None):
        self.shapes = shapes
        self.stack = []
        self.current: None | Shape = None
        self.p_point = None
        self.p_k = None
        self.verbose = verbose
        self.time = time
        self.home_dir = home_dir
        self.steps=0
        self.current = self.get_start()
        self.is_running = False

    def get_start(self) -> Shape:
        starts = []
        for s in self.shapes:
            if s.get_shape_type() == ShapeEnum.START and s.outer is None:
                starts.append(s)
        if len(starts) < 1:
            raise InterpreterError("No start found")
        if len(starts) > 1:
            raise InterpreterError("You can't have more than one start")
        if len(starts[0].connecteds) < 1:
            raise InterpreterError("Start isn't connected to anything")
        if len(starts[0].connecteds) > 1:
            raise InterpreterError("Start can't be connected to more than one shape")
        if len(starts[0].connecteds[list(starts[0].connecteds.keys())[0]][1]) > 1:
            raise InterpreterError("Start can't be connected to more than one shape")
        return starts[0]

    def default_next(self):
        next_s = self.current.get_default_next(self.p_point)
        if next_s is None:
            print("|finished due to dead-end|")
            self.is_running=False
        self.current = next_s[0]
        self.p_point = next_s[1]
        self.p_k = next_s[2]

    def check_number(self, val):
        return isinstance(val, (float, int))

    def both_is_num(self, x, y):
        return self.check_number(x) and self.check_number(y)

    def neither_is_num(self, x, y):
        return not (self.check_number(x) or self.check_number(y))

    def push_back(self, x, y):
        self.stack.append(y)
        self.stack.append(x)

    def step(self):
        if self.verbose:
            print(f"|{self.steps}, current: {self.current.get_shape_type().name}|")
            print(f"|number of points of current: {len(self.current.points)}|")
        self.previous = self.current
        match self.current.get_shape_type():
            case ShapeEnum.START:
                # print(self.current.connecteds)
                self.p_point = self.current.connecteds[
                    list(self.current.connecteds.keys())[0]
                ][1][0][1]
                self.current = self.current.connecteds[
                    list(self.current.connecteds.keys())[0]
                ][1][0][0]

            case ShapeEnum.IN:
                inp = input("<<< ")
                try:
                    self.stack.append(int(inp))
                except ValueError:
                    try:
                        self.stack.append(float(inp))
                    except ValueError:
                        self.stack.append(inp)

                self.default_next()

            case ShapeEnum.OUT:
                if len(self.stack) > 0:
                    val = self.stack.pop()

                    print(val)
                else:
                    print()
                self.default_next()

            case ShapeEnum.OUT_NO_LF:
                if len(self.stack) > 0:
                    val = self.stack.pop()

                    print(val, end="")

                self.default_next()

            case ShapeEnum.READ:
                if len(self.stack) > 0:
                    path = str(self.stack.pop())

                    try:
                        if self.home_dir is None:
                            with open(path, "r") as f:
                                self.stack.append(f.read())
                        else:
                            with open(
                                Path(self.home_dir).joinpath(path), "r"
                            ) as f:
                                self.stack.append(f.read())
                    except FileNotFoundError:
                        self.stack.append(0)
                    except UnicodeDecodeError:
                        self.stack.append(1)
                    except Exception as e:
                        if self.verbose:
                            print(
                                f"|encountered unhadled exception while reading file: {e}|"
                            )

                        self.stack.append(2)

                self.default_next()

            case ShapeEnum.CONTAINER:
                if self.current.value is not None:
                    self.stack.append(self.current.value)
                    self.current.value = None
                else:
                    self.current.value = self.stack.pop()
                self.default_next()

            case ShapeEnum.STACK:
                if self.verbose:
                    print(f"|current local stack: {self.current.value}|")
                if len(self.stack) > 1:
                    top = self.stack.pop()
                    bottom = self.stack.pop()

                    if top == 1:
                        if self.current.value is None:
                            self.current.value = [bottom]
                        else:
                            self.current.value.append(bottom)
                    elif top == 2:
                        self.stack.append(bottom)
                        self.stack.append(len(self.current.value))
                    elif top == 0:
                        if len(self.current.value) > 0:
                            self.stack.append(bottom)

                            self.stack.append(self.current.value.pop())
                        else:
                            self.stack.append(bottom)
                    else:
                        self.stack.append(bottom)
                        self.stack.append(top)
                self.default_next()

            case ShapeEnum.JUNCTION:
                self.default_next()

            case ShapeEnum.NUMBER:
                if self.verbose:
                    print(f"|number shape value: {self.current.get_value()}|")
                self.stack.append(self.current.get_value())
                self.default_next()

            case ShapeEnum.POP:
                if len(self.stack) > 0:
                    self.stack.pop()
                self.default_next()

            case ShapeEnum.DUPE:
                if len(self.stack) > 0:
                    self.stack.append(self.stack[-1])
                self.default_next()

            case ShapeEnum.NUMBER_CHECK:
                if len(self.stack) > 0:
                    val = self.stack.pop()
                    self.stack.append(int(self.check_number(val)))
                self.default_next()

            case ShapeEnum.TO_STRING:
                if len(self.stack) > 0:
                    self.stack.append(str(self.stack.pop()))
                self.default_next()

            case ShapeEnum.TO_CHAR:
                if len(self.stack) > 0:
                    val = self.stack.pop()
                    if isinstance(val, (float, int)):
                        self.stack.append(chr(int(val)))
                    elif isinstance(val, str):
                        self.stack.extend([i for i in val[::-1]])
                self.default_next()

            case ShapeEnum.CHR_TO_NUM:
                if len(self.stack) > 0:
                    val = self.stack.pop()
                    if isinstance(val, str):
                        if len(val) == 1:
                            self.stack.append(ord(val))
                    else:
                        self.stack.append(val)

                self.default_next()

            case ShapeEnum.TO_NUMBER:
                if len(self.stack) > 0:
                    val = self.stack.pop()

                    try:
                        self.stack.append(int(val))
                    except ValueError:
                        try:
                            self.stack.append(float(val))
                        except ValueError:
                            self.stack.append(val)

                self.default_next()

            case ShapeEnum.OPER:
                if len(self.stack) > 1:
                    a = self.stack.pop()
                    b = self.stack.pop()

                    def _both_is_num():
                        return self.both_is_num(a, b)

                    def _neither_is_num():
                        return self.neither_is_num(a, b)

                    def _push_back():
                        self.stack.append(b)
                        self.stack.append(a)

                    l = len(self.current.get_holes())

                    if self.verbose:
                        print(f"|operation shape code: {l}|")

                    match l:
                        case 1:
                            if _both_is_num():
                                self.stack.append(a + b)
                            elif _neither_is_num():
                                self.stack.append(a + b)
                            else:
                                _push_back()
                        case 2:
                            if _both_is_num():
                                self.stack.append(a - b)
                            else:
                                _push_back()
                        case 3:
                            if _both_is_num():
                                self.stack.append(a * b)
                            else:
                                _push_back()
                        case 4:
                            if _both_is_num():
                                if b != 0:
                                    self.stack.append(a / b)
                                else:
                                    self.stack.append("NaN")
                            else:
                                _push_back()
                        case 5:
                            if _both_is_num():
                                self.stack.append(a % b)
                            else:
                                _push_back()
                        case 6:
                            self.stack.append(str(a) + str(b))
                        case _:
                            self.stack.append(a)
                            self.stack.append(b)
                self.default_next()

            case ShapeEnum.OR:
                if len(self.stack) > 1:
                    a = self.stack.pop()
                    b = self.stack.pop()
                    if self.both_is_num(a, b) or self.neither_is_num(a, b):
                        self.stack.append(a or b)
                    else:
                        self.push_back(a, b)

                self.default_next()

            case ShapeEnum.AND:
                if len(self.stack) > 1:
                    a = self.stack.pop()
                    b = self.stack.pop()
                    if self.both_is_num(a, b) or self.neither_is_num(a, b):
                        self.stack.append(a and b)
                    else:
                        self.push_back(a, b)

                self.default_next()

            case ShapeEnum.NOT:
                if len(self.stack) > 0:
                    val = self.stack.pop()
                    self.stack.append(int(not val))

                self.default_next()

            case ShapeEnum.EQUALS:
                if len(self.stack) > 1:
                    a = self.stack.pop()
                    b = self.stack.pop()
                    if self.both_is_num(a, b) or self.neither_is_num(a, b):
                        self.stack.append(int(a == b))
                    else:
                        self.push_back(a, b)

                self.default_next()

            case ShapeEnum.LARGER:
                if len(self.stack) > 1:
                    a = self.stack.pop()
                    b = self.stack.pop()
                    if self.both_is_num(a, b) or self.neither_is_num(a, b):
                        self.stack.append(int(a > b))
                    else:
                        self.push_back(a, b)

                self.default_next()

            case ShapeEnum.SMALLER:
                if len(self.stack) > 1:
                    a = self.stack.pop()
                    b = self.stack.pop()
                    if self.both_is_num(a, b) or self.neither_is_num(a, b):
                        self.stack.append(int(a < b))
                    else:
                        self.push_back(a, b)

                self.default_next()

            case ShapeEnum.LENGTH:
                self.stack.append(len(self.stack))
                self.default_next()

            case ShapeEnum.CONTROL:
                target = None
                if len(self.stack) > 0:
                    target = self.stack.pop()
                matches = []
                for c in self.current.get_all_connections():
                    if c[0].get_value() == target and c[2] != self.p_k:
                        matches.append(c)
                if len(matches) < 1:
                    for c in self.current.get_all_connections():
                        if c[0].get_value() == None and c[2] != self.p_k:
                            matches.append(c)

                min_dist = None
                nearest = None
                for m in matches:
                    dist = distance(self.current.center, m[1])
                    if min_dist is None or dist < min_dist:
                        min_dist = dist
                        nearest = m

                if nearest is None:
                    print()
                    print("|finished due to dead-end|")
                    self.is_running=False
                self.current = nearest[0]
                self.p_point = nearest[1]
            case ShapeEnum.END:
                print()
                print("--------------|finished|--------------")
                self.is_running=False

            case ShapeEnum.ANY:
                self.default_next()
        if self.verbose:
            print(f"|global stack: {self.stack}|")
            if self.is_running:
                print("--------------------------------------")
        self.steps += 1

    def run(self):
        self.is_running=True
        try:
            if self.time >= 0:
                while True:
                    self.step()
                    if not self.is_running:
                        break
                    
                    sleep(self.time)
            else:
                while True:
                    self.step()
                    if not self.is_running:
                        break
                    input("|press enter|")
                    print("\r", end='\r')
        except KeyboardInterrupt:
            print("|aborted!|")
