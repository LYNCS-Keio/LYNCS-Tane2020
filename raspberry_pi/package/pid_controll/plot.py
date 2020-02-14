from matplotlib import pyplot
import core
y = []
x = []
y.append(0.0)
x.append(0)

p = core.pid(0.5, 0.5, 0.1)
for i in range(1, 100):
    y.append(p.update_pid(50, y[i-1], 1))
    x.append(i)

pyplot.plot(x, y)
pyplot.show()