#魔术方法底层实现原理：Python底层会自动调用对应的魔术方法，规定好的 __名字__ 与之相对应
class Vector:
    def __init__(self,x,y):
        #初始化属性x,y
        self.x=x
        self.y=y
    def __str__(self):
        #str魔术方法，print对象时调用，返回字符串
        return f"Vector({self.x},{self.y})"
    def __add__(self,other):
        new_x=self.x+other.x
        new_y=self.y+other.y
        return Vector(new_x,new_y)
v1=Vector(1,2)
v2=Vector(3,4)
print(v1)
print(v2)
v3=v1+v2
print(v3)
