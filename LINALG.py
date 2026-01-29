from ti_system import * # type: ignore
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
<<<<<<< HEAD:LinAlg.py

def cross_product(vec1: list, vec2: list):
    return [vec1[1]*vec2[2]-vec2[1]*vec1[2], vec1[2]*vec2[0]-vec2[2]*vec1[0], vec1[0]*vec2[1]-vec2[0]*vec1[1]]

while not escape(): # type: ignore
    print("1) dot product")
    print("2) cross product")
    print("3) norm")
    print("4) normalize")
    print("5) theta")

    choice = int(input("Pick one of the above"))
    if choice == 1:
        print(dot_product(v1, v2))
    elif choice == 2:
        print(cross_product(v1, v2))
    elif choice == 3 :
        print(norm(v1), "\n", norm(v2))
    elif choice == 4:
            print(normalized(v1), "\n", normalized(v2))
    elif choice == 5:
            print(theta(v1), "\n", theta(v2))
=======
>>>>>>> 360a33d6197eb55c7302d183dbbac7d220146b26:LINALG.py
