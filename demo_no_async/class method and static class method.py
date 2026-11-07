class Date:
    def __init__(self,year,month,day):
        self.year=year
        self.month=month
        self.day=day
    #实例方法：必须接收self,操作实例对象
    def display(self):
        """实例方法：打印日期"""
        print(f"{self.year}年{self.month:02d}月{self.day:02d}日")
    @classmethod
    def from_string(cls,date_str):
        """
        类方法：@classmethod,第一个参数cls代表当前类
        作用：从字符串“2026-09-19”构造Date对象
        """
    #分割字符串
        y,m,d=map(int,date_str.split('-'))
        return cls(y,m,d)
    @staticmethod
    def is_valid_date(year,month,day):
        """
        静态方法：@staticmethod,不需要self/cls
        属于类的工具函数，不访问实例和类属性
        只做独立逻辑判断，日期合法性校验
        :param year:
        :param month:
        :param day:
        :return:
        """
        #简单校验
        if not (1<=month<=12):
            return False
        month_days=[31,28,31,30,31,30,31,31,30,31,30,31]
        #闰年处理
        if (year%4==0 and year%100!=0 )or (year%400==0):
            month_days[1]=29
        return 1<=day<=month_days[month-1]
#方式1：直接构造实例
d1=Date(2026,9,19)
d1.display()
#方式2：调用类方法 from_string,字符串生成实例
d2=Date.from_string('2026-09-19')
d2.display()
#调用静态方法
print(d1.is_valid_date(2024,2,29))
print(d2.is_valid_date(2025,2,29))
