import subprocess

for _ in range(60):
    subprocess.run(["scp", "Alegria@24.201.18.112:feed.jpg", "feed.jpg"])
