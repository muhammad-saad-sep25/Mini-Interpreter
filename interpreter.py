from parser import *
from rich.console import Console
from rich.prompt import Prompt
from rich.tree import Tree

console = Console()

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
            elif node.op.type == NOT:
                return not self.visit(node.expr)

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
            elif node.op.type == AND:
                return left and right
            elif node.op.type == OR:
                return left or right

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

def visualize_ast(node, tree=None):
    if tree is None:
        tree = Tree(f"[bold magenta]{node.__class__.__name__}[/bold magenta]")
    
    if isinstance(node, BinOp):
        op_node = tree.add(f"[yellow]Op: {node.op.value}[/yellow]")
        visualize_ast(node.left, op_node)
        visualize_ast(node.right, op_node)
    elif isinstance(node, UnaryOp):
        op_node = tree.add(f"[yellow]Unary: {node.op.value}[/yellow]")
        visualize_ast(node.expr, op_node)
    elif isinstance(node, Num):
        tree.add(f"[green]Num: {node.value}[/green]")
    elif isinstance(node, Var):
        tree.add(f"[cyan]Var: {node.name}[/cyan]")
    elif isinstance(node, Assign):
        tree.add(f"[cyan]Assign to: {node.left.name}[/cyan]")
        visualize_ast(node.right, tree)
    elif isinstance(node, Print):
        visualize_ast(node.expr, tree.add("[blue]Print[/blue]"))
    elif isinstance(node, If):
        cond = tree.add("[bold red]If[/bold red]")
        visualize_ast(node.condition, cond.add("Condition"))
        visualize_ast(node.true_branch, cond.add("True Branch"))
        if node.false_branch:
            visualize_ast(node.false_branch, cond.add("False Branch"))
    elif isinstance(node, While):
        loop = tree.add("[bold red]While[/bold red]")
        visualize_ast(node.condition, loop.add("Condition"))
        visualize_ast(node.body, loop.add("Body"))
    elif isinstance(node, Block):
        block = tree.add("[bold blue]Block[/bold blue]")
        for stmt in node.statements:
            visualize_ast(stmt, block)
    
    return tree

def run_tui():
    interpreter = Interpreter(None)
    
    while True:
        try:
            text = Prompt.ask("[bold green]>>>[/bold green]")

            if text.strip().lower() == "exit":
                console.print("[bold red]Goodbye![/bold red]")
                break

            if not text.strip():
                continue

            while text.count('{') > text.count('}'):
                more_text = Prompt.ask("[bold yellow]...[/bold yellow]")
                text += " " + more_text

            lexer = Lexer(text)
            parser = Parser(lexer)
            
            tree_root = parser.parse()
            
            console.print("\n[bold white]Generated Abstract Syntax Tree (AST):[/bold white]")
            console.print(visualize_ast(tree_root))
            console.print("")

            # Show the LLL (Low Level Language / Intermediate Code)
            console.print("[bold yellow]LLL (Intermediate Code):[/bold yellow]")
            lll_code = tree_root.to_lll()
            console.print(f"[white]{lll_code}[/white]\n")

            # Show the Bits (Binary Representation)
            console.print("[bold cyan]Bits (Binary Representation):[/bold cyan]")
            binary_bits = ' '.join(format(ord(c), '08b') for c in lll_code)
            console.print(f"[green]{binary_bits}[/green]\n")

            interpreter.parser = parser
            interpreter.visit(tree_root)
            
            if text.strip().startswith(('if', 'while', 'print', '{')):
                pass 
            elif '=' in text:
                var_name = text.split('=')[0].strip()
                if var_name in interpreter.memory:
                    console.print(f"[dim white]{var_name} = {interpreter.memory[var_name]}[/dim white]")

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    run_tui()