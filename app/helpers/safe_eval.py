import pandas as pd
import numpy as np
import ast
import math
import random


# ----------------------------
# AST-based validation (restricts constructs)
# ----------------------------
ALLOWED_MODULES = {
    "np": np,
    "math": math,
    "random": random,
    "pd": pd
}


class VectorSafeVisitor(ast.NodeVisitor):
    """Allow arithmetic, calls, names, attributes (only for allowed modules), subscript, tuples, lists."""
    ALLOWED_NODES = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Div, ast.Name, ast.Mult, ast.Add, ast.Sub,
        ast.Load, ast.Call, ast.Attribute, ast.Subscript, ast.Index, ast.Slice,
        ast.Tuple, ast.List, ast.Dict, ast.BoolOp, ast.Compare, ast.IfExp
    )

    def __init__(self, allowed_names):
        self.allowed_names = set(allowed_names) | set(ALLOWED_MODULES.keys())

    def generic_visit(self, node):
        if not isinstance(node, self.ALLOWED_NODES):
            raise ValueError(f"Disallowed AST node: {node.__class__.__name__}")
        super().generic_visit(node)

    def visit_Name(self, node):
        if node.id not in self.allowed_names:
            raise ValueError(
                f"Use of name '{node.id}' is not allowed in formulas.")
        super().generic_visit(node)

    def visit_Attribute(self, node):
        # allow attribute access only when base is allowed module
        base = node
        while isinstance(base, ast.Attribute):
            base = base.value
        if isinstance(base, ast.Name):
            if base.id not in ALLOWED_MODULES:
                raise ValueError(
                    f"Attribute access on '{base.id}' is not allowed.")
        else:
            raise ValueError("Complex attribute expressions not allowed.")
        super().generic_visit(node)


def validate_formula_ast(expr, allowed_names):
    node = ast.parse(expr, mode="eval")
    visitor = VectorSafeVisitor(allowed_names)
    visitor.visit(node)
    return True

# ----------------------------
# Vectorized formula evaluation
# ----------------------------


def vectorized_eval(expr: str, df: pd.DataFrame):
    """
    Try to evaluate expr in a vectorized manner by providing numpy arrays for columns.
    If it fails (due to uses of Python-only constructs), raise an Exception so caller can fallback.
    """
    allowed_names = list(df.columns)
    validate_formula_ast(expr, allowed_names)

    local_vars = {c: df[c].to_numpy() for c in df.columns} | ALLOWED_MODULES

    try:
        # Evaluate safely (no builtins)
        result = eval(compile(ast.parse(expr, mode="eval"), '<vec_expr>', 'eval'), {
                      "__builtins__": None}, local_vars)
    except Exception as e:
        raise

    if hasattr(result, '__len__') and not isinstance(result, (str, bytes)) and len(result) == len(df):
        return pd.Series(result)
    else:  # Handle scalar result
        return pd.Series([result] * len(df))

# ----------------------------
# Safe fallback row-wise evaluator
# ----------------------------


def rowwise_safe_eval(expr: str, row: dict):
    validate_formula_ast(expr, list(row.keys()))
    local_vars = row | ALLOWED_MODULES
    return eval(compile(ast.parse(expr, mode="eval"), '<row_expr>', 'eval'), {"__builtins__": None}, local_vars)
