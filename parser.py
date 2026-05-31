# parser.py

from lexer import *

# AST Nodes
class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Num:
    def __init__(self, value):
        self.value = value

class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Var:
    def __init__(self, name):
        self.name = name

class Assign:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Print:
    def __init__(self, expr):
        self.expr = expr

class If:
    def __init__(self, condition, true_branch, false_branch=None):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class Block:
    def __init__(self, statements):
        self.statements = statements

class NoOp:
    pass

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f"Syntax Error: Expected {token_type}, got {self.current_token.type}")

    # factor → (+ | -) factor | INTEGER | ID | ( expr )
    def factor(self):
        token = self.current_token

        if token.type == PLUS:
            self.eat(PLUS)
            return UnaryOp(token, self.factor())
        elif token.type == MINUS:
            self.eat(MINUS)
            return UnaryOp(token, self.factor())
        elif token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token.value)
        elif token.type == ID:
            self.eat(ID)
            return Var(token.value)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        raise Exception(f"Syntax Error: Unexpected token {token.type} in factor")

    # term → factor (* or /)
    def term(self):
        node = self.factor()
        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.factor())
        return node

    # arithmetic_expr → term (+ or -)
    def arithmetic_expr(self):
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.term())
        return node

    # expr → arithmetic_expr (comparison arithmetic_expr)?
    def expr(self):
        node = self.arithmetic_expr()
        if self.current_token.type in (EQ, NE, LT, GT, LE, GE):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.arithmetic_expr())
        return node

    # statement → assignment | print | if | while | block
    def statement(self):
        if self.current_token.type == ID:
            left = Var(self.current_token.value)
            self.eat(ID)
            self.eat(ASSIGN)
            right = self.expr()
            return Assign(left, right)
        elif self.current_token.type == PRINT:
            self.eat(PRINT)
            expr = self.expr()
            return Print(expr)
        elif self.current_token.type == IF:
            self.eat(IF)
            condition = self.expr()
            true_branch = self.statement()
            false_branch = None
            if self.current_token.type == ELSE:
                self.eat(ELSE)
                false_branch = self.statement()
            return If(condition, true_branch, false_branch)
        elif self.current_token.type == WHILE:
            self.eat(WHILE)
            condition = self.expr()
            body = self.statement()
            return While(condition, body)
        elif self.current_token.type == LBRACE:
            return self.block()
        else:
            return NoOp()

    def block(self):
        self.eat(LBRACE)
        statements = []
        while self.current_token.type != RBRACE and self.current_token.type != EOF:
            statements.append(self.statement())
        self.eat(RBRACE)
        return Block(statements)

    def parse(self):
        statements = []
        while self.current_token.type != EOF:
            statements.append(self.statement())
        return Block(statements) if len(statements) > 1 else (statements[0] if statements else NoOp())