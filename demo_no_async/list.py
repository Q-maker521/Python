#给定一个列表list[1,2,2,3,4,3]去重并保证原顺序
#运用字典去重，dict.fromkeys(可迭代对象，value=None)把传入序列里的每一项作为字典的key，value默认none
list6=[1,2,2,3,4,3]
res=list(dict.fromkeys(list6))
print(res)


from copy import deepcopy

###列表相关知识：有序，可变，可重复用[]表示

#1.创建列表
list1 = [1,2,3]#直接赋值
list2 = list('abc')#可迭代对象[a,b,c]

#2.索引与切片，与元组类似从0开始，-1代表最后一个元素
list3=[10,20,30]
print(list3[0],list3[-1])#10,20

#3.常用方法
#append(x)在末尾追加元素
#extend(iter)追加可迭代对象的所有元素（合并列表）
#insert(index,x)在指定位置插入元素
#pop(index)删除并返回索引元素，无参数默认删最后一个
#remove(x)删除第一个匹配的元素，找不到报错
#clear()清空列表
#sort(原地排序，默认升序，sort(reverse=true)降序)
#reverse()反转列表
#index(x)返回第一个元素匹配的索引，找不到报错
#count(x)统计元素出现次数

#4.增删改操作
list1[0]=5#索引赋值
del list1#删除后list1为空
del list2[1:3]#只剩[a]

#5.列表运算 类似元组 ，+拼接 *重复 in判断元素是否存在

#6.遍历列表
#(1)遍历元素
for item in list2:
    print(item)
#(2)遍历索引
for i in range(len(list2)):
    print(i,list2[i])
#(3)同时取索引和元素
for idx,val in enumerate(list2):
    print(idx,val)


#7.列表推导式
res=[i for i in range(11) if i%2==0]
print(res)#2,4,6,8,10


#8.深浅拷贝：列表直接赋值只是引用，指向同一个内存地址
a=[1,2,[3,4]]
b=a#引用，a变，b也变
#浅拷贝：
c=b.copy()#修改外层元素(1,2)，不会影响对方,修改内层元素([3,4])都会改变
#原理，浅拷贝只复制外层容器，里边嵌套的可变对象依旧共用一个引用
#深拷贝：导入copy模块
import copy
d=copy.deepcopy(a)
#递归复制所有层级，全部新建独立内存


#9.常用内置函数
print(len(list2))
max(list2)
min(list2)
sum(list3)#求和
