"""
Sanity checks on extracted metrics.

Cheap validation that runs before the data reaches the model, so obvious
mapping errors surface as warnings instead of confident-but-wrong analysis.
"""


def validate(metrics: dict) -> list:
    """
    Return human-readable warnings; empty list means it looks sane.

    Cheap sanity checks catch bad mappings before they reach the model and become confident-but-wrong analysis.
    """
    w = []
    a, l, e = (metrics.get(k) for k in
               ("total_assets", "total_liabilities", "shareholders_equity"))
    if a and l and e and abs(a - (l + e)) > 0.01 * a:
        w.append("Balance sheet off: assets != liabilities + equity")
    rev, ni = metrics.get("total_revenue"), metrics.get("net_income")
    if rev and ni and ni > rev:
        w.append("Net income exceeds revenue - check mapping")
    return w
