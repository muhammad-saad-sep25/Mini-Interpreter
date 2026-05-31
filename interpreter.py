# interpreter.py

from parser import *

class Interpreter:
    def __init__(self, parser):
        self.parser = parser
        self.memory = {}  # stores variables

    def visit(self, node):
        if isinstance(node, Num):
            return node.value

        elif isinstance(node, Var):
            return self.memory.get(node.name, 0)

        elif isinstance(node, UnaryOp):
            if node.op.type == PLUS:
                return +self.visit(node.expr)
            elif node.op.type == MINUS:
                return -self.visit(node.expr)

        elif isinstance(node, BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)

            if node.op.type == PLUS:
                return left + right
            elif node.op.type == MINUS:
                return left - right
            elif node.op.type == MUL:
                return left * right
            elif node.op.type == DIV:
                return left / right
            elif node.op.type == EQ:
                return left == right
            elif node.op.type == NE:
                return left != right
            elif node.op.type == LT:
                return left < right
            elif node.op.type == GT:
                return left > right
            elif node.op.type == LE:
                return left <= right
            elif node.op.type == GE:
                return left >= right

        elif isinstance(node, Assign):
            value = self.visit(node.right)
            self.memory[node.left.name] = value
            return value

        elif isinstance(node, Print):
            value = self.visit(node.expr)
            print(value)
            return value

        elif isinstance(node, If):
            if self.visit(node.condition):
                return self.visit(node.true_branch)
            elif node.false_branch:
                return self.visit(node.false_branch)

        elif isinstance(node, While):
            result = None
            while self.visit(node.condition):
                result = self.visit(node.body)
            return result

        elif isinstance(node, Block):
            result = None
            for statement in node.statements:
                result = self.visit(statement)
            return result

        elif isinstance(node, NoOp):
            return None

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)