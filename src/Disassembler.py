import dis
import math

x = lambda x, y: math.sqrt(x**2 + y**2)

dis.dis(x)
print(dis.code_info(x))

set().union()