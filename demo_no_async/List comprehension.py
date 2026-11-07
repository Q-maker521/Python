#列表推导式，1-21中可被3整除数的平方
res=[i**2 for i in range(1,21) if i%3==0]
print(res)
