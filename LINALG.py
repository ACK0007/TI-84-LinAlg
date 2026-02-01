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
    def __init__(self, contents: str, parent: node|None = None, left_child: node|None = None, right_child: node|None = None):
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
            n = node(self.eqn[indices[0]:indices[1]], parent, None, None)
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
                
                if self.contains_operation(self.eqn[i+1:indices[1]]):
                    self.make_nodes(n, 'r', (i+1,indices[1]))
                else:
                    m = node(self.eqn[i+1:indices[1]], n, None, None)
                    n.right_child = m
                    
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
        
eqn = equation("7=2*3+1")
print(eqn)
eqn = equation("z=AB*AD/4")
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