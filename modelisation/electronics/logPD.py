import matplotlib.pyplot as plt
import numpy as np


Ip_max = 12000 * 10**(-6) / 100  # V


def Id(tC):
    return 1 * 10 ** (-18)
    # tK = tC + 273.15
    # ta, tb = 44 + 273.15, 71 + 273.15
    # B = (tb / ta ** 10) ** (1/9)
    # A = 100 * 10 ** (-9) / np.log(tb * B)
    # return A * np.log(B * tK)


print(Id(25))


def Ip(tC):
    tK = tC + 273.15
    dtK = tK - 273.15 + 25
    return np.linspace(0, Ip_max, 100000) * (1 + 0.15 / 100 * dtK)


Vt = 0.0253  # V  (temp dependant)
# Vt = k_B * T / e
# Id = 1 * 10 ** (-9)  # A  (temp dependant)

# Ip = np.linspace(0, 12000 * 10**(-6) / 100, 100000)
# vout = Vt * np.log(Ip / Id)

# y = np.linspace(0, max(vout), 1024)
# x = Id * np.exp(y / Vt)

T = [25]
# T = np.linspace(-10, 30, 10)
for t in T:
    Id_t = Id(t)
    vout = Vt * np.log(Ip(t) / Id_t)

    y = np.linspace(0, max(vout), 1024)
    x = Id_t * np.exp(y / Vt)

    dv = np.max(vout) / 1024
    print("Rel at {} C = {}%".format(round(t, 1), round(dv / Vt * 100, 3)))
    plt.plot(Ip(t), vout, label=str(round(t, 1)))
    plt.plot(x, y, marker='.', linestyle='', color='r', markersize=1.5)

plt.legend()
plt.show()


#
# rel_error = round((x[1]-x[0]) / np.mean([x[1], x[0]]) * 100, 3)
# print(np.mean(rel_error))
# dv = np.max(vout) / 1024
# dlog = np.max(np.log(Ip / Id)) / 1024
# print(dlog * 100)
# print(dv/Vt * 100)
# print(x[:5])