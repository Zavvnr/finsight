"""
Structured XBRL extraction from SEC ``companyfacts`` data.

Pure logic over the facts dict returned by ``sec_client.get_company_facts``;
nothing in this module performs network I/O.
"""

# field -> (taxonomy, XBRL concept, unit)
CONCEPT_MAP = {
    "total_revenue": ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax", "USD"),
    "net_income":          ("us-gaap", "NetIncomeLoss", "USD"),
    "total_assets":        ("us-gaap", "Assets", "USD"),
    "total_liabilities":   ("us-gaap", "Liabilities", "USD"),
    "shareholders_equity": ("us-gaap", "StockholdersEquity", "USD"),
    "operating_cash_flow": ("us-gaap", "NetCashProvidedByUsedInOperatingActivities", "USD"),
    "cash_and_equivalents": ("us-gaap", "CashAndCashEquivalentsAtCarryingValue", "USD"),
}


def latest_annual(facts, taxonomy, concept, unit):
    """Most recent 10-K (full-year) value for one concept, with its period."""
    try:
        rows = facts["facts"][taxonomy][concept]["units"][unit]
    except KeyError:
        return None

    annual = [r for r in rows if r.get("form") == "10-K" and r.get("fp") == "FY"]

    if not annual:
        return None

    best = max(annual, key=lambda r: r["end"])     # latest period end
    return {"value": best["val"], "fy": best["fy"], "end": best["end"]}


# field -> candidate concept names to try in the company's own namespace
EXTENSION_OVERRIDES = {
    "product_revenue": ["RevenueFromProducts", "ProductRevenue"],
}


def get_fact(facts, field):
    """
    Standard us-gaap concept first; fall back to company extension tags.

    Some line items live in the company's own namespace (e.g. aapl:) instead of us-gaap:. Try the standard tag
    first, then fall back to candidate names in any non-standard namespace. Note: a few breakdowns (product /
    segment revenue) are not reliably tagged anywhere.
    """
    # Standard us-gaap concept first (only if this field is mapped there).
    # Some fields (e.g. product_revenue) are extension-only and not in CONCEPT_MAP,
    # so use .get() to avoid a KeyError and fall through to the extension search.
    mapped = CONCEPT_MAP.get(field)
    if mapped:
        taxonomy, concept, unit = mapped
        hit = latest_annual(facts, taxonomy, concept, unit)
        if hit:
            return hit

    # Fall back to the company's own extension namespace(s).
    for tax, concepts in facts.get("facts", {}).items():
        if tax in ("us-gaap", "dei"):          # standard / metadata, already tried
            continue

        for cand in EXTENSION_OVERRIDES.get(field, []):
            if cand in concepts:

                for u in concepts[cand]["units"]:
                    hit = latest_annual(facts, tax, cand, u)
                    if hit:
                        return hit
    return None
