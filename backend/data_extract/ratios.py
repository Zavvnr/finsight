"""
Derived financial ratios computed from already-extracted metrics.

Pure functions: they take the income / balance / cash-flow dicts and return
ratios. No I/O, no parsing.
"""


def compute_ratios(income: dict, balance: dict, cash_flow: dict) -> dict:
    try:
        ratios = {}

        # Debt to equity
        debt = balance.get("long_term_debt_millions")
        equity = balance.get("shareholders_equity_millions")
        if debt and equity and equity != 0:
            ratios["debt_to_equity"] = round(debt / equity, 3)

        # Return on equity
        net_income = income.get("net_income_millions")
        if net_income and equity and equity != 0:
            ratios["return_on_equity_pct"] = round((net_income / equity) * 100, 2)

        # Return on assets
        total_assets = balance.get("total_assets_millions")
        if net_income and total_assets and total_assets != 0:
            ratios["return_on_assets_pct"] = round((net_income / total_assets) * 100, 2)

        # Current ratio
        current_assets = balance.get("total_current_assets_millions")
        current_liabilities = balance.get("total_current_liabilities")
        if current_assets and current_liabilities and current_liabilities != 0:
            ratios["current_ratio"] = round(current_assets / current_liabilities, 3)

        # FCF margin
        revenue = income.get("total_revenue_millions")
        fcf = cash_flow.get("free_cash_flow_millions")
        if fcf and revenue and revenue != 0:
            ratios["fcf_margin_pct"] = round((fcf / revenue) * 100, 2)

        # Operating margin
        op_income = income.get("operating_income_millions")
        if op_income and revenue and revenue != 0:
            ratios["operating_margin_pct"] = round((op_income / revenue) * 100, 2)

        # Net margin
        if net_income and revenue and revenue != 0:
            ratios["net_margin_pct"] = round((net_income / revenue) * 100, 2)

        return ratios

    except Exception as e:
        print(f"Error computing financial ratios: {e}")
        raise
