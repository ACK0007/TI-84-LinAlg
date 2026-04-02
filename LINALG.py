import math

EPSILON = 1e-9
FUNCTION_NAMES = {"cos", "sin", "acos", "asin", "atan", "n", "nr"}
COMPONENT_SUFFIXES = ("x", "y", "z")


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def to_float(value):
    return float(value)


def almost_zero(value):
    return abs(to_float(value)) <= EPSILON


def format_number(value):
    number = to_float(value)
    if almost_zero(number):
        return "0"
    rounded = round(number)
    if abs(number - rounded) <= EPSILON:
        return str(int(rounded))
    text = f"{number:.10f}".rstrip("0").rstrip(".")
    if text == "-0":
        return "0"
    return text


def zero_vector():
    return vector(0.0, 0.0, 0.0)


def component_name(name, index):
    return f"{name}.{COMPONENT_SUFFIXES[index]}"


class vector:
    def __init__(self, x, y, z):
        self.x = to_float(x)
        self.y = to_float(y)
        self.z = to_float(z)

    def components(self):
        return (self.x, self.y, self.z)

    @classmethod
    def norm(cls, v):
        return math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)

    @classmethod
    def normalized(cls, v):
        length = cls.norm(v)
        if almost_zero(length):
            raise ZeroDivisionError("Cannot normalize the zero vector.")
        return vector(v.x / length, v.y / length, v.z / length)

    @classmethod
    def cross_product(cls, v1, v2):
        return vector(
            v1.y * v2.z - v2.y * v1.z,
            v1.z * v2.x - v2.z * v1.x,
            v1.x * v2.y - v2.x * v1.y,
        )

    @classmethod
    def theta(cls, v1, v2):
        return math.acos((v1 * v2) / (cls.norm(v1) * cls.norm(v2))) * 180 / math.pi

    def __add__(self, other):
        if isinstance(other, vector):
            return vector(self.x + other.x, self.y + other.y, self.z + other.z)
        raise TypeError("Unsupported operand type(s) for +")

    def __sub__(self, other):
        if isinstance(other, vector):
            return vector(self.x - other.x, self.y - other.y, self.z - other.z)
        raise TypeError("Unsupported operand type(s) for -")

    def __mul__(self, other):
        if isinstance(other, vector):
            return self.x * other.x + self.y * other.y + self.z * other.z
        if is_number(other):
            scalar = to_float(other)
            return vector(scalar * self.x, scalar * self.y, scalar * self.z)
        raise TypeError("Unsupported operand type(s) for *")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if not is_number(other):
            raise TypeError("Unsupported operand type(s) for /")
        scalar = to_float(other)
        if almost_zero(scalar):
            raise ZeroDivisionError("Division by zero.")
        return self * (1 / scalar)

    def __neg__(self):
        return vector(-self.x, -self.y, -self.z)

    def __repr__(self):
        return f"{{{format_number(self.x)},{format_number(self.y)},{format_number(self.z)}}}"


class Expr:
    def __init__(self, kind, value_type, value=None, name=None, op=None, left=None, right=None, func=None, arg=None):
        self.kind = kind
        self.value_type = value_type
        self.value = value
        self.name = name
        self.op = op
        self.left = left
        self.right = right
        self.func = func
        self.arg = arg

    @classmethod
    def symbol(cls, name, value_type):
        return cls("symbol", value_type, name=name)

    @classmethod
    def binary(cls, op, left, right, value_type):
        return cls("binary", value_type, op=op, left=left, right=right)

    @classmethod
    def function(cls, func, arg, value_type):
        return cls("function", value_type, func=func, arg=arg)

    def __repr__(self):
        return render_value(self)


class ASTNode:
    def __init__(self, kind, value=None, name=None, op=None, left=None, right=None, func=None, arg=None, components=None):
        self.kind = kind
        self.value = value
        self.name = name
        self.op = op
        self.left = left
        self.right = right
        self.func = func
        self.arg = arg
        self.components = components


def render_value(value, parent_precedence=0, is_right_child=False):
    if is_number(value):
        return format_number(value)
    if isinstance(value, vector):
        return repr(value)
    if not isinstance(value, Expr):
        return str(value)
    if value.kind == "symbol":
        return value.name
    if value.kind == "function":
        return f"{value.func}({render_value(value.arg)})"
    if value.kind == "binary":
        precedence = 1 if value.op in {"+", "-"} else 2
        left_text = render_value(value.left, precedence, False)
        right_text = render_value(value.right, precedence, True)
        text = f"{left_text} {value.op} {right_text}"
        needs_parens = precedence < parent_precedence
        if is_right_child and precedence == parent_precedence and value.op in {"-", "/"}:
            needs_parens = True
        if needs_parens:
            return f"({text})"
        return text
    return str(value)


def collect_ast_identifiers(node):
    if node.kind == "identifier":
        return {node.name}
    if node.kind == "binary":
        return collect_ast_identifiers(node.left) | collect_ast_identifiers(node.right)
    if node.kind == "function":
        return collect_ast_identifiers(node.arg)
    if node.kind == "vector":
        names = set()
        for component in node.components:
            names |= collect_ast_identifiers(component)
        return names
    return set()


class Parser:
    def __init__(self, source):
        self.source = source
        self.tokens = self.tokenize(source)
        self.index = 0

    def tokenize(self, source):
        tokens = []
        i = 0
        while i < len(source):
            char = source[i]
            if char.isspace():
                i += 1
                continue
            if char.isdigit() or (char == "." and i + 1 < len(source) and source[i + 1].isdigit()):
                start = i
                dot_seen = char == "."
                i += 1
                while i < len(source):
                    current = source[i]
                    if current.isdigit():
                        i += 1
                        continue
                    if current == "." and not dot_seen:
                        dot_seen = True
                        i += 1
                        continue
                    break
                tokens.append(("NUMBER", source[start:i]))
                continue
            if char == "X" and (i + 1 == len(source) or not (source[i + 1].isalnum() or source[i + 1] == "_")):
                tokens.append(("OP", char))
                i += 1
                continue
            if char.isalpha() or char == "_":
                start = i
                i += 1
                while i < len(source) and (source[i].isalnum() or source[i] == "_"):
                    i += 1
                tokens.append(("IDENT", source[start:i]))
                continue
            if char in "+-*/=X(),{}":
                kind = "OP" if char in "+-*/=X" else "PUNCT"
                tokens.append((kind, char))
                i += 1
                continue
            raise ValueError(f"Unexpected character: {char}")
        tokens.append(("EOF", ""))
        return tokens

    def current(self):
        return self.tokens[self.index]

    def consume(self):
        token = self.current()
        self.index += 1
        return token

    def peek(self, value):
        token_type, token_value = self.current()
        return token_value == value and token_type in {"OP", "PUNCT"}

    def expect(self, value):
        token_type, token_value = self.current()
        if token_value != value:
            raise ValueError(f"Expected '{value}' but found '{token_value}'.")
        self.index += 1

    def parse_equation(self):
        lhs = self.parse_expression()
        if not self.peek("="):
            raise ValueError("Equations must contain '='.")
        self.expect("=")
        rhs = self.parse_expression()
        if self.current()[0] != "EOF":
            raise ValueError(f"Unexpected token: {self.current()[1]}")
        return lhs, rhs

    def parse_expression(self):
        node = self.parse_term()
        while self.peek("+") or self.peek("-"):
            op = self.consume()[1]
            node = ASTNode("binary", op=op, left=node, right=self.parse_term())
        return node

    def parse_term(self):
        node = self.parse_unary()
        while self.peek("*") or self.peek("/") or self.peek("X"):
            op = self.consume()[1]
            node = ASTNode("binary", op=op, left=node, right=self.parse_unary())
        return node

    def parse_unary(self):
        if self.peek("+"):
            self.consume()
            return self.parse_unary()
        if self.peek("-"):
            self.consume()
            return ASTNode(
                "binary",
                op="*",
                left=ASTNode("number", value=-1.0),
                right=self.parse_unary(),
            )
        return self.parse_primary()

    def parse_primary(self):
        token_type, token_value = self.current()
        if token_type == "NUMBER":
            self.consume()
            return ASTNode("number", value=to_float(token_value))
        if token_type == "IDENT":
            self.consume()
            if self.peek("("):
                if token_value not in FUNCTION_NAMES:
                    raise ValueError(f"Unknown function: {token_value}")
                self.expect("(")
                argument = self.parse_expression()
                self.expect(")")
                return ASTNode("function", func=token_value, arg=argument)
            return ASTNode("identifier", name=token_value)
        if self.peek("("):
            self.expect("(")
            node = self.parse_expression()
            self.expect(")")
            return node
        if self.peek("{"):
            return self.parse_vector_literal()
        raise ValueError(f"Unexpected token: {token_value}")

    def parse_vector_literal(self):
        self.expect("{")
        components = [self.parse_expression()]
        self.expect(",")
        components.append(self.parse_expression())
        self.expect(",")
        components.append(self.parse_expression())
        self.expect("}")
        return ASTNode("vector", components=components)


class equation:
    def __init__(self, eqn):
        self.eqn = eqn.strip()
        parser = Parser(self.eqn)
        self.lhs, self.rhs = parser.parse_equation()
        self.identifiers = sorted(collect_ast_identifiers(self.lhs) | collect_ast_identifiers(self.rhs))

    def assignment_target(self):
        if self.lhs.kind == "identifier":
            return self.lhs.name
        return None

    def __repr__(self):
        return self.eqn


class LinearizationError(Exception):
    pass


class LinearScalar:
    def __init__(self, constant=0.0, coeffs=None):
        self.constant = to_float(constant)
        self.coeffs = {}
        if coeffs:
            for name, value in coeffs.items():
                number = to_float(value)
                if not almost_zero(number):
                    self.coeffs[name] = number

    def copy(self):
        return LinearScalar(self.constant, self.coeffs)

    def cleanup(self):
        for name in list(self.coeffs.keys()):
            if almost_zero(self.coeffs[name]):
                del self.coeffs[name]
        if almost_zero(self.constant):
            self.constant = 0.0
        return self

    def add(self, other):
        result = LinearScalar(self.constant + other.constant, self.coeffs)
        for name, value in other.coeffs.items():
            result.coeffs[name] = result.coeffs.get(name, 0.0) + value
        return result.cleanup()

    def sub(self, other):
        return self.add(other.scale(-1.0))

    def scale(self, factor):
        number = to_float(factor)
        result = LinearScalar(self.constant * number)
        for name, value in self.coeffs.items():
            result.coeffs[name] = value * number
        return result.cleanup()

    def is_constant(self):
        return len(self.coeffs) == 0


class LinearVector:
    def __init__(self, components):
        self.components = components

    @classmethod
    def constant(cls, value):
        return cls([LinearScalar(value.x), LinearScalar(value.y), LinearScalar(value.z)])

    @classmethod
    def symbol(cls, name):
        return cls(
            [
                LinearScalar(0.0, {component_name(name, 0): 1.0}),
                LinearScalar(0.0, {component_name(name, 1): 1.0}),
                LinearScalar(0.0, {component_name(name, 2): 1.0}),
            ]
        )

    def add(self, other):
        return LinearVector([self.components[i].add(other.components[i]) for i in range(3)])

    def sub(self, other):
        return LinearVector([self.components[i].sub(other.components[i]) for i in range(3)])

    def scale_by_constant(self, factor):
        return LinearVector([component.scale(factor) for component in self.components])

    def is_constant(self):
        return all(component.is_constant() for component in self.components)

    def as_vector(self):
        if not self.is_constant():
            raise LinearizationError("Expected a constant vector.")
        return vector(
            self.components[0].constant,
            self.components[1].constant,
            self.components[2].constant,
        )


class environment:
    def __init__(self):
        self.equations = []
        self.vars = {}
        self.symbols = {}

    def declare_symbol(self, name, kind="scalar"):
        if not self._is_valid_identifier(name):
            raise ValueError(f"Invalid symbol name: {name}")
        if kind not in {"scalar", "vector"}:
            raise ValueError("Symbol kind must be 'scalar' or 'vector'.")
        existing = self.symbols.get(name)
        if existing is not None and existing != kind:
            raise ValueError(f"Symbol '{name}' is already declared as {existing}.")
        self.symbols[name] = kind
        self.vars[name] = Expr.symbol(name, kind)

    def process_line(self, line):
        text = line.strip()
        if not text:
            return None
        if text.startswith("sym "):
            parts = text.split()
            if len(parts) == 2:
                self.declare_symbol(parts[1], "scalar")
                return None
            if len(parts) == 3 and parts[2] == "vec":
                self.declare_symbol(parts[1], "vector")
                return None
            raise ValueError("Symbol declarations must be 'sym <name>' or 'sym <name> vec'.")
        self.add_equation(equation(text))
        return None

    def add_equation(self, eqn):
        target = eqn.assignment_target()
        if target is None:
            raise ValueError("Assignments must have a single identifier on the left-hand side.")
        rhs = self.evaluate_expression(eqn.rhs)
        if target in self.symbols:
            expected_type = self.symbols[target]
            actual_type = self.value_type(rhs)
            if actual_type != expected_type:
                raise TypeError(f"Symbol '{target}' expects a {expected_type} value, not {actual_type}.")
        self.vars[target] = rhs
        self.equations.append(eqn)

    def evaluate_expression(self, expr):
        return self._evaluate_ast(expr)

    def value_type(self, value):
        if is_number(value):
            return "scalar"
        if isinstance(value, vector):
            return "vector"
        if isinstance(value, Expr):
            return value.value_type
        raise TypeError(f"Unsupported value type: {type(value).__name__}")

    def apply_binary(self, op, left, right):
        left_type = self.value_type(left)
        right_type = self.value_type(right)

        if op in {"+", "-"}:
            if left_type != right_type:
                raise TypeError(f"Unsupported operand types for {op}: {left_type} and {right_type}")
            if op == "+":
                if is_number(left) and is_number(right):
                    return to_float(left) + to_float(right)
                if isinstance(left, vector) and isinstance(right, vector):
                    return left + right
                if self._is_zero_value(left):
                    return right
                if self._is_zero_value(right):
                    return left
                return Expr.binary(op, left, right, left_type)
            if is_number(left) and is_number(right):
                return to_float(left) - to_float(right)
            if isinstance(left, vector) and isinstance(right, vector):
                return left - right
            if self._is_zero_value(right):
                return left
            if self._is_zero_value(left):
                return self.apply_binary("*", -1.0, right)
            return Expr.binary(op, left, right, left_type)

        if op == "*":
            if left_type == "scalar" and right_type == "scalar":
                if is_number(left) and is_number(right):
                    return to_float(left) * to_float(right)
                if self._is_zero_value(left) or self._is_zero_value(right):
                    return 0.0
                if self._is_one_value(left):
                    return right
                if self._is_one_value(right):
                    return left
                return Expr.binary(op, left, right, "scalar")
            if left_type == "vector" and right_type == "vector":
                if isinstance(left, vector) and isinstance(right, vector):
                    return left * right
                return Expr.binary(op, left, right, "scalar")
            if left_type == "scalar" and right_type == "vector":
                if is_number(left) and isinstance(right, vector):
                    return right * left
                if self._is_zero_value(left) or self._is_zero_value(right):
                    return zero_vector()
                if self._is_one_value(left):
                    return right
                return Expr.binary(op, left, right, "vector")
            if left_type == "vector" and right_type == "scalar":
                if isinstance(left, vector) and is_number(right):
                    return left * right
                if self._is_zero_value(left) or self._is_zero_value(right):
                    return zero_vector()
                if self._is_one_value(right):
                    return left
                return Expr.binary(op, left, right, "vector")
            raise TypeError(f"Unsupported operand types for *: {left_type} and {right_type}")

        if op == "/":
            if right_type != "scalar":
                raise TypeError("Division requires a scalar denominator.")
            if is_number(right) and almost_zero(right):
                raise ZeroDivisionError("Division by zero.")
            if left_type == "scalar":
                if is_number(left) and is_number(right):
                    return to_float(left) / to_float(right)
                if self._is_zero_value(left):
                    return 0.0
                if self._is_one_value(right):
                    return left
                return Expr.binary(op, left, right, "scalar")
            if left_type == "vector":
                if isinstance(left, vector) and is_number(right):
                    return left / right
                if self._is_zero_value(left):
                    return zero_vector()
                if self._is_one_value(right):
                    return left
                return Expr.binary(op, left, right, "vector")
            raise TypeError(f"Unsupported operand types for /: {left_type} and {right_type}")

        if op == "X":
            if left_type != "vector" or right_type != "vector":
                raise TypeError("Cross products require two vectors.")
            if isinstance(left, vector) and isinstance(right, vector):
                return vector.cross_product(left, right)
            if self._is_zero_value(left) or self._is_zero_value(right):
                return zero_vector()
            return Expr.binary(op, left, right, "vector")

        raise ValueError(f"Unknown operator: {op}")

    def apply_function(self, name, arg):
        arg_type = self.value_type(arg)
        if name in {"cos", "sin", "acos", "asin", "atan"}:
            if arg_type != "scalar":
                raise TypeError(f"Function '{name}' requires a scalar argument.")
            if is_number(arg):
                angle = to_float(arg)
                if name == "cos":
                    return math.cos(angle * math.pi / 180)
                if name == "sin":
                    return math.sin(angle * math.pi / 180)
                if name == "acos":
                    return math.acos(angle) * 180 / math.pi
                if name == "asin":
                    return math.asin(angle) * 180 / math.pi
                return math.atan(angle) * 180 / math.pi
            return Expr.function(name, arg, "scalar")

        if name == "n":
            if arg_type != "vector":
                raise TypeError("Function 'n' requires a vector argument.")
            if isinstance(arg, vector):
                return vector.norm(arg)
            return Expr.function(name, arg, "scalar")

        if name == "nr":
            if arg_type != "vector":
                raise TypeError("Function 'nr' requires a vector argument.")
            if isinstance(arg, vector):
                return vector.normalized(arg)
            return Expr.function(name, arg, "vector")

        raise ValueError(f"Unknown function: {name}")

    def solve_system(self, equations, unknowns=None):
        try:
            parsed_equations = [self._coerce_equation(item) for item in equations]
            evaluated = []
            all_symbols = set()
            for eqn in parsed_equations:
                lhs = self.evaluate_expression(eqn.lhs)
                rhs = self.evaluate_expression(eqn.rhs)
                evaluated.append((lhs, rhs))
                all_symbols |= self._collect_symbols(lhs)
                all_symbols |= self._collect_symbols(rhs)

            if unknowns is None:
                ordered_symbols = sorted(
                    name for name in all_symbols if name in self.symbols and self._is_unresolved_symbol(name)
                )
            else:
                ordered_symbols = []
                for name in unknowns:
                    if name not in self.symbols:
                        raise ValueError(f"Unknown symbolic variable: {name}")
                    if name not in ordered_symbols:
                        ordered_symbols.append(name)

            unknown_type_map = {name: self.symbols[name] for name in ordered_symbols}
            replacements = {}
            remaining = list(evaluated)

            while True:
                progress = False
                next_remaining = []
                for lhs, rhs in remaining:
                    lhs = self._substitute_value(lhs, replacements)
                    rhs = self._substitute_value(rhs, replacements)
                    if self._both_concrete(lhs, rhs):
                        if not self._values_equal(lhs, rhs):
                            return self._solve_result("no_solution", None, "The system is inconsistent.")
                        continue

                    direct = self._try_direct_function_solution(lhs, rhs, unknown_type_map, replacements)
                    if direct is None:
                        next_remaining.append((lhs, rhs))
                        continue
                    if direct["status"] != "solved":
                        return direct
                    replacements[direct["name"]] = direct["value"]
                    del unknown_type_map[direct["name"]]
                    progress = True
                remaining = next_remaining
                if not progress:
                    break

            component_unknowns = []
            for name in ordered_symbols:
                if name in replacements:
                    continue
                if self.symbols[name] == "scalar":
                    component_unknowns.append(name)
                else:
                    component_unknowns.extend([component_name(name, i) for i in range(3)])

            rows = []
            constants = []
            deferred = []

            for lhs, rhs in remaining:
                diff = self.apply_binary("-", lhs, rhs)
                diff = self._substitute_value(diff, replacements)
                if self._is_concrete_zero(diff):
                    continue
                if self._is_concrete_value(diff):
                    return self._solve_result("no_solution", None, "The system is inconsistent.")

                function_names = self._collect_function_names(diff)
                if function_names:
                    if function_names <= {"n", "nr"}:
                        deferred.append(diff)
                        continue
                    return self._solve_result(
                        "invalid",
                        None,
                        "Only direct single-unknown scalar trig equations can be inverted by the solver.",
                    )

                try:
                    if self.value_type(diff) == "scalar":
                        forms = [self._linearize_scalar(diff, unknown_type_map)]
                    else:
                        forms = self._linearize_vector(diff, unknown_type_map).components
                except LinearizationError as exc:
                    return self._solve_result("invalid", None, str(exc))

                for form in forms:
                    row = [form.coeffs.get(name, 0.0) for name in component_unknowns]
                    rhs_value = -form.constant
                    if all(almost_zero(value) for value in row):
                        if not almost_zero(rhs_value):
                            return self._solve_result("no_solution", None, "The system is inconsistent.")
                        continue
                    rows.append(row)
                    constants.append(rhs_value)

            linear_solution = {}
            if component_unknowns:
                matrix_result = self._solve_matrix(rows, constants, component_unknowns)
                if matrix_result["status"] != "solved":
                    return matrix_result
                linear_solution = matrix_result["solution"]

            merged = {}
            merged.update(replacements)
            merged.update(self._collapse_component_solution(linear_solution, ordered_symbols))

            validation = self._validate_solution(evaluated, merged, ordered_symbols)
            if validation["status"] != "solved":
                return validation

            if deferred and self._solution_still_symbolic(evaluated, merged):
                return self._solve_result(
                    "infinite_solutions",
                    None,
                    "Norm and normalization constraints do not uniquely determine all unknowns.",
                )

            for name, value in merged.items():
                self.vars[name] = value

            if not ordered_symbols:
                return self._solve_result("solved", {}, "No symbolic unknowns were present in the system.")

            solution = {name: merged[name] for name in ordered_symbols if name in merged}
            return self._solve_result("solved", solution, "System solved.")
        except Exception as exc:
            return self._solve_result("invalid", None, str(exc))

    def _coerce_equation(self, item):
        if isinstance(item, equation):
            return item
        if isinstance(item, str):
            return equation(item)
        raise TypeError("solve_system expects equation objects or equation strings.")

    def _evaluate_ast(self, node):
        if node.kind == "number":
            return node.value
        if node.kind == "identifier":
            return self._resolve_identifier(node.name)
        if node.kind == "vector":
            components = [self._evaluate_ast(component) for component in node.components]
            if not all(is_number(component) for component in components):
                raise ValueError("Vector literal components must evaluate to numeric scalars.")
            return vector(components[0], components[1], components[2])
        if node.kind == "binary":
            left = self._evaluate_ast(node.left)
            right = self._evaluate_ast(node.right)
            return self.apply_binary(node.op, left, right)
        if node.kind == "function":
            arg = self._evaluate_ast(node.arg)
            return self.apply_function(node.func, arg)
        raise ValueError(f"Unknown AST node: {node.kind}")

    def _resolve_identifier(self, name):
        if name in self.vars:
            return self.vars[name]
        if name in self.symbols:
            return Expr.symbol(name, self.symbols[name])
        raise NameError(f"Unknown identifier: {name}")

    def _substitute_value(self, value, replacements):
        if not isinstance(value, Expr):
            return value
        if value.kind == "symbol":
            return replacements.get(value.name, value)
        if value.kind == "binary":
            left = self._substitute_value(value.left, replacements)
            right = self._substitute_value(value.right, replacements)
            return self.apply_binary(value.op, left, right)
        if value.kind == "function":
            arg = self._substitute_value(value.arg, replacements)
            return self.apply_function(value.func, arg)
        return value

    def _collect_symbols(self, value):
        if isinstance(value, Expr):
            if value.kind == "symbol":
                return {value.name}
            if value.kind == "binary":
                return self._collect_symbols(value.left) | self._collect_symbols(value.right)
            if value.kind == "function":
                return self._collect_symbols(value.arg)
        return set()

    def _collect_function_names(self, value):
        if isinstance(value, Expr):
            if value.kind == "function":
                return {value.func} | self._collect_function_names(value.arg)
            if value.kind == "binary":
                return self._collect_function_names(value.left) | self._collect_function_names(value.right)
        return set()

    def _linearize_scalar(self, value, unknown_type_map):
        if is_number(value):
            return LinearScalar(value)
        if isinstance(value, vector):
            raise LinearizationError("Expected a scalar expression, but found a vector.")
        if not isinstance(value, Expr):
            raise LinearizationError("Unsupported scalar expression.")

        if value.kind == "symbol":
            if value.value_type != "scalar":
                raise LinearizationError(f"Vector symbol '{value.name}' cannot appear as a scalar unknown.")
            if value.name not in unknown_type_map:
                raise LinearizationError(f"Unresolved scalar symbol '{value.name}' is not in the solve set.")
            return LinearScalar(0.0, {value.name: 1.0})

        if value.kind == "binary":
            left_type = self.value_type(value.left)
            right_type = self.value_type(value.right)

            if value.op == "+":
                return self._linearize_scalar(value.left, unknown_type_map).add(
                    self._linearize_scalar(value.right, unknown_type_map)
                )
            if value.op == "-":
                return self._linearize_scalar(value.left, unknown_type_map).sub(
                    self._linearize_scalar(value.right, unknown_type_map)
                )
            if value.op == "*":
                if left_type == "scalar" and right_type == "scalar":
                    left_form = self._linearize_scalar(value.left, unknown_type_map)
                    right_form = self._linearize_scalar(value.right, unknown_type_map)
                    if left_form.is_constant():
                        return right_form.scale(left_form.constant)
                    if right_form.is_constant():
                        return left_form.scale(right_form.constant)
                    raise LinearizationError("Symbolic scalar multiplication is nonlinear.")
                if left_type == "vector" and right_type == "vector":
                    return self._dot_linear(
                        self._linearize_vector(value.left, unknown_type_map),
                        self._linearize_vector(value.right, unknown_type_map),
                    )
                raise LinearizationError("Unsupported scalar multiplication.")
            if value.op == "/":
                denominator = self._linearize_scalar(value.right, unknown_type_map)
                if not denominator.is_constant():
                    raise LinearizationError("Division by a symbolic scalar is nonlinear.")
                if almost_zero(denominator.constant):
                    raise LinearizationError("Division by zero.")
                return self._linearize_scalar(value.left, unknown_type_map).scale(1.0 / denominator.constant)
            raise LinearizationError("Cross products do not produce scalar equations.")

        raise LinearizationError("Symbolic functions are not linear.")

    def _linearize_vector(self, value, unknown_type_map):
        if isinstance(value, vector):
            return LinearVector.constant(value)
        if is_number(value):
            raise LinearizationError("Expected a vector expression, but found a scalar.")
        if not isinstance(value, Expr):
            raise LinearizationError("Unsupported vector expression.")

        if value.kind == "symbol":
            if value.value_type != "vector":
                raise LinearizationError(f"Scalar symbol '{value.name}' cannot appear as a vector unknown.")
            if value.name not in unknown_type_map:
                raise LinearizationError(f"Unresolved vector symbol '{value.name}' is not in the solve set.")
            return LinearVector.symbol(value.name)

        if value.kind == "binary":
            left_type = self.value_type(value.left)
            right_type = self.value_type(value.right)

            if value.op == "+":
                return self._linearize_vector(value.left, unknown_type_map).add(
                    self._linearize_vector(value.right, unknown_type_map)
                )
            if value.op == "-":
                return self._linearize_vector(value.left, unknown_type_map).sub(
                    self._linearize_vector(value.right, unknown_type_map)
                )
            if value.op == "*":
                if left_type == "scalar" and right_type == "vector":
                    return self._scale_linear_vector(
                        self._linearize_scalar(value.left, unknown_type_map),
                        self._linearize_vector(value.right, unknown_type_map),
                    )
                if left_type == "vector" and right_type == "scalar":
                    return self._scale_linear_vector(
                        self._linearize_scalar(value.right, unknown_type_map),
                        self._linearize_vector(value.left, unknown_type_map),
                    )
                raise LinearizationError("Only scalar-vector multiplication can produce vector equations.")
            if value.op == "/":
                denominator = self._linearize_scalar(value.right, unknown_type_map)
                if not denominator.is_constant():
                    raise LinearizationError("Division by a symbolic scalar is nonlinear.")
                if almost_zero(denominator.constant):
                    raise LinearizationError("Division by zero.")
                return self._linearize_vector(value.left, unknown_type_map).scale_by_constant(1.0 / denominator.constant)
            if value.op == "X":
                return self._cross_linear(
                    self._linearize_vector(value.left, unknown_type_map),
                    self._linearize_vector(value.right, unknown_type_map),
                )

        raise LinearizationError("Symbolic functions are not linear.")

    def _scale_linear_vector(self, scalar_form, vector_form):
        if scalar_form.is_constant():
            return vector_form.scale_by_constant(scalar_form.constant)
        if vector_form.is_constant():
            base = vector_form.as_vector()
            return LinearVector(
                [
                    scalar_form.scale(base.x),
                    scalar_form.scale(base.y),
                    scalar_form.scale(base.z),
                ]
            )
        raise LinearizationError("Scalar-vector products with unknowns on both sides are nonlinear.")

    def _dot_linear(self, left_vector, right_vector):
        if left_vector.is_constant():
            left = left_vector.as_vector()
            return (
                right_vector.components[0].scale(left.x)
                .add(right_vector.components[1].scale(left.y))
                .add(right_vector.components[2].scale(left.z))
            )
        if right_vector.is_constant():
            right = right_vector.as_vector()
            return (
                left_vector.components[0].scale(right.x)
                .add(left_vector.components[1].scale(right.y))
                .add(left_vector.components[2].scale(right.z))
            )
        raise LinearizationError("Dot products between two unresolved vectors are nonlinear.")

    def _cross_linear(self, left_vector, right_vector):
        if left_vector.is_constant():
            left = left_vector.as_vector()
            rx, ry, rz = right_vector.components
            return LinearVector(
                [
                    ry.scale(-left.z).add(rz.scale(left.y)),
                    rx.scale(left.z).add(rz.scale(-left.x)),
                    rx.scale(-left.y).add(ry.scale(left.x)),
                ]
            )
        if right_vector.is_constant():
            right = right_vector.as_vector()
            lx, ly, lz = left_vector.components
            return LinearVector(
                [
                    ly.scale(right.z).add(lz.scale(-right.y)),
                    lx.scale(-right.z).add(lz.scale(right.x)),
                    lx.scale(right.y).add(ly.scale(-right.x)),
                ]
            )
        raise LinearizationError("Cross products between two unresolved vectors are nonlinear.")

    def _solve_matrix(self, rows, constants, component_unknowns):
        if not component_unknowns:
            return self._solve_result("solved", {}, "No linear unknowns remain.")

        if not rows:
            return self._solve_result(
                "infinite_solutions",
                None,
                "The system does not contain enough linear equations to determine all unknowns.",
            )

        augmented = [row[:] + [constants[i]] for i, row in enumerate(rows)]
        row_count = len(augmented)
        column_count = len(component_unknowns)
        pivot_columns = []
        pivot_row = 0

        for column in range(column_count):
            best_row = pivot_row
            best_value = 0.0
            for row in range(pivot_row, row_count):
                value = abs(augmented[row][column])
                if value > best_value:
                    best_value = value
                    best_row = row
            if best_value <= EPSILON:
                continue

            augmented[pivot_row], augmented[best_row] = augmented[best_row], augmented[pivot_row]
            pivot_value = augmented[pivot_row][column]
            for entry in range(column, column_count + 1):
                augmented[pivot_row][entry] /= pivot_value

            for row in range(row_count):
                if row == pivot_row:
                    continue
                factor = augmented[row][column]
                if almost_zero(factor):
                    continue
                for entry in range(column, column_count + 1):
                    augmented[row][entry] -= factor * augmented[pivot_row][entry]

            pivot_columns.append(column)
            pivot_row += 1
            if pivot_row == row_count:
                break

        for row in augmented:
            if all(almost_zero(value) for value in row[:-1]) and not almost_zero(row[-1]):
                return self._solve_result("no_solution", None, "The linear system is inconsistent.")

        if len(pivot_columns) < column_count:
            return self._solve_result(
                "infinite_solutions",
                None,
                "The linear system is underdetermined.",
            )

        solution = {}
        for row_index, column in enumerate(pivot_columns):
            solution[component_unknowns[column]] = augmented[row_index][-1]
        return self._solve_result("solved", solution, "Linear system solved.")

    def _collapse_component_solution(self, component_solution, ordered_symbols):
        solution = {}
        for name in ordered_symbols:
            if name in component_solution:
                solution[name] = component_solution[name]
                continue
            if self.symbols[name] == "vector":
                x_name = component_name(name, 0)
                y_name = component_name(name, 1)
                z_name = component_name(name, 2)
                if x_name in component_solution and y_name in component_solution and z_name in component_solution:
                    solution[name] = vector(
                        component_solution[x_name],
                        component_solution[y_name],
                        component_solution[z_name],
                    )
        return solution

    def _validate_solution(self, equations, solution, ordered_symbols):
        for lhs, rhs in equations:
            lhs_value = self._substitute_value(lhs, solution)
            rhs_value = self._substitute_value(rhs, solution)
            if self._both_concrete(lhs_value, rhs_value):
                if not self._values_equal(lhs_value, rhs_value):
                    return self._solve_result("no_solution", None, "The proposed solution does not satisfy the system.")
                continue

            symbols = self._collect_symbols(lhs_value) | self._collect_symbols(rhs_value)
            unresolved_targets = [name for name in ordered_symbols if name in symbols]
            if unresolved_targets:
                deferred_functions = self._collect_function_names(lhs_value) | self._collect_function_names(rhs_value)
                if deferred_functions <= {"n", "nr"} and deferred_functions:
                    return self._solve_result(
                        "infinite_solutions",
                        None,
                        "Norm and normalization constraints leave the system underdetermined.",
                    )
                return self._solve_result(
                    "invalid",
                    None,
                    "The system still contains unsupported symbolic expressions after solving.",
                )

        return self._solve_result("solved", {}, "Validated.")

    def _solution_still_symbolic(self, equations, solution):
        for lhs, rhs in equations:
            lhs_value = self._substitute_value(lhs, solution)
            rhs_value = self._substitute_value(rhs, solution)
            if self._collect_symbols(lhs_value) or self._collect_symbols(rhs_value):
                return True
        return False

    def _try_direct_function_solution(self, lhs, rhs, unknown_type_map, replacements):
        for function_side, other_side in ((lhs, rhs), (rhs, lhs)):
            if not isinstance(function_side, Expr) or function_side.kind != "function":
                continue
            if function_side.func not in {"sin", "cos", "atan", "asin", "acos"}:
                continue
            if not is_number(other_side):
                continue
            arg = function_side.arg
            if not isinstance(arg, Expr) or arg.kind != "symbol" or arg.value_type != "scalar":
                continue
            if arg.name not in unknown_type_map:
                continue
            if unknown_type_map[arg.name] != "scalar":
                continue

            try:
                value = self._invert_function(function_side.func, other_side)
            except ValueError as exc:
                return self._solve_result("no_solution", None, str(exc))

            check_lhs = self._substitute_value(lhs, {arg.name: value, **replacements})
            check_rhs = self._substitute_value(rhs, {arg.name: value, **replacements})
            if not self._both_concrete(check_lhs, check_rhs) or not self._values_equal(check_lhs, check_rhs):
                return self._solve_result("no_solution", None, "The function equation has no principal-value solution.")

            return {"status": "solved", "name": arg.name, "value": value}
        return None

    def _invert_function(self, name, target):
        value = to_float(target)
        if name == "sin":
            if value < -1.0 - EPSILON or value > 1.0 + EPSILON:
                raise ValueError("sin(x) = c has no real solution for the requested c.")
            clipped = min(1.0, max(-1.0, value))
            return math.asin(clipped) * 180 / math.pi
        if name == "cos":
            if value < -1.0 - EPSILON or value > 1.0 + EPSILON:
                raise ValueError("cos(x) = c has no real solution for the requested c.")
            clipped = min(1.0, max(-1.0, value))
            return math.acos(clipped) * 180 / math.pi
        if name == "atan":
            if abs(value) >= 90.0 - EPSILON:
                raise ValueError("atan(x) only returns principal values in (-90, 90) degrees.")
            return math.tan(value * math.pi / 180)
        if name == "asin":
            if value < -90.0 - EPSILON or value > 90.0 + EPSILON:
                raise ValueError("asin(x) only returns principal values in [-90, 90] degrees.")
            return math.sin(value * math.pi / 180)
        if name == "acos":
            if value < -EPSILON or value > 180.0 + EPSILON:
                raise ValueError("acos(x) only returns principal values in [0, 180] degrees.")
            return math.cos(value * math.pi / 180)
        raise ValueError(f"Cannot invert function: {name}")

    def _solve_result(self, status, solution, message):
        return {"status": status, "solution": solution, "message": message}

    def _both_concrete(self, left, right):
        return self._is_concrete_value(left) and self._is_concrete_value(right)

    def _is_concrete_value(self, value):
        return is_number(value) or isinstance(value, vector)

    def _is_concrete_zero(self, value):
        if is_number(value):
            return almost_zero(value)
        if isinstance(value, vector):
            return all(almost_zero(component) for component in value.components())
        return False

    def _values_equal(self, left, right):
        if is_number(left) and is_number(right):
            return almost_zero(to_float(left) - to_float(right))
        if isinstance(left, vector) and isinstance(right, vector):
            return all(almost_zero(a - b) for a, b in zip(left.components(), right.components()))
        return False

    def _is_zero_value(self, value):
        if is_number(value):
            return almost_zero(value)
        if isinstance(value, vector):
            return self._is_concrete_zero(value)
        return False

    def _is_one_value(self, value):
        return is_number(value) and almost_zero(to_float(value) - 1.0)

    def _is_unresolved_symbol(self, name):
        value = self.vars.get(name)
        return isinstance(value, Expr) and value.kind == "symbol" and value.name == name

    def _is_valid_identifier(self, name):
        if not name:
            return False
        if not (name[0].isalpha() or name[0] == "_"):
            return False
        for char in name[1:]:
            if not (char.isalnum() or char == "_"):
                return False
        return name not in FUNCTION_NAMES and name != "sym"

    def __repr__(self):
        lines = []
        seen = set()
        for name in sorted(self.symbols.keys()):
            value = self.vars.get(name, Expr.symbol(name, self.symbols[name]))
            lines.append(f"{name} [{self.symbols[name]}]: {render_value(value)}")
            seen.add(name)
        for name in sorted(self.vars.keys()):
            if name in seen:
                continue
            lines.append(f"{name}: {render_value(self.vars[name])}")
        if not lines:
            return "\n"
        return "\n" + "\n".join(lines) + "\n"


class ui:
    env = environment()

    @classmethod
    def run_ui(cls):
        while True:
            line = input("Input an equation: ").strip()
            if line == "done":
                break
            try:
                cls.env.process_line(line)
            except Exception as exc:
                print(f"Error: {exc}")
        print(cls.env)


if __name__ == "__main__":
    ui.run_ui()
