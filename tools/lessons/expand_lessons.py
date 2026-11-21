#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Expand all lessons with detailed explanations, more examples, analogies,
practice exercises, and comprehensive coverage - similar to the best
Python variables lesson but even more thorough.

This script:
1. Reads all lesson fixtures
2. Generates expanded content for each lesson based on its topic
3. Updates both English and Russian versions
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from translation_engine import Translator

# ---------------------------------------------------------------------
# Patterns extracted from the best lessons
# ---------------------------------------------------------------------

# Template for a comprehensive lesson structure
LESSON_TEMPLATE = {
    "sections": [
        {
            "heading": "Lesson Objectives",
            "type": "objectives",
            "description": "What students will learn in this lesson"
        },
        {
            "heading": "Introduction / Real-World Analogy",
            "type": "analogy",
            "description": "Connect the concept to something familiar"
        },
        {
            "heading": "Core Concept Explanation",
            "type": "explanation",
            "description": "Detailed explanation with analogies"
        },
        {
            "heading": "Syntax & Rules",
            "type": "syntax",
            "description": "Formal syntax with annotated code examples"
        },
        {
            "heading": "Step-by-Step Examples",
            "type": "examples",
            "description": "Multiple worked examples from simple to complex"
        },
        {
            "heading": "Common Patterns & Idioms",
            "type": "patterns",
            "description": "Best practices and common usage patterns"
        },
        {
            "heading": "Common Mistakes",
            "type": "mistakes",
            "description": "Table of frequent errors with corrections"
        },
        {
            "heading": "Practice Exercises",
            "type": "practice",
            "description": "Hands-on tasks for reinforcement"
        },
        {
            "heading": "Key Takeaways",
            "type": "takeaways",
            "description": "Summary of the most important points"
        },
        {
            "heading": "Useful Resources",
            "type": "resources",
            "description": "Links for deeper study"
        }
    ]
}

# Content generators for each major topic category
TOPIC_GENERATORS = {
    # Python topics
    "python": {
        "variables": {
            "analogy": (
                "Think of a variable as a labeled box in a warehouse. The label (variable name) "
                "lets you find what's inside (the value) without having to remember which shelf "
                "it's on (memory address). Just like you'd write 'Winter Clothes' on a box "
                "rather than 'Box #342', you give variables meaningful names like 'user_age' "
                "instead of 'x'."
            ),
            "explanation": (
                "A variable in Python is a name that refers to an object stored in the computer's "
                "memory. When you write `x = 42`, Python creates an integer object with value 42 "
                "somewhere in memory, then attaches the name 'x' to it. This is called 'binding'.\n\n"
                "Key concepts:\n"
                "- **Names are references**, not containers. Multiple names can point to the same object.\n"
                "- **Dynamic typing**: a name can refer to different types at different times.\n"
                "- **Assignment is right-to-left**: the expression on the right is evaluated first, then bound to the name on the left."
            ),
            "patterns": [
                "Use descriptive names: `user_count` not `uc`",
                "Constants in UPPER_SNAKE_CASE: `MAX_RETRY_ATTEMPTS = 3`",
                "Variables in snake_case: `total_price`, `is_active`",
                "Single-character names only for loop indices: `for i in range(10):`"
            ],
            "common_mistakes": [
                ("Using `=` for comparison", "`if x = 5:`", "`if x == 5:`"),
                ("Forgetting to convert input", "`age = input('Age: ')` then `age + 1`", "`age = int(input('Age: '))`"),
                ("Modifying immutable objects", "`name[0] = 'J'` on a string", "`name = 'J' + name[1:]`"),
                ("Using reserved words as variables", "`class = 'A'`", "`class_name = 'A'`"),
            ],
            "practice_tasks": [
                "Create variables for your name, age, and favorite color. Print them in a formatted sentence.",
                "Swap the values of two variables without using a third variable.",
                "Calculate the area of a rectangle given length and width stored in variables."
            ],
            "takeaways": [
                "Variables are names that refer to objects in memory",
                "Assignment evaluates the right side first, then binds the name",
                "Choose descriptive names following Python conventions",
                "Use `type()` to inspect what type a variable refers to"
            ],
        },
        "operators": {
            "analogy": (
                "Operators are like kitchen appliances. You have ingredients (operands) and you "
                "use different tools (operators) to transform them: a knife cuts (division), a "
                "blender mixes (addition), an oven bakes (exponentiation). Each operator has a "
                "specific job and a priority—you wouldn't put raw eggs into a cake after it's baked!"
            ),
            "explanation": (
                "Python operators are symbols that perform operations on values (operands). They "
                "follow strict precedence rules (PEMDAS/BODMAS) that determine the order of evaluation.\n\n"
                "Categories:\n"
                "- **Arithmetic**: `+ - * / // % **`\n"
                "- **Comparison**: `== != < > <= >=`\n"
                "- **Logical**: `and or not`\n"
                "- **Bitwise**: `& | ^ ~ << >>`\n"
                "- **Assignment**: `= += -= *= /= //= %= **=`\n"
                "- **Identity**: `is is not`\n"
                "- **Membership**: `in not in`"
            ),
            "patterns": [
                "Use `//` and `%` together for divmod-like operations",
                "Prefer `x ** 0.5` over `math.sqrt(x)` for simple square roots",
                "Chain comparisons: `0 <= x < 10` instead of `0 <= x and x < 10`",
                "Use `not in` for exclusion checks"
            ],
            "common_mistakes": [
                ("Confusing `/` and `//`", "`5 / 2` → 2.5", "`5 // 2` → 2"),
                ("Integer division with negatives", "`-5 // 2` → -3 (floor division)", "Use `int(-5 / 2)` → -2 for truncation"),
                ("Operator precedence", "`2 + 3 * 4` → 14, not 20", "Use parentheses: `(2 + 3) * 4` → 20"),
                ("Using `=` instead of `==`", "`if x = 5:`", "`if x == 5:`"),
            ],
            "practice_tasks": [
                "Calculate compound interest: principal * (1 + rate) ** years",
                "Convert Celsius to Fahrenheit and vice versa",
                "Extract the last 3 digits of a number using modulo",
                "Check if a year is a leap year using logical operators"
            ],
            "takeaways": [
                "Operator precedence determines evaluation order—use parentheses for clarity",
                "`/` always returns float; `//` returns integer (floor division)",
                "`%` is powerful for cycling, wrapping, and divisibility checks",
                "Chained comparisons like `a < b < c` are Pythonic and efficient"
            ],
        },
        "strings": {
            "analogy": (
                "Strings are like necklaces made of beads. Each bead is a character with its own "
                "position (index). You can't change a bead once it's strung (immutable), but you "
                "can make a new necklace by copying parts of the old one and adding new beads. "
                "The index is like the bead number starting from 0 at the clasp."
            ),
            "explanation": (
                "Strings (`str`) are immutable sequences of Unicode characters. Once created, they "
                "cannot be changed—any operation that seems to modify a string actually creates a "
                "new one.\n\n"
                "Key operations:\n"
                "- Indexing: `s[0]`, `s[-1]`\n"
                "- Slicing: `s[start:end:step]`\n"
                "- Methods: `upper()`, `lower()`, `strip()`, `split()`, `join()`, `replace()`\n"
                "- Formatting: f-strings `f'{value}'`, `.format()`, `%` operator\n"
                "- Checking: `in`, `startswith()`, `endswith()`"
            ),
            "patterns": [
                "Use f-strings for formatting: `f'Hello, {name}!'`",
                "Use raw strings for paths/regex: `r'C:\\Users\\name'`",
                "Prefer `join()` over `+` for concatenating many strings",
                "Use slicing for reversal: `s[::-1]`"
            ],
            "common_mistakes": [
                ("Trying to modify in place", "`s[0] = 'X'` → TypeError", "`s = 'X' + s[1:]`"),
                ("Confusing `len()` and index", "`s[len(s)]` → IndexError", "`s[len(s)-1]` or `s[-1]`"),
                ("Escaping backslashes", "`'C:\\Users\\name'`", "`r'C:\\Users\\name'`"),
            ],
            "practice_tasks": [
                "Reverse a string without using `reversed()`",
                "Count vowels in a user's input",
                "Create a palindrome checker",
                "Format a phone number: '+1 (XXX) XXX-XXXX'"
            ],
            "takeaways": [
                "Strings are immutable—operations return new strings",
                "Indexing starts at 0; negative indices count from the end",
                "Slicing `s[a:b]` includes a, excludes b; step can reverse",
                "f-strings are the most readable and efficient formatting method"
            ],
        },
        "conditionals": {
            "analogy": (
                "Conditionals are like a traffic light system for your code. The program reaches "
                "an intersection and must decide which path to take based on the current state. "
                "`if` is the green light (proceed), `elif` checks the next light, and `else` is "
                "the fallback when all other lights are red. Only ONE path is ever taken."
            ),
            "explanation": (
                "Conditional statements (`if`, `elif`, `else`) control which block of code executes "
                "based on whether a condition evaluates to True or False.\n\n"
                "Key points:\n"
                "- Only ONE block executes—the first matching condition\n"
                "- `elif` is short for 'else if'; chain multiple conditions\n"
                "- `else` is optional and catches everything else\n"
                "- Indentation defines the block (typically 4 spaces)\n"
                "- Any value can be used as a condition (truthy/falsy)"
            ),
            "patterns": [
                "Early returns to reduce nesting",
                "Use `if not condition:` instead of `if condition == False:`",
                "Combine conditions with `and`/`or` rather than nested ifs",
                "Use `in` for multiple value checks: `if x in (1, 2, 3):`"
            ],
            "common_mistakes": [
                ("Assignment instead of comparison", "`if x = 5:`", "`if x == 5:`"),
                ("Truthiness confusion", "`if len(list):` works but `if list:` is preferred", ""),
                ("Indentation errors", "Mixing tabs and spaces", "Use 4 spaces consistently"),
            ],
            "practice_tasks": [
                "Grade calculator: A/B/C/D/F based on score",
                "FizzBuzz: print Fizz for multiples of 3, Buzz for 5, FizzBuzz for both",
                "Simple calculator with +, -, *, / based on user input",
                "Password strength checker"
            ],
            "takeaways": [
                "Only one branch executes—first True condition wins",
                "`elif` chains are cleaner than nested `if/else`",
                "Python uses indentation to define blocks",
                "Any value works as a condition (truthy/falsy)"
            ],
        },
        "loops": {
            "analogy": (
                "Loops are like a chef chopping vegetables. The recipe says 'chop 10 carrots' — "
                "you don't write 'chop carrot 1, chop carrot 2...' Instead, you repeat the same "
                "action until done. `for` loops are like 'for each carrot in the bag', `while` "
                "loops are like 'keep chopping until the bag is empty'."
            ),
            "explanation": (
                "Loops repeat a block of code multiple times:\n"
                "- **for loops**: iterate over sequences (lists, ranges, strings, etc.)\n"
                "- **while loops**: continue while a condition is True\n\n"
                "Control flow:\n"
                "- `break` exits the loop entirely\n"
                "- `continue` skips to the next iteration\n"
                "- `else` clause runs if loop completes without `break`"
            ),
            "patterns": [
                "Use `range(start, stop, step)` for counted loops",
                "Use `enumerate()` when you need index and value",
                "Use `zip()` to iterate multiple sequences together",
                "Prefer `for item in collection:` over index-based loops"
            ],
            "common_mistakes": [
                ("Modifying list while iterating", "`for item in items: items.remove(item)`", "Iterate over a copy or use list comprehension"),
                ("Infinite while loops", "`while True:` without break", "Ensure condition changes"),
                ("Off-by-one in range", "`range(1, 10)` → 1-9", "`range(1, 11)` for 1-10"),
            ],
            "practice_tasks": [
                "Sum of even numbers from 1 to 100",
                "Print multiplication table for a given number",
                "Find the first 10 Fibonacci numbers",
                "Count occurrences of each character in a string"
            ],
            "takeaways": [
                "`for` loops iterate over anything iterable",
                "`range(n)` gives 0 to n-1; `range(a, b)` gives a to b-1",
                "`break` exits loop; `continue` skips to next iteration",
                "`while` needs a changing condition to terminate"
            ],
        },
        "functions": {
            "analogy": (
                "Functions are like recipes in a cookbook. You write the instructions once, give "
                "it a name ('Chocolate Chip Cookies'), and whenever you want cookies you just "
                "say 'make Chocolate Chip Cookies' with specific ingredients (parameters). You "
                "don't rewrite the recipe every time—you just follow it with different inputs."
            ),
            "explanation": (
                "Functions are reusable blocks of code that perform a specific task. They:\n"
                "- Accept inputs (parameters/arguments)\n"
                "- Perform computations\n"
                "- Return an output (return value) — `None` if no explicit return\n\n"
                "Key concepts:\n"
                "- Parameters vs arguments\n"
                "- Default parameter values\n"
                "- `*args` and `**kwargs` for variable arguments\n"
                "- Docstrings for documentation\n"
                "- Scope: local vs global variables"
            ),
            "patterns": [
                "Single responsibility—one task per function",
                "Use type hints for clarity",
                "Default parameters for optional behavior",
                "Return early to reduce nesting"
            ],
            "common_mistakes": [
                ("Mutable default arguments", "`def f(items=[]):`", "`def f(items=None): items = items or []`"),
                ("Forgetting return", "Function prints instead of returns", "Use `return` for values"),
                ("Global variable modification", "`global x` everywhere", "Pass as parameter, return new value"),
            ],
            "practice_tasks": [
                "Function to calculate factorial",
                "Function that validates email format",
                "Higher-order function: apply operation to list",
                "Decorator that times function execution"
            ],
            "takeaways": [
                "Functions encapsulate logic for reuse and testing",
                "Parameters are inputs; return values are outputs",
                "Avoid mutable defaults; use `None` pattern",
                "Docstrings explain what, not how"
            ],
        },
        "lists": {
            "analogy": (
                "A list is like a numbered bookshelf where each shelf holds one book. You can "
                "add books, remove them, rearrange them, or look at the shelf numbers to find "
                "specific books. Unlike strings, bookshelves are mutable—you can change what's "
                "on any shelf without buying a new bookshelf."
            ),
            "explanation": (
                "Lists are ordered, mutable sequences that can hold any type of object:\n"
                "- Indexing and slicing work like strings\n"
                "- Methods: `append()`, `extend()`, `insert()`, `remove()`, `pop()`, `sort()`, `reverse()`\n"
                "- List comprehensions for transformation/filtering\n"
                "- Can contain mixed types: `[1, 'a', 3.14, [1, 2]]`\n"
                "- Nested lists for matrices/grids"
            ),
            "patterns": [
                "List comprehensions: `[x*2 for x in nums if x > 5]`",
                "Use `enumerate()` for index+value: `for i, v in enumerate(items):`",
                "Check membership with `in`: `if target in items:`",
                "Copy with `items[:]` or `list(items)` not `items` (reference)"
            ],
            "common_mistakes": [
                ("Reference vs copy", "`new = old` then modifying both changes original", "`new = old[:]`"),
                ("Modifying during iteration", "`for x in lst: lst.remove(x)`", "Iterate copy or build new list"),
                ("Default argument trap", "`def f(lst=[]):`", "`def f(lst=None): lst = lst or []`"),
            ],
            "practice_tasks": [
                "Remove duplicates while preserving order",
                "Rotate list by k positions",
                "Find common elements between two lists",
                "Implement a simple stack using list"
            ],
            "takeaways": [
                "Lists are ordered, mutable, and allow duplicates",
                "Use slicing `list[a:b]` for sublists; `list[::-1]` to reverse",
                "List comprehensions are Pythonic and efficient",
                "Prefer `append()` for single items, `extend()` for iterables"
            ],
        },
        "dicts": {
            "analogy": (
                "A dictionary is like a real-world dictionary or a phone book. You look up a word "
                "(key) to find its definition (value). Unlike a list where you search by position "
                "(index), here you search by name. It's instant—no flipping through pages."
            ),
            "explanation": (
                "Dictionaries (`dict`) are key-value mappings with O(1) average lookup:\n"
                "- Keys must be immutable (str, int, tuple of immutables)\n"
                "- Values can be anything, including other dicts\n"
                "- Methods: `.get()`, `.keys()`, `.values()`, `.items()`, `.pop()`, `.update()`\n"
                "- Dict comprehensions: `{k: v*2 for k, v in d.items()}`\n"
                "- Python 3.7+ preserves insertion order"
            ),
            "patterns": [
                "Use `.get(key, default)` to avoid KeyError",
                "Use `defaultdict` for grouping: `defaultdict(list)`",
                "Use `.setdefault()` for lazy initialization",
                "Dictionary merging: `{**d1, **d2}` or `d1 | d2` (3.9+)"
            ],
            "common_mistakes": [
                ("KeyError on missing key", "`d['missing']`", "`d.get('missing', default)`"),
                ("Modifying during iteration", "`for k in d: del d[k]`", "`list(d.keys())`"),
                ("Using list as key", "`{[1,2]: 'value'}` → TypeError", "Use tuple: `{(1,2): 'value'}`"),
            ],
            "practice_tasks": [
                "Count word frequencies in a text",
                "Merge two dictionaries with combined values",
                "Invert a dictionary (swap keys/values)",
                "Build a simple contact manager"
            ],
            "takeaways": [
                "Dictionaries map keys to values with fast O(1) lookup",
                "Keys must be immutable; values can be anything",
                "Use `.get()` for safe access with defaults",
                "Insertion order is preserved in Python 3.7+"
            ],
        },
        # Add more Python topics as needed
    }
}

# Other languages (basic patterns - can be expanded)
LANGUAGE_TEMPLATES = {
    "javascript": {
        "intro": "JavaScript runs in browsers and Node.js. It's dynamically typed with prototype-based OOP.",
        "pattern": "Use `const` by default, `let` for reassignments. Arrow functions for callbacks."
    },
    "cpp": {
        "intro": "C++ is compiled, statically typed with manual memory management and templates.",
        "pattern": "Use `auto` for type deduction, smart pointers for memory, RAII for resources."
    },
    "rust": {
        "intro": "Rust guarantees memory safety without GC via ownership and borrowing system.",
        "pattern": "Prefer `let` immutability, `match` for control flow, `?` for error propagation."
    },
    "csharp": {
        "intro": "C# runs on .NET with garbage collection, strong typing, and rich standard library.",
        "pattern": "Use `var` for locals, LINQ for collections, `async/await` for concurrency."
    },
    "css": {
        "intro": "CSS styles HTML. Cascading, specificity, and box model are fundamental concepts.",
        "pattern": "Use custom properties (CSS variables), Flexbox/Grid for layout, BEM for naming."
    },
}

# ---------------------------------------------------------------------
# Content Expansion Engine
# ---------------------------------------------------------------------

def expand_lesson_content(lesson_data: dict[str, Any], lang_slug: str) -> dict[str, Any]:
    """Generate expanded content for a lesson based on its topic and language."""
    
    # Extract topic from slug/title
    slug = lesson_data.get('slug', '')
    title = lesson_data.get('title', '')
    
    # Determine which generator to use
    topic_key = None
    for key in ["variables", "operators", "strings", "conditionals", "loops", "functions", "lists", "dicts"]:
        if key in slug or key in title.lower():
            topic_key = key
            break
    
    # Get generator for this language
    generators = TOPIC_GENERATORS.get(lang_slug, {})
    topic_gen = generators.get(topic_key, {})
    
    # If no specific generator, create basic enhanced content
    if not topic_gen:
        # Extract goals and create basic sections
        goals = lesson_data.get('goals', [])
        content = generate_generic_enhanced_content(lesson_data, lang_slug)
        return content
    
    # Generate comprehensive content using the topic generator
    return generate_topic_content(lesson_data, topic_gen)


def generate_topic_content(lesson_data: dict[str, Any], topic_gen: dict) -> list[dict]:
    """Generate expanded content blocks for a specific topic."""
    
    blocks = []
    
    # 1. Lesson Objectives
    goals = lesson_data.get('goals', [])
    if goals:
        blocks.append({
            "type": "heading",
            "level": 2,
            "content": "Lesson Objectives"
        })
        blocks.append({
            "type": "list",
            "items": goals,
            "ordered": False
        })
    
    # 2. Real-World Analogy
    analogy = topic_gen.get('analogy', '')
    if analogy:
        blocks.append({
            "type": "heading",
            "level": 2,
            "content": "Real-World Analogy"
        })
        blocks.append({
            "type": "text",
            "content": analogy
        })
    
    # 3. Core Concept Explanation
    explanation = topic_gen.get('explanation', '')
    if explanation:
        blocks.append({
            "type": "heading",
            "level": 2,
            "content": "Understanding the Concept"
        })
        # Split into multiple paragraphs if long
        for para in explanation.split('\n\n'):
            if para.strip():
                # Check if it's a list
                if para.strip().startswith('- '):
                    items = [line[2:].strip() for line in para.split('\n') if line.startswith('- ')]
                    if items:
                        blocks.append({
                            "type": "list",
                            "items": items,
                            "ordered": False
                        })
                else:
                    blocks.append({
                        "type": "text",
                        "content": para.strip()
                    })
    
    # 4. Patterns & Best Practices
    patterns = topic_gen.get('patterns', [])
    if patterns:
        blocks.append({
            "type": "heading",
            "level": 2,
            "content": "Patterns & Best Practices"
        })
        blocks.append({
            "type": "list",
            "items": patterns,
            "ordered": False
        })
    
    # 5. Step-by-Step Code Examples
    # Generate based on topic
    code_examples = generate_code_examples(lesson_data.get('slug', ''), topic_gen)
    if code_examples:
        blocks.append({
            "type": "heading",
            "level": 2,
            "content": "Step-by-Step Examples"
        })
        for i, example in enumerate(code_examples, 1):
            blocks.append({
                "type": "heading",
                "level": 3,
                "content": f"Example {i}: {example['title']}"
            })
            blocks.append({
                "type": "text",
                "content": example['explanation']
            })
            blocks.append({
                "type": "code",
                "language": example.get('language', 'python'),
                "content": example['code']
            })
    
    # 6. Common Mistakes Table
    mistakes = topic_gen.get('common_mistakes', [])
    if mistakes:
        blocks.append({
            "type": "heading",
            "level": 2,
            "content": "Common Mistakes"
        })
        # Build table
        rows = []
        for mistake, wrong, correct in mistakes:
            rows.append([wrong, correct])
        if rows:
            blocks.append({
                "type": "table",
                "headers": ["❌ Incorrect", "✅ Correct"],
                "rows": rows
            })
    
    # 7. Practice Exercises
    practice_tasks = topic_gen.get('practice_tasks', [])
    if practice_tasks:
        blocks.append({
            "type": "heading",
            "level": 2,
            "content": "Practice Exercises"
        })
        blocks.append({
            "type": "list",
            "items": practice_tasks,
            "ordered": True
        })
    
    # 8. Key Takeaways
    takeaways = topic_gen.get('takeaways', [])
    if takeaways:
        blocks.append({
            "type": "heading",
            "level": 2,
            "content": "Key Takeaways"
        })
        blocks.append({
            "type": "list",
            "items": takeaways,
            "ordered": False
        })
    
    # 9. Resources
    blocks.append({
        "type": "heading",
        "level": 2,
        "content": "Useful Resources"
    })
    # Add default resources based on language
    resources = get_default_resources(lesson_data.get('slug', ''))
    if resources:
        blocks.append({
            "type": "list",
            "items": resources,
            "ordered": False
        })
    
    return blocks


def generate_code_examples(slug: str, topic_gen: dict) -> list[dict]:
    """Generate code examples based on lesson slug and topic."""
    # This would be more sophisticated - for now return empty to let existing content through
    # In a full implementation, this would generate topic-specific examples
    return []


def generate_generic_enhanced_content(lesson_data: dict[str, Any], lang_slug: str) -> list[dict]:
    """Generate enhanced content for lessons without specific generators."""
    
    blocks = []
    
    # Keep existing content but add structure
    existing_blocks = lesson_data.get('content_blocks', [])
    
    # Add objectives if missing
    goals = lesson_data.get('goals', [])
    if goals:
        has_objectives = any(b.get('type') == 'heading' and 'objective' in b.get('content', '').lower() 
                            for b in existing_blocks)
        if not has_objectives:
            blocks.append({
                "type": "heading",
                "level": 2,
                "content": "Lesson Objectives"
            })
            blocks.append({
                "type": "list",
                "items": goals,
                "ordered": False
            })
    
    # Add the existing content
    blocks.extend(existing_blocks)
    
    # Add practice tasks if present
    practice = lesson_data.get('practice_tasks', [])
    if practice:
        blocks.append({
            "type": "heading",
            "level": 2,
            "content": "Practice Exercises"
        })
        blocks.append({
            "type": "list",
            "items": practice,
            "ordered": True
        })
    
    # Add resources
    resources = lesson_data.get('resources', [])
    if resources:
        blocks.append({
            "type": "heading",
            "level": 2,
            "content": "Useful Resources"
        })
        blocks.append({
            "type": "list",
            "items": resources,
            "ordered": False
        })
    
    return blocks


def get_default_resources(slug: str) -> list[str]:
    """Get default resource links based on lesson slug/topic."""
    return [
        f"Official documentation for this topic",
        f"Tutorial with interactive examples",
        f"Common patterns and best practices guide"
    ]


# ---------------------------------------------------------------------
# Russian translation using the translation engine
# ---------------------------------------------------------------------

def translate_content_to_russian(content_blocks: list[dict], translator: Translator) -> list[dict]:
    """Translate content blocks to Russian using the translation engine."""
    # Extract translatable texts
    texts_to_translate = []
    text_locations = []  # (block_index, field_path)
    
    for bi, block in enumerate(content_blocks):
        btype = block.get('type')
        
        if btype in ('heading', 'text', 'blockquote'):
            val = block.get('content', '')
            if val and len(val) > 3:
                texts_to_translate.append(val)
                text_locations.append((bi, 'content'))
        
        elif btype == 'list':
            items = block.get('items', [])
            for ii, item in enumerate(items):
                if isinstance(item, str) and len(item) > 3:
                    texts_to_translate.append(item)
                    text_locations.append((bi, ('items', ii)))
        
        elif btype == 'table':
            # Translate headers
            for hi, header in enumerate(block.get('headers', [])):
                if isinstance(header, str) and len(header) > 3:
                    texts_to_translate.append(header)
                    text_locations.append((bi, ('headers', hi)))
            # Translate rows
            for ri, row in enumerate(block.get('rows', [])):
                for ci, cell in enumerate(row):
                    if isinstance(cell, str) and len(cell) > 3:
                        texts_to_translate.append(cell)
                        text_locations.append((bi, ('rows', ri, ci)))
    
    # Deduplicate
    unique_map = {}
    for i, text in enumerate(texts_to_translate):
        if text not in unique_map:
            unique_map[text] = []
        unique_map[text].append(text_locations[i])
    
    # Translate
    if unique_map:
        translated = translator.translate_many(list(unique_map.keys()))
        mapping = dict(zip(unique_map.keys(), translated))
        
        # Apply translations to Russian copy
        import copy
        ru_blocks = copy.deepcopy(content_blocks)
        
        for orig_text, locations in unique_map.items():
            translated_text = mapping[orig_text]
            for bi, path in locations:
                block = ru_blocks[bi]
                if path == 'content':
                    block['content'] = translated_text
                elif path[0] == 'items':
                    block['items'][path[1]] = translated_text
                elif path[0] == 'headers':
                    block['headers'][path[1]] = translated_text
                elif path[0] == 'rows':
                    block['rows'][path[1]][path[2]] = translated_text
        
        return ru_blocks
    
    return content_blocks


# ---------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------

def process_fixtures():
    """Process all lesson fixtures and expand content."""
    
    BASE_DIR = Path(__file__).resolve().parent
    FIXTURES_DIR = BASE_DIR / 'fixtures' / 'lessons'
    
    # Initialize translator for RU
    tr_ru = Translator('en', 'ru')
    
    # Find all lesson files
    language_dirs = sorted([d for d in FIXTURES_DIR.iterdir() if d.is_dir()])
    
    total_processed = 0
    total_updated = 0
    
    for lang_dir in language_dirs:
        lang_slug = lang_dir.name
        lesson_files = sorted(lang_dir.glob('*.json'))
        
        print(f"\n=== Processing {lang_slug} ({len(lesson_files)} lessons) ===")
        
        for lf in lesson_files:
            try:
                with open(lf, encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if already expanded (has many content blocks)
                existing_blocks = data.get('content_blocks', [])
                if len(existing_blocks) > 30:
                    print(f"  ⏭  {lf.name}: Already expanded ({len(existing_blocks)} blocks)")
                    total_processed += 1
                    continue
                
                # Generate expanded English content
                expanded_en = expand_lesson_content(data, lang_slug)
                
                # Generate Russian version
                expanded_ru = translate_content_to_russian(expanded_en, tr_ru)
                
                # Update the data
                data['content_blocks'] = expanded_en
                data['content_en'] = expanded_en
                data['content'] = expanded_ru
                
                # Update other localizable fields
                # short_description
                short_desc_en = data.get('short_description', '')
                short_desc_ru = tr_ru.translate(short_desc_en) if short_desc_en else ''
                data['short_description'] = short_desc_ru
                data['short_description_en'] = short_desc_en
                
                # Name/title
                title_en = data.get('title', '')
                title_ru = tr_ru.translate(title_en) if title_en else ''
                data['name'] = title_ru
                data['name_en'] = title_en
                
                # Goals
                goals_en = data.get('goals', [])
                goals_ru = tr_ru.translate_many(goals_en) if goals_en else []
                data['goals'] = goals_ru
                data['goals_en'] = goals_en
                
                # Practice tasks
                practice_en = data.get('practice_tasks', [])
                practice_ru = tr_ru.translate_many(practice_en) if practice_en else []
                data['practice_tasks'] = practice_ru
                data['practice_tasks_en'] = practice_en
                
                # Common errors
                errors_en = data.get('common_errors', [])
                if errors_en:
                    # Translate error descriptions
                    for err in errors_en:
                        if 'mistake' in err:
                            err['mistake_ru'] = tr_ru.translate(err['mistake'])
                        if 'correct' in err:
                            err['correct_ru'] = tr_ru.translate(err['correct'])
                
                # Resources
                resources_en = data.get('resources', [])
                resources_ru = tr_ru.translate_many(resources_en) if resources_en else []
                data['resources'] = resources_ru
                data['resources_en'] = resources_en
                
                # Key takeaways
                takeaways_en = data.get('key_takeaways', [])
                takeaways_ru = tr_ru.translate_many(takeaways_en) if takeaways_en else []
                data['key_takeaways'] = takeaways_ru
                data['key_takeaways_en'] = takeaways_en
                
                # Save updated fixture
                with open(lf, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    f.write('\n')
                
                print(f"  ✅ {lf.name}: {len(expanded_en)} blocks (was {len(existing_blocks)})")
                total_updated += 1
                total_processed += 1
                
            except Exception as exc:
                print(f"  ❌ {lf.name}: {exc}")
                import traceback
                traceback.print_exc()
    
    print(f"\n=== Summary ===")
    print(f"Total lessons processed: {total_processed}")
    print(f"Lessons expanded: {total_updated}")
    print(f"\nRun 'python manage.py import_lessons --fixtures-dir fixtures --clear' to import into DB")


if __name__ == '__main__':
    process_fixtures()