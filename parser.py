from lexer import *

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def to_lll(self, label_count=[0]):
        return self.left.to_lll(label_count) + "\n" + self.right.to_lll(label_count) + f"\n{self.op.type}"

class Num:
    def __init__(self, value):
        self.value = value

    def to_lll(self, label_count=[0]):
        return f"PUSH {self.value}"

class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def to_lll(self, label_count=[0]):
        return self.expr.to_lll(label_count) + f"\n{self.op.type}"

class Var:
    def __init__(self, name):
        self.name = name

    def to_lll(self, label_count=[0]):
        return f"LOAD {self.name}"

class Assign:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_lll(self, label_count=[0]):
        return self.right.to_lll(label_count) + f"\nSTORE {self.left.name}"

class Print:
    def __init__(self, expr):
        self.expr = expr

    def to_lll(self, label_count=[0]):
        return self.expr.to_lll(label_count) + "\nPRINT"

class If:
    def __init__(self, condition, true_branch, false_branch=None):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def to_lll(self, label_count=[0]):
        label_count[0] += 1
        l1 = f"L{label_count[0]}"
        label_count[0] += 1
        l2 = f"L{label_count[0]}"
        
        cond = self.condition.to_lll(label_count)
        true_b = self.true_branch.to_lll(label_count)
        
        if self.false_branch:
            false_b = self.false_branch.to_lll(label_count)
            return f"{cond}\nJZ {l1}\n{true_b}\nJMP {l2}\n{l1}:\n{false_b}\n{l2}:"
        else:
            return f"{cond}\nJZ {l1}\n{true_b}\n{l1}:"

class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def to_lll(self, label_count=[0]):
        label_count[0] += 1
        start_label = f"L{label_count[0]}"
        label_count[0] += 1
        end_label = f"L{label_count[0]}"
        
        cond = self.condition.to_lll(label_count)
        body = self.body.to_lll(label_count)
        
        return f"{start_label}:\n{cond}\nJZ {end_label}\n{body}\nJMP {start_label}\n{end_label}:"

class Block:
    def __init__(self, statements):
        self.statements = statements

    def to_lll(self, label_count=[0]):
        return "\n".join(s.to_lll(label_count) for s in self.statements)

class NoOp:
    def to_lll(self, label_count=[0]):
        return "NOOP"

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f"Syntax Error: Expected {token_type}, got {self.current_token.type}")

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

    def term(self):
        node = self.factor()
        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.factor())
        return node

    def arithmetic_expr(self):
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.term())
        return node

    def comparison(self):
        node = self.arithmetic_expr()
        if self.current_token.type in (EQ, NE, LT, GT, LE, GE):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.arithmetic_expr())
        return node

    def logical_not(self):
        if self.current_token.type == NOT:
            token = self.current_token
            self.eat(NOT)
            return UnaryOp(token, self.logical_not())
        return self.comparison()

    def logical_and(self):
        node = self.logical_not()
        while self.current_token.type == AND:
            token = self.current_token
            self.eat(AND)
            node = BinOp(node, token, self.logical_not())
        return node

    def expr(self):
        node = self.logical_and()
        while self.current_token.type == OR:
            token = self.current_token
            self.eat(OR)
            node = BinOp(node, token, self.logical_and())
        return node

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