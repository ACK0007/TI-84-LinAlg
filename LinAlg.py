#from ti_python_module import ti_system as ts
import math

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
    return math.sqrt(sum(dot_product(vec,vec)))

def normalized(vec: list):
    norm = norm(vec)
    return map(lambda x: x*1/norm, vec)

def theta(vec1: list, vec2: list):
    return math.acos(dot_product(vec1,vec2)/(norm(vec1)*norm(vec2)))*180/math.pi