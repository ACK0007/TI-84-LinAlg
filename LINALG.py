from ti_system import * # type: ignore
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
        return self.x*other.x + self.z*other.y + self.z*other.z
    
    
        
        
        
x1 = float(input("x1= "))
y1 = float(input("y1= "))
z1 = float(input("z1= "))
v1 = [x1,y1,z1]

x2 = float(input("x2= "))
y2 = float(input("y2= "))
z2 = float(input("z2= "))
v2 = [x2,y2,z2]

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
