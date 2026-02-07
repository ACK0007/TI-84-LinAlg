#from ti_system import * # type: ignore
import math

class vector():
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    
    def norm(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalized(self):
        n = self.norm()
        return vector(self.x/n, self.y/n, self.z/n)
    
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
        
    def cross_product(self, other: vector):
        return vector(self.y*other.z-other.y*self.z, self.z*other.x-other.z*self.x, self.x*other.y-other.x*self.y)
    
    def theta(self, other: vector):
        return math.acos(self*other/self.norm(self)*self.norm(other))*180/math.pi
    
class node():
    def __init__(self, contents: str|vector, parent: node|None = None, left_child: node|None = None, right_child: node|None = None):
        try:
            self.contents = float(contents)
        except:
            self.contents = contents
            
        self.parent = parent
        self.right_child = right_child
        self.left_child = left_child
        
    def __repr__(self):
        return str(self.contents)

class equation():
    def __init__(self, eqn: str):
        self.eqn = eqn
        self.operations = {
            1: ["="],
            2: ["+", "-"],
            3: ["*", "x", "/"]
            }
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
                self.tree = node(self.eqn[i], None, None, None)
                self.make_nodes(self.tree, 'l', (0,i))
                self.make_nodes(self.tree, 'r', (i+1,len(self.eqn)))
                break
        
        
    def make_nodes(self, parent: node, direction: str, indices: tuple):
        
        assert direction in {'l', 'r'}
        operation_indices = list(filter(lambda x: indices[0] <= x[0] < indices[1] and x[1] != 1, self.operation_indices))
        
        if len(operation_indices) == 0:
            if self.is_vector(self.eqn[indices[0]:indices[1]]):
                coords = self.find_coord(self.eqn[indices[0]:indices[1]])
                v = vector(coords[0], coords[1], coords[2])
                n = node(v, parent, None, None)
            else:
                n = node(self.eqn[indices[0]:indices[1]], parent, None, None)
                
                if isinstance(n.contents,str):
                    self.vars[n.contents] = None
                    
            if direction == 'l':
                parent.left_child = n
            elif direction == 'r':
                parent.right_child = n
            return

        max_op_precedent = 3
        for o in operation_indices:
            if o[1] == 2:
                max_op_precedent = 2
                break
                  
        for i,j in operation_indices:
            if j == max_op_precedent:
                
                n = node(self.eqn[i], parent, None, None)
                
                if direction == 'l':
                    parent.left_child = n
                elif direction == 'r':
                    parent.right_child = n
                    
                if self.contains_operation(self.eqn[indices[0]:i]):
                    self.make_nodes(n, 'l', (indices[0],i))
                else:
                    m = node(self.eqn[indices[0]:i], n, None, None)
                    n.left_child = m
                    if isinstance(m.contents,str):
                        self.vars[m.contents] = None
                
                if self.contains_operation(self.eqn[i+1:indices[1]]):
                    self.make_nodes(n, 'r', (i+1,indices[1]))
                else:
                    m = node(self.eqn[i+1:indices[1]], n, None, None)
                    n.right_child = m
                    if isinstance(m.contents,str):
                        self.vars[m.contents] = None
                    
                break

        
    def contains_operation(self, partial_equation: str):
        ops = []
        for j in self.operations.values():
            for i in j:
                ops.append(i)
        for o in ops:
            if o in partial_equation:
                return True
        return False
    
    def is_vector(self, partial_equation: str):
        return partial_equation[0] == "{" and partial_equation[-1] == "}" and partial_equation.count(",") == 2
       
    def find_coord(self, vector: str):
        vector = vector.strip("{").strip("}")
        components = vector.split(",")
        return list(map(lambda x: float(x), components))
       
    def print_value(self, starting_node: node):
        string = ''
        if starting_node != None:
            print(f"Node: {starting_node}\nParent: {starting_node.parent}\nLeft Child: {starting_node.left_child}\nRight Child: {starting_node.right_child}\n\n ")
            if starting_node.left_child != None:
                string += self.print_value(starting_node.left_child)
            string += str(starting_node.contents)
            if starting_node.right_child != None:
                string += self.print_value(starting_node.right_child)
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
            "/": lambda a,b: a/b
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
        
    
    def evaluate_expression(self, expr: node):
        
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
print(e)