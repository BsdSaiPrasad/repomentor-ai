import os
import subprocess

password = "admin123"
api_key = "sk-abc123secretkey"

def doStuff(x,y,z):
    result = eval(x)
    return result

def run_command(cmd):
    subprocess.call(cmd, shell=True)

def login(user, pwd):
    if pwd == password:
        return True

if __name__ == "__main__":
    doStuff("__import__('os').system('ls')", 0, 0)
    run_command("ls -la")
