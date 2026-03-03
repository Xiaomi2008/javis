#!/usr/bin/env python3
"""Daily Python Interview Questions Generator"""

from javis import Javis

def generate_interview_questions():
    """Generate medium-level Python interview questions with explanations."""
    
    questions = [
        {
            'topic': 'Decorators',
            'question': 'What are decorators in Python and how do you create one?',
            'answer': '''A decorator is a function that takes another function as input and extends its behavior without explicitly modifying it.

Example:
```python
def my_decorator(func):
    def wrapper():
        print("Something before the function.")
        func()
        print("Something after the function.")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
# Output:
# Something before the function.
# Hello!
# Something after the function.
```''',
            'difficulty': 'Medium'
        },
        {
            'topic': 'Generators',
            'question': 'What is a generator and when would you use one?',
            'answer': '''A generator is a special type of iterator that yields values one at a time using the yield keyword, rather than returning all values at once like a regular function.

Benefits:
- Memory efficient (doesn't load entire sequence in memory)
- Lazy evaluation (values generated on demand)
- Can represent infinite sequences

Example:
```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

for num in fibonacci(10):
    print(num)
# Output: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34
```''',
            'difficulty': 'Medium'
        },
        {
            'topic': 'List Comprehensions',
            'question': 'How do list comprehensions work and what are their advantages?',
            'answer': '''List comprehensions provide a concise way to create lists in Python. They're more readable and often faster than equivalent for loops.

Basic syntax: [expression for item in iterable if condition]

Examples:
```python
# Square numbers from 0-9
squares = [x**2 for x in range(10)]
# Output: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# Even numbers only
evens = [x for x in range(10) if x % 2 == 0]
# Output: [0, 2, 4, 6, 8]

# Nested comprehension (matrix transpose)
matrix = [[1, 2, 3], [4, 5, 6]]
transposed = [[row[i] for row in matrix] for i in range(3)]
```''',
            'difficulty': 'Medium'
        },
        {
            'topic': 'Context Managers',
            'question': 'What are context managers and how do you create custom ones?',
            'answer': '''Context managers allow objects to be used with the `with` statement, ensuring proper setup and teardown (like file handling).

Built-in example:
```python
with open('file.txt', 'r') as f:
    content = f.read()
# File automatically closed after block
```

Custom context manager using class:
```python
class Timer:
    def __enter__(self):
        import time
        self.start = time.time()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        print(f"Time elapsed: {time.time() - self.start:.2f}s")

with Timer():
    # Your code here
    pass
```''',
            'difficulty': 'Medium'
        },
        {
            'topic': 'Mutable Default Arguments',
            'question': 'Why is using mutable default arguments in function definitions problematic?',
            'answer': '''This is a common Python gotcha! Mutable objects (lists, dicts) are created once when the function is defined, not each time it's called.

Problematic code:
```python
def add_item(item, items=[]):  # ❌ BAD
    items.append(item)
    return items

print(add_item(1))  # [1]
print(add_item(2))  # [1, 2] - unexpected!
```

Correct approach:
```python
def add_item(item, items=None):  # ✅ GOOD
    if items is None:
        items = []
    items.append(item)
    return items

print(add_item(1))  # [1]
print(add_item(2))  # [2] - correct!
```''',
            'difficulty': 'Medium'
        }
    ]
    
    print('=' * 70)
    print('🐍 DAILY PYTHON INTERVIEW QUESTIONS')
    print('=' * 70)

    for i, q in enumerate(questions, 1):
        print(f'\n{i}. [{q["difficulty"]}] {q["topic"]}')
        print(f'   Question: {q["question"]}')
        print('\n   Answer:')
        for line in q['answer'].split('\n'):
            if line.strip():
                print(f'      {line}')

    print('\n' + '=' * 70)
    print('💡 Tip: Try to answer these yourself before looking at the solutions!')
    print('=' * 70)

if __name__ == '__main__':
    generate_interview_questions()
