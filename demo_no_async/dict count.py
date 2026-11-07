#Dict统计：统计"hello world python"每个单词中字母o的次数
str1="hello world python"
result={word:word.count('o') for word in str1.split()}
print(result)

#dict:可变、无序（3.7+插入有序），键值对的映射类型key:value
#1.创建字典：
d1={"name":"Tom","age":20}#字面量方式创建
d2=dict(name="Jerry",age=20)#dict()
d3=dict([('a',1),('b',2),('c',3)])#可迭代对象
d4=dict.fromkeys(['a','b','c'],3)#fromkeys快速创建，所有value相同
empty={}#空字典

#2.字典key(键)：
#1.key必须为不可变类型（可哈希hashable）:int\str\float\tuple
#2.键唯一：重复写同一个key,后面值覆盖前面：
d={"a":1,"a":99}
print(d)#{"a":99}

#3.取值、新增、修改、删除
#1.索引
d={"name":"Tom","age":20}
print(d["name"])#若key不存在直接报错keyError
#2.get(),key不存在直接返回None,可设默认值
print(d.get("age"))
print(d.get("gender","女"))#女

d["name"]="Jerry"#若key存在就是修改，不存在就是新增

del d["name"]#删除指定key,不会报错
res=d.pop("gender")#删除并返回value,可加默认值d.pop("x",0)
res1=d.popitem()#删除最后插入的键值对，返回（key,value）,空字典抛错
d.clear()#清空字典



