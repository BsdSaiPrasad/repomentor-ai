import os

def add_numbers(a, b):
    # adds two numbers
    return a + b

def greet_user(name):
    return f"Hello, {name}!"

def read_file(filepath):
    f = open(filepath, 'r')
    data = f.read()
    return data

if __name__ == "__main__":
    print(add_numbers(3, 5))
    print(greet_user("Student"))
