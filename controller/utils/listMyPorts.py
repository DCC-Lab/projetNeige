from serial.tools import list_ports

ports = [e.device for e in list_ports.comports()]
print(ports)
