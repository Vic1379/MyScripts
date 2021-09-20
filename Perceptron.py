import random as rd, math

class Perceptron:
    def __init__(self, rate = 0.1):
        self.w1, self.b1, self.rate = [rd.uniform(0, 1), rd.uniform(0, 1), rd.uniform(0, 1)], rd.uniform(0, 1), rate
        self.l1, self.l2 = 0, 0
    def layer_one(self, x): return x[0]*self.w1[0]+x[1]*self.w1[1]+x[2]*self.w1[2]+self.b1
    def layer_two(self, x): return 1/(1+math.exp(-x))
    def dl_two(self): return self.l2*(1-self.l2)
    def predict(self, x):
        self.l1 = self.layer_one(x)
        self.l2 = self.layer_two(self.l1)
        return self.l2
    def train(self, x, y):
        for i in range(len(x)):
            r = self.predict(x[i])
            if r > 0.5: res = 1
            else: res = 0
            if res != y[i]:
                de_p = 2*(r-y[i])
                dp_1 = self.dl_two()
                d1_w = x[i]
                self.w1 = [
                    self.w1[0]-de_p*dp_1*d1_w[0]*self.rate,
                    self.w1[1]-de_p*dp_1*d1_w[1]*self.rate,
                    self.w1[2]-de_p*dp_1*d1_w[2]*self.rate
                ]
                self.b1 = self.b1-de_p*dp_1*self.rate

x, y, inp = [], [], 'start'
for i in range (10000):
    if i%10 == 0: x.append([1, 0, 1])
    else: x.append([rd.randint(0, 1), rd.randint(0, 1), rd.randint(0, 1)])
    if x[i] == [1, 0, 1]: y.append(1)
    else: y.append(0)
net = Perceptron()
net.train(x, y)
print(net.w1, net.b1)
while inp != '':
    inp = input()
    x = inp.split()
    if len(x) == 3:
        x[0], x[1], x[2] = int(x[0]), int(x[1]), int(x[2])
        print(net.predict(x))
