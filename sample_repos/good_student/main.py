"""
A well-structured Python app demonstrating good coding practices.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def add_numbers(a: int, b: int) -> int:
    """
    Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b


def greet_user(name: str) -> str:
    """
    Generate a greeting message for the user.

    Args:
        name: The user's name

    Returns:
        A greeting string
    """
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}! Welcome to CMSC389A."


if __name__ == "__main__":
    result = add_numbers(3, 5)
    print(f"3 + 5 = {result}")
    print(greet_user("Student"))
