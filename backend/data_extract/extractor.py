"""
Main extraction pipeline.

Orchestrates the SEC client and the extraction modules into a single
``run(ticker)`` call that turns a ticker symbol into structured JSON.

Run from the repo root:
    python -m backend.data_extract.extractor AAPL 10-K
or import ``run`` from the FastAPI app (see app.py).
"""

import json

from .sec_client import get_cik, get_filings, get_document_url, fetch_and_parse
from .sections import extract_sections
from .text_metrics import (
    extract_income_statement,
    extract_balance_sheet,
    extract_cash_flow,
    extract_qualitative,
)
from .ratios import compute_ratios


# ─── MAIN PIPELINE ──────────────────────────────────────────────────────────

def extract_all_metrics(sections: dict) -> dict:
    """Run all extraction layers and return unified metrics dict."""
    try:
        financial_text = sections.get("financial_statements", "") + sections.get("mda", "")

        income    = extract_income_statement(financial_text)
        balance   = extract_balance_sheet(financial_text)
        cash_flow = extract_cash_flow(financial_text)
        ratios    = compute_ratios(income, balance, cash_flow)
        qualitative = extract_qualitative(sections)

        return {
            "income_statement": income,
            "balance_sheet": balance,
            "cash_flow": cash_flow,
            "computed_ratios": ratios,
            "qualitative": qualitative,
        }

    except Exception as e:
        print(f"Error extracting all metrics: {e}")
        raise


def run(ticker: str, form_type: str = "10-K") -> dict:
    """Full pipeline: ticker symbol → structured JSON."""
    try:
        print(f"\n[1/4] Looking up CIK for {ticker}...")
        cik = get_cik(ticker)
        print(f"      CIK: {cik}")

        print(f"[2/4] Fetching {form_type} filings...")
        filings = get_filings(cik, form_type=form_type, limit=1)

        if not filings:
            raise ValueError(f"No {form_type} filings found for {ticker}")

        filing = filings[0]
        print(f"      Most recent: {filing['date']}")

        print(f"[3/4] Fetching and parsing document...")
        url = get_document_url(cik, filing["accession"], filing["primary_document"])
        print(f"      URL: {url}")
        text = fetch_and_parse(url)

        print(f"[4/4] Extracting sections and metrics...")
        sections = extract_sections(text)
        metrics  = extract_all_metrics(sections)

        result = {
            "ticker": ticker.upper(),
            "form": form_type,
            "filing_date": filing["date"],
            "accession_number": filing["accession"],
            "source_url": url,
            "char_count": len(text),
            "metrics": metrics,
            "sections": sections,
        }

        return result

    except Exception as e:
        print(f"Error in run pipeline for {ticker} {form_type}: {e}")
        raise


if __name__ == "__main__":
    import sys

    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    form   = sys.argv[2] if len(sys.argv) > 2 else "10-K"

    data = run(ticker, form)

    output_file = f"{ticker}_{form.replace('-', '')}.json"
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nSaved → {output_file}")
    print(f"Sections found:  {list(data['sections'].keys())}")
    print(f"\nMetrics summary:")
    for category, values in data["metrics"].items():
        if values:
            print(f"  {category}: {len(values)} fields extracted")
    print(f"\nTotal characters: {data['char_count']:,}")
