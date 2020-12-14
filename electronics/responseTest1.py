from matplotlib import pyplot as plt


# test 1 = (reverse mode) = (GND -->|-- opamp)
# gain was still with the 100k and 2.2k
lux = [1906, 603, 563, 458, 394, 304, 194, 25, 14, 9]
voltage = [5.35, 2.42, 1.61, 1.33, 1.15, 0.918, 0.607, 0.173, 0.117, 0.35]
plt.plot(lux, voltage, linewidth=0.8, markersize=1)
plt.xlabel("Light Power (Lux)")
plt.ylabel("Amplified Diode Voltage (V)")
plt.show()

# test 2 = (forward mode) = (GND --|<-- opamp)
# resistance had to be changed in order to be able to reach 5V with approximately the same luminosity
# Rg is now 22Ohms
# there is a dark of 210mV
# if I increase the gain, it increases the dark current.
lux = [1713, 1616, 1455, 1206, 1178, 630, 530, 442, 358, 101, 71, 50, 30, ]
voltage = [4.96, 4.94, 4.90, 4.85, 4.84, 4.56, 4.505, 4.42, 4.36, 3.93, 3.84, 1.56 ,1.17]
plt.plot(lux, voltage, linewidth=0.8, markersize=1)
plt.xlabel("Light Power (Lux)")
plt.ylabel("Amplified Diode Voltage (V)")
plt.show()


# == TEST 3 == #

# test 3  = forward (no bias) = added a resistance in parrallel with capacitor.
lux = [1362, 1304, 1186, 696, 426, 71, 48, 44, 22, 0]
voltage = [3.01, 2.97, 2.95, 2.82, 2.74, 2.60, 2.09, 1.96, 1.43, 0.014]
plt.plot(lux, voltage, linewidth=0.8, markersize=1)
plt.xlabel("Luminance (Lux)")
plt.ylabel("Amplified Diode Voltage (V)")
plt.show()

# test3 = boosted gain (saturation is around 6.7V)
lux = [682, 422, 106, 44, 0]
voltage = [6.44, 6.20, 5.68, 5.5, 0.014]
plt.plot(lux, voltage, linewidth=0.8, markersize=1)
plt.xlabel("Luminance (Lux)")
plt.ylabel("Amplified Diode Voltage (V)")
plt.show()

# == TEST 4 == #
# Only the photodiode.
lux = [1582, 1476, 1255, 773, 320, 71, 48, 1, 0]
voltage = [0.350, 0.345, 0.342, 0.335, 0.318, 0.312, 0.272, 0.120, 0.01]
plt.plot(lux, voltage, linewidth=0.8, markersize=1, label="photodiode only")
plt.xlabel("Luminance (Lux)")
plt.ylabel("Amplified Diode Voltage (V)")
plt.legend()
plt.show()
