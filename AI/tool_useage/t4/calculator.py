# calculator.py

import sys
import ast

def safe_eval(expr):
    try:
        # Parse the expression into an AST node
        tree = ast.parse(expr, mode='eval')

        # Walk through the AST and only allow safe nodes
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Expression, ast.BinOp, ast.Num, ast.UnaryOp,
                                     ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
                                     ast.Mod, ast.USub, ast.UAdd, ast.FloorDiv)):
                raise ValueError("Unsafe expression")

        # Safely evaluate the expression
        result = eval(compile(tree, filename="<ast>", mode="eval"))
        return result
    except Exception as e:
        return f"ERROR: {e}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR: Expected a single math expression as an argument.")
        sys.exit(1)

    expression = sys.argv[1]
    result = safe_eval(expression)
    print(f"CALC_RESULT: {result}")
