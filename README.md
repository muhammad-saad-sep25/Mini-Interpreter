# Custom Interpreter Framework v2.0 - Comprehensive Documentation

Welcome to the official documentation for the **Custom Interpreter Framework**. This project is a feature-complete, recursive-descent interpreter written in Python, designed to demonstrate the core principles of compiler construction: Lexical Analysis, Parsing, Intermediate Code Generation, and Interpretation.

---

## 1. Project Overview
The Custom Interpreter is a lightweight yet powerful scripting environment. It supports:
- **Dynamic Variable Assignment**: State is maintained across the session.
- **Complex Arithmetic**: Full precedence handling with parentheses.
- **Relational & Logical Branching**: `if-else` logic powered by comparisons (`<`, `==`) and boolean operators (`and`, `or`, `not`).
- **Iteration**: `while` loops for repetitive tasks.
- **Multi-Stage Output Pipeline**: Every evaluated command is shown at three levels of abstraction — the high-level **AST**, a stack-based pseudo-bytecode **Intermediate Code ("LLL")**, and a raw **Binary (ASCII bit)** encoding of that bytecode.
- **Rich Interaction**: A modern REPL powered by the `rich` library with live AST, intermediate code, and binary visualization.

---

## 2. Language Syntax & Grammar
The language follows a strict, precedence-based grammar (EBNF-like) to ensure operations are evaluated in the correct mathematical and logical order:

    program     : statement*
    statement   : assignment | print_stmt | if_stmt | while_stmt | block | empty
    assignment  : ID '=' expr
    print_stmt  : 'print' expr
    if_stmt     : 'if' expr statement ('else' statement)?
    while_stmt  : 'while' expr statement
    block       : '{' statement* '}'

    expr        : logical_and ('or' logical_and)*
    logical_and : logical_not ('and' logical_not)*
    logical_not : 'not' logical_not | comparison
    comparison  : arith_expr ((EQ|NE|LT|GT|LE|GE) arith_expr)?
    arith_expr  : term ((PLUS|MINUS) term)*
    term        : factor ((MUL|DIV) factor)*
    factor      : (PLUS|MINUS) factor | INTEGER | ID | '(' expr ')'

---

## 3. Architecture & Components

### Lexer (`lexer.py`)
The Lexer (or Tokenizer) scans the raw input string character-by-character and converts them into **Tokens**.
- **Regex-free scanning**: Uses a pointer-based approach for maximum clarity.
- **Keyword Recognition**: Distinguishes between variable names (`ID`) and reserved keywords (`print`, `if`, `while`, `and`, `or`, `not`).
- **Multi-character Operators**: Correctly peeks ahead to identify `==`, `<=`, `!=`, etc.

### Parser (`parser.py`)
The Parser takes the stream of tokens and builds an **Abstract Syntax Tree (AST)**.
- **Recursive Descent**: Each grammar rule has a corresponding method, building nodes sequentially.
- **Precedence Climbing**: Ensures operations like `not x and y` or `3 + 4 * 2` are nested correctly in the tree.
- **AST Nodes**: Every operation is represented as a distinct Python object (`BinOp`, `UnaryOp`, `If`, `While`).
- **Self-Compiling Nodes**: Every AST node class also implements a `to_lll()` method. This lets each node recursively "compile" itself (and its children) down into a flat, linear, stack-based pseudo-bytecode sequence — the same way `visit_*` lets the Interpreter "execute" itself. See Section 6 for details.

### Interpreter (`interpreter.py`)
The Interpreter traverses the AST using the **Visitor Pattern**.
- **Visit Methods**: Each node type has a specific execution logic (e.g., `visit_BinOp` performs math, `visit_Assign` updates memory).
- **Environment State**: Uses a memory dictionary to store and retrieve variable values during runtime.

---

## 4. Control Flow

### Conditionals
Conditionals allow the program to branch based on truthy evaluations.
- **Syntax**: `if <condition> <statement> else <statement>`
- **Example**: `if x > 10 and not y == 0 { print 1 } else { print 0 }`

### Looping Constructs
Loops allow for repeated execution of blocks.
- **Syntax**: `while <condition> <statement>`
- **Blocks**: Use `{}` to group multiple statements inside a loop.

---

## 5. Rich TUI & Multi-Stage Visualization
For every command entered into the REPL, the TUI walks the **full pipeline** end-to-end and renders each stage before executing the program:

1. **AST Visualization** — a graphical tree of the parsed program using the `rich.tree` module.
2. **LLL (Intermediate Code)** — the linear pseudo-bytecode produced by calling `to_lll()` on the root AST node (see Section 6).
3. **Bits (Binary Representation)** — the LLL text re-encoded as raw 8-bit binary, one group per character (see Section 7).
4. **Execution** — only after all three are displayed does the Interpreter actually `visit()` the tree and run the program.

**Why this is vital for evaluation:**
- It provides physical proof of how the parser structures nested expressions.
- It immediately exposes if operator precedence (like PEMDAS or Logical hierarchy) is functioning correctly.
- Multi-line blocks and scope hierarchies are clearly mapped.
- It demonstrates, step by step, how a single line of source code is progressively lowered from a tree, to a flat instruction sequence, to raw bits — mirroring the stages of a real compiler/interpreter pipeline.

---

## 6. Intermediate Code Generation (LLL)
"LLL" (Low-Level Language) is a small, stack-based pseudo-bytecode that the framework generates from the AST before interpretation. It is **not executed** — the tree-walking Interpreter still does the actual work — but it is generated purely to give a transparent, textbook view of what a real compiler's intermediate representation might look like.

Each AST node implements its own `to_lll()` method, recursively emitting instructions for its children first (postfix/stack order) and then its own operation:

| Opcode | Meaning |
|---|---|
| `PUSH <n>` | Push the integer literal `n` onto the stack |
| `LOAD <name>` | Push the current value of variable `name` |
| `STORE <name>` | Pop the top of the stack into variable `name` |
| `PRINT` | Pop and print the top of the stack |
| `PLUS` / `MINUS` / `MUL` / `DIV` | Pop two operands, push the arithmetic result |
| `EQ` / `NE` / `LT` / `GT` / `LE` / `GE` | Pop two operands, push the comparison result |
| `AND` / `OR` | Pop two operands, push the logical result |
| `NOT` | Pop one operand, push its logical negation |
| `JZ <label>` | Pop a condition; if it is falsy, jump to `<label>` |
| `JMP <label>` | Unconditionally jump to `<label>` |
| `L<n>:` | A label/jump target (auto-numbered per `if`/`while` encountered) |

### Worked Example
Source:

    >>> result = 10 + 2 * 3 - 4 / 2

Generated LLL:

    PUSH 10
    PUSH 2
    PUSH 3
    MUL
    PLUS
    PUSH 4
    PUSH 2
    DIV
    MINUS
    STORE result

Note how `2 * 3` and `4 / 2` are emitted (and would be "executed" on a stack machine) *before* the surrounding `+`/`-`, which is exactly the precedence the parser already enforced when it built the tree.

### Control Flow Example
Source:

    >>> if a < b { print 1 } else { print 0 }

Generated LLL:

    LOAD a
    LOAD b
    LT
    JZ L1
    PUSH 1
    PRINT
    JMP L2
    L1:
    PUSH 0
    PRINT
    L2:

`while` loops follow the same pattern, but wrap the condition and body between a start label and a backward `JMP`:

    >>> while count <= 3 { print count  count = count + 1 }

    L1:
    LOAD count
    PUSH 3
    LE
    JZ L2
    LOAD count
    PRINT
    LOAD count
    PUSH 1
    PLUS
    STORE count
    JMP L1
    L2:

---

## 7. Binary Representation
As a final, purely illustrative step, the TUI takes the entire LLL text generated above and re-encodes it as **raw binary**: every single character of the LLL string (letters, digits, spaces, and newlines alike) is converted to its 8-bit ASCII binary code via `format(ord(c), '08b')`, and the groups are joined with spaces.

This is **not** a real compiled bytecode or executable binary format — it's a one-to-one bit-level encoding of the *text* of the intermediate code, included purely to make the abstraction chain (source → AST → intermediate code → bits) tangible for evaluation purposes.

For the `result = 10 + 2 * 3 - 4 / 2` example above, the first few bytes look like this:

    01010000 01010101 01010011 01001000 00100000 00110001 00110000 00001010 ...
    (P)      (U)      (S)      (H)      ( )      (1)      (0)      (\n)     ...

---

## 8. Comprehensive Evaluation Test Cases
The following examples represent all major combinations of logic, precedence, and control flow that the interpreter can handle. These can be copied directly into the TUI. Each one will also produce its own AST, LLL, and Bits output as described in Sections 5–7.

### Test Case 1: Mathematical Precedence
Proves that multiplication and division are evaluated before addition and subtraction, and that parentheses override default precedence.

    >>> result = 10 + 2 * 3 - 4 / 2
    >>> print result
    14.0

    >>> nested = (10 + 2) * (3 - 4) / 2
    >>> print nested
    -6.0

### Test Case 2: Unary Operator Chaining
Proves the recursive nature of the `factor` parsing rule by handling stacked unary operators.

    >>> x = 5
    >>> print ---x
    -5

    >>> print -(-x)
    5

### Test Case 3: Advanced Relational & Logical Operators
Proves that `not` evaluates before `and`, which evaluates before `or`, alongside standard math comparisons.

    >>> a = 10
    >>> b = 20
    >>> c = 5
    >>> if a < b and not c == 10 { print 100 }
    100

    >>> if a == 99 or b == 20 and c > 0 { print 200 }
    200

### Test Case 4: Nested Conditionals (If/Else Blocks)
Proves that the parser correctly maps branches inside of other branches without losing scope.

    >>> val = 15
    >>> if val > 10 {
    ...   if val < 20 {
    ...     print 1
    ...   } else {
    ...     print 2
    ...   }
    ... } else {
    ...   print 0
    ... }
    1

### Test Case 5: The "FizzBuzz" Logic (While + If/Else)
A classic structural test. Proves the interpreter can handle iteration while simultaneously evaluating complex conditionals and updating memory.

    >>> count = 1
    >>> while count <= 5 {
    ...   if count == 3 {
    ...     print 999
    ...   } else {
    ...     print count
    ...   }
    ...   count = count + 1
    ... }
    1
    2
    999
    4
    5

### Test Case 6: Short-Circuit Logic Simulation
Proves that multiple conditions can be checked safely in a single `while` loop declaration.

    >>> power = 0
    >>> active = 1
    >>> while power < 3 and active == 1 {
    ...   print power
    ...   power = power + 1
    ... }
    0
    1
    2

### Test Case 7: Intermediate Code & Binary Output
Proves that the new LLL and Bits stages are produced correctly for both arithmetic and control-flow constructs. See the worked examples in Sections 6 and 7 for the exact LLL and binary output of:

    >>> result = 10 + 2 * 3 - 4 / 2
    >>> if a < b { print 1 } else { print 0 }
    >>> while count <= 3 { print count  count = count + 1 }

---

## 9. Error Handling
The framework provides graceful error reporting without crashing the REPL session:
- **Lexical Errors**: Throws "Invalid character" if an unsupported symbol (like `@`) is encountered.
- **Syntax Errors**: Throws "Unexpected token" if the grammar rules are violated (e.g., typing `if + print`).
- **Python-Level Fallbacks**: Standard mathematical exceptions (like `ZeroDivisionError`) are caught and displayed in bold red via the `rich` console.

---
