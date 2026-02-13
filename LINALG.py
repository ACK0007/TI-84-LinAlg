#from ti_system import * # type: ignore
import math

class vector():
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    
    @classmethod
    def norm(cls, v: vector):
        return math.sqrt(v.x**2 + v.y**2 + v.z**2)
    
    @classmethod
    def normalized(cls, v: vector):
        n = cls.norm(v)
        return vector(v.x/n, v.y/n, v.z/n)
    
    def __add__(self, other):
        if isinstance(other, vector):
            return vector(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            raise TypeError("Unsupported operand type(s) for +")
    
    def __sub__(self, other):
        if isinstance(other, vector):
            return vector(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            raise TypeError("Unsupported operand type(s) for -")
        
    def __mul__(self, other):
        if isinstance(other, vector):
            return self.x*other.x + self.z*other.y + self.z*other.z
        elif isinstance(other, float):
            return vector(other*self.x, other*self.y, other*self.z)
        elif isinstance(other, int):
            other = float(other)
            return self*other
        else:
            raise TypeError("Unsupported operand type(s) for *")
        
    def __rmul__(self, other):
        return self.__mul__(other)
        
    def __truediv__(self, other: float):
        return self*(1/other)
    
    def __repr__(self):
        return f"{{{self.x},{self.y},{self.z}}}"
        
    @classmethod    
    def cross_product(cls, v1: vector, v2: vector):
        return vector(v1.y*v2.z-v2.y*v1.z, v1.z*v2.x-v2.z*v1.x, v1.x*v2.y-v2.x*v1.y)
    
    @classmethod
    def theta(cls, v1: vector, v2: vector):
        return math.acos(v1*v2/(cls.norm(v1)*cls.norm(v2)))*180/math.pi
    
class node():
    def __init__(self, contents: str|vector, parent: node|None = None):
        try:
            self.contents = float(contents)
        except:
            self.contents = contents
            
        self.parent = parent
        self.right_child = None
        self.left_child = None
        self.center_child = None
        
        
    def __repr__(self):
        return str(self.contents)


class equation():
    def __init__(self, eqn: str):
        self.eqn = eqn
        self.operations = {
            1: ["="],
            2: ["+", "-"],
            3: ["*", "X", "/"]
            }
        self.functions = ["cos", "sin", "acos", "asin", "atan", "n", "nr"]
        self.vars = {}
        self.tree = None
        self.operation_indices = []
        self.find_operation_indices()
        self.make_tree()
    
    def find_operation_indices(self):
        for i in range(len(self.eqn)):
            if self.eqn[i] in self.operations[1]:
                self.operation_indices.append((i,1))
            elif self.eqn[i] in self.operations[2]:
                self.operation_indices.append((i,2))
            elif self.eqn[i] in self.operations[3]:
                self.operation_indices.append((i,3))
            self.operation_indices.reverse()
                
                     
    def make_tree(self):
        for i,j in self.operation_indices:
            if j == 1:
                self.tree = node(self.eqn[i], None)
                self.make_nodes(self.tree, 'l', (0,i))
                self.make_nodes(self.tree, 'r', (i+1,len(self.eqn)))
                break
        
        
    def make_nodes(self, parent: node, direction: str, indices: tuple):
        assert direction in {'l', 'r', 'c'}
        operation_indices = list(filter(lambda x: indices[0] <= x[0] < indices[1] and x[1] != 1, self.operation_indices))
        index_range = slice(indices[0],indices[1])
        
        if len(operation_indices) == 0:
            if self.is_vector(self.eqn[index_range]):
                coords = self.find_coords(self.eqn[index_range])
                v = vector(coords[0], coords[1], coords[2])
                n = node(v, parent)
            elif self.is_function(self.eqn[index_range]):
                function = self.eqn[index_range].partition("(")[0]
                n = node(function, parent)
                if self.is_vector(self.eqn[indices[0]+len(function)+1: indices[1]-1]):
                    coords = self.find_coords(self.eqn[indices[0]+len(function)+1: indices[1]-1])
                    m = node(vector(coords[0], coords[1], coords[2]), n)
                else:
                    m = node(self.eqn[indices[0]+len(function)+1: indices[1]-1], n)
                n.center_child = m
            else:
                n = node(self.eqn[index_range], parent)
                
                if isinstance(n.contents,str):
                    self.vars[n.contents] = None
                    
            if direction == 'l':
                parent.left_child = n
            elif direction == 'r':
                parent.right_child = n
            elif direction == 'c':
                parent.center_child = n
            return

        max_op_precedent = 3
        for o in operation_indices:
            if o[1] == 2:
                max_op_precedent = 2
                break
                  
        for i,j in operation_indices:
            if j == max_op_precedent:
                
                n = node(self.eqn[i], parent)
                
                if direction == 'l':
                    parent.left_child = n
                elif direction == 'r':
                    parent.right_child = n
                    
                if self.contains_operation(self.eqn[indices[0]:i]):
                    self.make_nodes(n, 'l', (indices[0],i))
                else:
                    m = node(self.eqn[indices[0]:i], n)
                    n.left_child = m
                    if isinstance(m.contents,str):
                        self.vars[m.contents] = None
                
                if self.contains_operation(self.eqn[i+1:indices[1]]):
                    self.make_nodes(n, 'r', (i+1,indices[1]))
                else:
                    m = node(self.eqn[i+1:indices[1]], n)
                    n.right_child = m
                    if isinstance(m.contents,str):
                        self.vars[m.contents] = None
                break

        
    def contains_operation(self, expr: str):
        ops = []
        for j in self.operations.values():
            for i in j:
                ops.append(i)
        for o in ops:
            if o in expr:
                return True
        return False
    
    def is_vector(self, expr: str):
        return expr[0] == "{" and expr[-1] == "}" and expr.count(",") == 2
       
    def find_coords(self, vector: str):
        vector = vector.strip("{").strip("}")
        components = vector.split(",")
        return list(map(lambda x: float(x), components))
       
    def is_function(self, expr: str):
        for f in self.functions:
            if expr.startswith(f) and expr.strip(f)[0] == "(" and expr.strip(f)[-1] == ")":
                return True
        return False
       
    def print_value(self, starting_node: node):

        string = ''
        if starting_node != None:
            print(f"Node: {starting_node}\nParent: {starting_node.parent}\nLeft Child: {starting_node.left_child}\nRight Child: {starting_node.right_child}\nCenter Child: {starting_node.center_child}\n\n")
            string += self.print_value(starting_node.left_child)
            string += str(starting_node.contents)
            string += self.print_value(starting_node.right_child)
            if starting_node.center_child != None:
                string += f"({self.print_value(starting_node.center_child)})"
        return string


       
    def __repr__(self):
        return self.print_value(self.tree)
        
        
class environment():
    def __init__(self):
        self.equations = []
        self.vars = {}
        self.operations = {
            "+": lambda a,b: a+b,
            "-": lambda a,b: a-b,
            "*": lambda a,b: a*b,
            "/": lambda a,b: a/b,
            "X": lambda a,b: vector.cross_product(a,b)
        }
        self.functions = {
            "cos": lambda a: math.cos(a*math.pi/180),
            "sin": lambda a: math.sin(a*math.pi/180),
            "acos": lambda a: math.acos(a)*180/math.pi,
            "asin": lambda a: math.asin(a)*180/math.pi,
            "atan": lambda a: math.atan(a)*180/math.pi,
            "n": lambda a: vector.norm(a),
            "nr": lambda a: vector.normalized(a)
        }
        
    def add_equation(self, eqn: equation):
        self.equations.append(eqn)
        self.add_variables(eqn)
        self.evaluate_equation(eqn)
        
        
    def add_variables(self, eqn: equation):
        for i,j in eqn.vars.items():
            if i not in self.vars.keys():
                self.vars[i] = j
                
                
    def has_children(self, node: node):
        try:
            return not (node.left_child is None and node.right_child is None)
        except:
            return False
        
    def is_function(self, node: node):
        for f in self.functions:
            if node.contents == f:
                return True
        return False
    
    def evaluate_expression(self, expr: node):
        if self.is_function(expr):
            try:
                return self.functions[expr.contents](self.vars[expr.center_child.contents])
            except:
                return self.functions[expr.contents](expr.center_child.contents)

        
        if not self.has_children(expr):
            try:
                return self.vars[expr.contents]
            except:
                return expr.contents

        return self.operations[expr.contents](self.evaluate_expression(expr.left_child),self.evaluate_expression(expr.right_child))        
        
        
    def evaluate_equation(self, eqn: equation):
        rhs = self.evaluate_expression(eqn.tree.right_child)
        self.vars[eqn.tree.left_child.contents] = rhs
    
    
    def __repr__(self):
        return str(self.vars)
        
        
e = environment()
eqn = equation("r=2*3+1")
e.add_equation(eqn)
eqn2 = equation('AB=8')
e.add_equation(eqn2)
eqn3 = equation('AD=3')
e.add_equation(eqn3)
eqn4 = equation("z=AB*AD/4")
e.add_equation(eqn4)
eqn5 = equation("b=5+4*7+AD")
e.add_equation(eqn5)
eqn6 = equation("y={1,2,3}")
e.add_equation(eqn6)
eqn7 = equation("a=2*y")
e.add_equation(eqn7)
eqn8 = equation("c={4,5,6}")
e.add_equation(eqn8)
eqn9 = equation("k=cXa")
e.add_equation(eqn9)
eqn10 = equation('h=atan(1)')
e.add_equation(eqn10)
eqn11 = equation("v=n({1,1,1})")
e.add_equation(eqn11)
eqn12 = equation("h=nr({3,4,0})")
e.add_equation(eqn12)
eqn13 = equation("l=nr(h)")
print(eqn13)
e.add_equation(eqn13)
print(e)