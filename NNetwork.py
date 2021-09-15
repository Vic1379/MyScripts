import random as rd, math

class NNetwork:
    def __init__(self, rate = 0.1):
        self.rate = rate
        self.w1, self.b1 = [rd.uniform(0, 1), rd.uniform(0, 1), rd.uniform(0, 1)], rd.uniform(0, 1)
        self.w2, self.b2 = [rd.uniform(0, 1), rd.uniform(0, 1), rd.uniform(0, 1)], rd.uniform(0, 1)
        self.w3, self.b3 = [rd.uniform(0, 1), rd.uniform(0, 1), rd.uniform(0, 1)], rd.uniform(0, 1)
        self.w4, self.b4 = [rd.uniform(0, 1), rd.uniform(0, 1), rd.uniform(0, 1)], rd.uniform(0, 1)
        self.n1, self.n2, self.n3, self.n4 = 0, 0, 0, 0
    def node_1(self, x): return x[0]*self.w1[0]+x[1]*self.w1[1]+x[2]*self.w1[2]+self.b1
    def node_2(self, x): return x[0]*self.w2[0]+x[1]*self.w2[1]+x[2]*self.w2[2]+self.b2
    def node_3(self, x): return x[0]*self.w3[0]+x[1]*self.w3[1]+x[2]*self.w3[2]+self.b3
    def node_4(self, x): return x[0]*self.w4[0]+x[1]*self.w4[1]+x[2]*self.w4[2]+self.b4
    def activation(self, x): return 1/(1+math.exp(-x))
    def d_act(self, node): return node*(1-node)
    def predict(self, x):
        self.n1 = self.activation(self.node_1(x))
        self.n2 = self.activation(self.node_2(x))
        self.n3 = self.activation(self.node_3(x))
        self.n4 = self.activation(self.node_4([self.n1, self.n2, self.n3]))
        return self.n4
    def train(self, x, y):
        for i in range(len(x)):
            r = self.predict(x[i])
            if r > 0.5: res = 1
            else: res = 0
            if res != y:
                de_p = 2*(r-y[i])
                dp_4 = self.d_act(self.n4)
                d4_w4 = [self.n1, self.n2, self.n3]
                d4_3 = self.w4[2]*self.d_act(self.n3)
                d4_2 = self.w4[1]*self.d_act(self.n2)
                d4_1 = self.w4[0]*self.d_act(self.n1)
                dl1_w = x[i]
                self.w4 = [
                    self.w4[0]-de_p*dp_4*d4_w4[0]*self.rate,
                    self.w4[1]-de_p*dp_4*d4_w4[1]*self.rate,
                    self.w4[2]-de_p*dp_4*d4_w4[2]*self.rate
                ]
                self.b4 = self.b4-de_p*dp_4*self.rate
                self.w3 = [
                    self.w3[0]-de_p*dp_4*d4_3*dl1_w[0]*self.rate,
                    self.w3[1]-de_p*dp_4*d4_3*dl1_w[1]*self.rate,
                    self.w3[2]-de_p*dp_4*d4_3*dl1_w[2]*self.rate
                ]
                self.b3 = self.b3-de_p*dp_4*d4_3*self.rate
                self.w2 = [
                    self.w2[0]-de_p*dp_4*d4_2*dl1_w[0]*self.rate,
                    self.w2[1]-de_p*dp_4*d4_2*dl1_w[1]*self.rate,
                    self.w2[2]-de_p*dp_4*d4_2*dl1_w[2]*self.rate
                ]
                self.b2 = self.b2-de_p*dp_4*d4_2*self.rate
                self.w1 = [
                    self.w1[0]-de_p*dp_4*d4_1*dl1_w[0]*self.rate,
                    self.w1[1]-de_p*dp_4*d4_1*dl1_w[1]*self.rate,
                    self.w1[2]-de_p*dp_4*d4_1*dl1_w[2]*self.rate
                ]
                self.b1 = self.b1-de_p*dp_4*d4_1*self.rate

x, y, inp = [], [], 'start'
for i in range (100000):
    x.append([rd.randint(0, 1), rd.randint(0, 1), rd.randint(0, 1)])
    if x[i] == [1, 0, 1] or x[i] == [0, 1, 0]: y.append(1)
    else: y.append(0)
net = NNetwork()
net.train(x, y)
print(net.w1, net.b1)
print(net.w2, net.b2)
print(net.w3, net.b3)
print(net.w4, net.b4)
while inp != '':
    inp = input()
    x = inp.split()
    if len(x) == 3:
        x[0], x[1], x[2] = int(x[0]), int(x[1]), int(x[2])
        print(net.predict(x))