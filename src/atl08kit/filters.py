from __future__ import annotations

from typing import Dict, Tuple
import pandas as pd

from atl08kit.expr import compile_expr, eval_expr


def filter_by_expr(df: pd.DataFrame, expr: str) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Filter a DataFrame by a safe boolean expression.

    Parameters
    ----------
    df : pd.DataFrame
        Input table (e.g., ATL08 extracted points).
    expr : str
        A boolean expression using DataFrame column names, arithmetic/comparisons,
        boolean operators (and/or/not), parentheses, and abs(x).

        Example:
          "abs(dem_h - h_te_best_fit) <= 3 and terrain_flg == 0 and cloud_flag_atm < 3"

    Returns
    -------
    df_filtered : pd.DataFrame
        Filtered rows.
    summary : dict
        Basic stats for reporting.
    """
    compiled = compile_expr(expr)
    mask = eval_expr(compiled, df)
    out = df.loc[mask].copy()

    summary = {
        "expr": expr,
        "N_total": int(len(df)),
        "N_pass": int(mask.sum()),
        "pass_rate": float(mask.mean()) if len(df) else 0.0,
    }
    return out, summary