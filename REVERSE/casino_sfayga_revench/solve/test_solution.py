import subprocess

with open("solution.txt", "r") as f:
    commands = f.read().splitlines()

proc = subprocess.Popen(["./target/release/sfayga_casino2v"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

for cmd in commands:
    proc.stdin.write(cmd + "\n")
    proc.stdin.flush()

# Read the rest of the output
stdout, stderr = proc.communicate()
print(stdout)
print(stderr)
