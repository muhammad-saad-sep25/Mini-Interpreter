# Custom Interpreter Framework v2.0 - Comprehensive Documentation

Welcome to the official documentation for the **Custom Interpreter Framework**. This project is a feature-complete, recursive-descent interpreter written in Python, designed to demonstrate the core principles of compiler construction: Lexical Analysis, Parsing, and Interpretation.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Language Syntax & Grammar](#2-language-syntax--grammar)
3. [Architecture & Components](#3-architecture--components)
    - [Lexer (Lexical Analysis)](#lexer)
    - [Parser (Syntactic Analysis)](#parser)
    - [Interpreter (Execution)](#interpreter)
4. [Control Flow](#4-control-flow)
    - [Conditional Statements](#conditionals)
    - [Looping Constructs](#loops)
5. [Rich TUI & AST Visualization](#5-rich-tui--ast-visualization)
6. [Usage Guide](#6-usage-guide)
7. [Implementation Details](#7-implementation-details)
8. [Error Handling](#8-error-handling)
9. [Future Roadmap](#9-future-roadmap)

---

## 1. Project Overview
The Custom Interpreter is a lightweight yet powerful scripting environment. It supports:
- **Dynamic Variable Assignment**: State is maintained across the session.
- **Complex Arithmetic**: Full precedence handling with parentheses.
- **Logical Branching**: `if-else` logic for decision making.
- **Iteration**: `while` loops for repetitive tasks.
- **Rich Interaction**: A modern REPL powered by the `rich` library.

---

## 2. Language Syntax & Grammar
The language follows a structured grammar (EBNF-like):

```text
program    : statement*
statement  : assignment | print_stmt | if_stmt | while_stmt | block | empty
assignment : ID '=' expr
print_stmt : 'print' expr
if_stmt    : 'if' expr statement ('else' statement)?
while_stmt : 'while' expr statement
block      : '{' statement* '}'
expr       : arith_expr ((EQ|NE|LT|GT|LE|GE) arith_expr)?
arith_expr : term ((PLUS|MINUS) term)*
term       : factor ((MUL|DIV) factor)*
factor     : (PLUS|MINUS) factor | INTEGER | ID | '(' expr ')'
```

---

## 3. Architecture & Components

### Lexer (`lexer.py`)
The Lexer (or Tokenizer) is the first stage. It scans the raw input string character-by-character and converts them into **Tokens**.
- **Regex-free scanning**: Uses a pointer-based approach for maximum clarity.
- **Keyword Recognition**: Distinguishes between variable names (`ID`) and keywords like `print`, `if`, and `while`.
- **Multi-character Operators**: Correctly peeks ahead to identify `==`, `<=`, etc.

### Parser (`parser.py`)
The Parser takes the stream of tokens and builds an **Abstract Syntax Tree (AST)**.
- **Recursive Descent**: Each grammar rule has a corresponding method.
- **Precedence Climbing**: Ensures `3 + 4 * 2` is evaluated as `3 + (4 * 2)`.
- **AST Nodes**: Every operation (addition, assignment, if-statement) is represented as a Python object.

### Interpreter (`interpreter.py`)
The Interpreter traverses the AST using the **Visitor Pattern**.
- **Visit Methods**: Each node type has a specific logic (e.g., `visit_BinOp` performs math, `visit_Assign` updates memory).
- **Environment**: Uses a simple dictionary to store variable states.

---

## 4. Control Flow

### Conditionals
Conditionals allow the program to branch.
- **Syntax**: `if <condition> <statement> else <statement>`
- **Example**: `if x > 10 print 1 else print 0`
- **Truthiness**: Any non-zero result in the condition is treated as `True`.

### Looping Constructs
Loops allow for repeated execution.
- **Syntax**: `while <condition> <statement>`
- **Example**: `while i < 10 { print i i = i + 1 }`
- **Blocks**: Use `{}` to group multiple statements inside a loop.

---

## 5. Rich TUI & AST Visualization
The `main.py` file implements a modern Terminal User Interface with a powerful diagnostic tool: **Live AST Visualization**.

### Visualizing the Tree
Every time a command is entered, the interpreter doesn't just execute it—it also generates a graphical representation of the **Abstract Syntax Tree (AST)** using the `rich.tree` module.

**Why this is useful:**
- **For Students/Teachers**: It provides physical proof of how the parser structures nested expressions, loops, and conditionals.
- **Debugging**: Easily see if operator precedence is working correctly.
- **Complexity**: Blocks and multi-line structures are clearly visualized with branches and hierarchy.

**Example Visualization:**
Input: `x = (5 + 3) * -2`
```text
Assign to: x
└── Op: *
    ├── Op: +
    │   ├── Num: 5
    │   └── Num: 3
    └── Unary: -
        └── Num: 2
```

---

## 6. Usage Guide

### Arithmetic
```text
>>> (10 + 2) * 3 / 2
18.0
```

### Variables
```text
>>> x = 10
>>> y = x * 2
>>> print y
20
```

### Negative Numbers
```text
>>> z = -5
>>> print z + 10
5
```

### Complex Logic
```text
>>> i = 1
>>> while i <= 5 {
...   if i == 3 print 999 else print i
...   i = i + 1
... }
1
2
999
4
5
```

---

## 7. Implementation Details

### Unary Operators
Unary operators (`+`, `-`) have the highest precedence in `factor`. This allows for nesting: `---5` is valid and results in `-5`.

### Comparisons
Comparison operators return Python Booleans (`True`/`False`). In this language, `True` acts like `1` and `False` acts like `0` in arithmetic contexts.

---

## 8. Error Handling
The framework provides two levels of error reporting:
1. **Lexical Errors**: "Invalid character" if a symbol is not recognized.
2. **Syntax Errors**: "Unexpected token" if the code doesn't follow the grammar (e.g., `if + print`).
3. **Runtime Errors**: Python exceptions (like `ZeroDivisionError`) are caught and printed gracefully in the TUI.

---

## 9. Future Roadmap
- [ ] **Data Types**: Add support for Strings and Lists.
- [ ] **Functions**: Allow users to define reusable blocks of code.
- [ ] **File Execution**: Add the ability to run `.txt` or `.custom` script files.
- [ ] **Standard Library**: Built-in functions like `len()`, `input()`, or `math.sqrt()`.

---
*Generated by Gemini CLI - 2026*
