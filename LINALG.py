#from ti_system import * # type: ignore
import math

class vector():
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    
    def norm(self):
        return math.sqrt(self.x^2 + self.y^2 + self.z^2)
    
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
    
class node():
    def __init__(self, contents: str, parent: node|None, left_child: node|None, right_child: node|None):
        try:
            self.contents = float(contents)
        except:
            self.contents = contents
            
        self.parent = parent
        self.right_child = right_child
        self.left_child = left_child

class equation():
    def __init__(self, eqn: str):
        self.eqn = eqn
        self.operations = ["=", "+", "-", "*" ,"x"]
        self.tree = None
        self.make_tree()
    
    def make_tree(self):
        i = 0
        while not self.eqn[i] in self.operations:
            i += 1
        self.tree = node(self.eqn[i], None, None, None)
        self.make_nodes(self.eqn[:i], self.tree, 'l')
        self.make_nodes(self.eqn[i+1:], self.tree, 'r')
        
    def contains_operation(self, partial_equation: str):
        for o in self.operations:
            if o in partial_equation:
                return True
        return False
        
    def make_nodes(self, partial_equation: str, parent: node, direction: str):
        assert direction in {'l', 'r'}
        if self.contains_operation(partial_equation):
            i = 0
            while not partial_equation[i] in self.operations:
                i += 1
                
            n = node(partial_equation[i], parent, None, None)
            if direction == 'l':
                parent.left_child = n
            elif direction == 'r':
                parent.right_child = n
            
            if self.contains_operation(partial_equation[:i]):
                self.make_nodes(partial_equation[:i], n, 'l')
            else:
                m = node(partial_equation[:i], n, None, None)
                n.right_child = m
            
            if self.contains_operation(partial_equation[i+1:]):
                self.make_nodes(partial_equation[i+1:], n, 'r')
            else:
                m = node(partial_equation[i+1:], n, None, None)
                n.left_child = m
        else:
            n = node(partial_equation, parent, None, None)
            if direction == 'l':
                parent.left_child = n
            elif direction == 'r':
                parent.right_child = n
        
        
       
    def print_value(self, starting_node: node):
        string = ''
        if starting_node.left_child != None:
            string += self.print_value(starting_node.left_child)
        print(string)
        string += str(starting_node.contents)
        print(string)
        if starting_node.right_child != None:
            string += self.print_value(starting_node.right_child)
        print(string)
        return string

       
    def __repr__(self):
        return self.print_value(self.tree)
        
eqn = equation("2*3+1")
print(eqn)
        
        


def dot_product(vec1: list, vec2: list):
    s = 0
    for i,j in zip(vec1,vec2):
        s += i*j
    return s

def norm(vec: list):
    return math.sqrt(dot_product(vec,vec))

def normalized(vec: list):
    n = norm(vec)
    return list(map(lambda x: x*1/n, vec))

def theta(vec1: list, vec2: list):
    return math.acos(dot_product(vec1,vec2)/(norm(vec1)*norm(vec2)))*180/math.pi

def cross_product(vec1: list, vec2: list):
    return [vec1[1]*vec2[2]-vec2[1]*vec1[2], vec1[2]*vec2[0]-vec2[2]*vec1[0], vec1[0]*vec2[1]-vec2[0]*vec1[1]]

'''
while not escape(): # type: ignore
    print("1) dot product")
    print("2) cross product")
    print("3) norm")
    print("4) normalize")
    print("5) theta")

    choice = int(input("Pick one of the above \n"))
    if choice == 1:
        print(dot_product(v1, v2))
    elif choice == 2:
        print(cross_product(v1, v2))
    elif choice == 3 :
        print(norm(v1), "\n", norm(v2))
    elif choice == 4:
            print(normalized(v1), "\n", normalized(v2))
    elif choice == 5:
            print(theta(v1, v2))
'''