import sys
from lexer import Lexer
from parser import *
from interpreter import Interpreter
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.tree import Tree

console = Console()

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
            # Multi-line input handling for blocks
            text = Prompt.ask("[bold green]>>>[/bold green]")

            if text.strip().lower() == "exit":
                console.print("[bold red]Goodbye![/bold red]")
                break

            if not text.strip():
                continue

            # Support for simple multi-line input by checking for unclosed braces
            while text.count('{') > text.count('}'):
                more_text = Prompt.ask("[bold yellow]...[/bold yellow]")
                text += " " + more_text

            lexer = Lexer(text)
            parser = Parser(lexer)
            
            # 1. Parse into a tree
            tree_root = parser.parse()
            
            # 2. Visualize the tree (for the teacher!)
            console.print("\n[bold white]Generated Abstract Syntax Tree (AST):[/bold white]")
            console.print(visualize_ast(tree_root))
            console.print("")

            # 2.5 Show the LLL (Low Level Language / Intermediate Code)
            console.print("[bold yellow]LLL (Intermediate Code):[/bold yellow]")
            lll_code = tree_root.to_lll()
            console.print(f"[white]{lll_code}[/white]\n")

            # 2.6 Show the Bits (Binary Representation)
            console.print("[bold cyan]Bits (Binary Representation):[/bold cyan]")
            binary_bits = ' '.join(format(ord(c), '08b') for c in lll_code)
            console.print(f"[green]{binary_bits}[/green]\n")

            # 3. Interpret the tree
            interpreter.parser = parser # Not really needed if we call visit directly, but keep for consistency
            interpreter.visit(tree_root)
            
            # Print memory state if it's a simple assignment
            if text.strip().startswith(('if', 'while', 'print', '{')):
                pass # Already handled by visit
            elif '=' in text:
                var_name = text.split('=')[0].strip()
                if var_name in interpreter.memory:
                    console.print(f"[dim white]{var_name} = {interpreter.memory[var_name]}[/dim white]")

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    run_tui()
