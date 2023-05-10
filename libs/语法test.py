class Sample:
    def __init__(self):
        print("自动调用构造方法")
        # 定义了一个实例属性
        self.name = "小明"

test = Sample()
print(test.name)


class Person:
    def __init__(self, newPersionName):
        self.name = newPersionName


p = Person('Bob')
print(p.name)

