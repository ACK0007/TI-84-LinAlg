from ti_python_module import ti_system as ts
import numpy as np


x1 = float(input("x1= "))
y1 = float(input("x1= "))
z1 = float(input("x1= "))
v1 = np.array([x1,y1,z1])

x2 = float(input("x1= "))
y2 = float(input("x1= "))
z2 = float(input("x1= "))
v2 = np.array([x2,y2,z2])

def norm(vec: np.array):
    return np.sqrt(np.sum(vec^2))

def normalized(vec: np.array):
    return vec/norm(vec)
