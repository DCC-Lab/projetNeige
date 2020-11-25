import subprocess
from picamera import PiCamera

cam = PiCamera()
cam.resolution = (1024, 576)
for _ in range(60):
    cam.capture("feed.jpg")
    subprocess.run(["scp", "feed.jpg", "Alegria@24.201.18.112:feed2.jpg"])
