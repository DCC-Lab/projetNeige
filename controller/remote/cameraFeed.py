import subprocess

for _ in range(60):
    subprocess.run(["scp", "Alegria@192.168.0.188:feed2.jpg", "feed.jpg"])
