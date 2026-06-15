"""
Extractor functions for fetching and parsing SEC filings.
"""

from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from extractor import run   # Running the full pipeline for a given ticker and form type

import json
import os
import re
import requests

# SEC requires a descriptive User-Agent or you'll get 403s
# Replace with your name and UW email
SEC_HEADERS = {
    "User-Agent": "FinSight rahmansyah@wisc.edu",
    "Accept-Encoding": "gzip, deflate",
}


app = FastAPI()


def get_company_facts(cik: str) -> dict:
    """All XBRL facts SEC has for a company, in one cached call."""
    try:
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        r = requests.get(url, headers={**SEC_HEADERS, "Host": "data.sec.gov"})
        r.raise_for_status()
        return r.json()
    
    except requests.exceptions.Timeout as e:
        print(f"Timeout error fetching company facts for CIK {cik}: {e}")
        raise
    
    except requests.RequestException as e:
        print(f"Error fetching company facts for CIK {cik}: {e}")
        raise
    
    except Exception as e:
        print(f"Unexpected error fetching company facts for CIK {cik}: {e}")
        raise
    
    
def get_cik(ticker: str) -> str:
    """Look up a company's CIK number by ticker symbol."""
    try :
        url = "https://www.sec.gov/files/company_tickers.json"
        r = requests.get(url, headers={**HEADERS, "Host": "www.sec.gov"})
        r.raise_for_status()
        data = r.json()
        for entry in data.values():
            if entry["ticker"].upper() == ticker.upper():
                return str(entry["cik_str"]).zfill(10)
        raise ValueError(f"Ticker '{ticker}' not found in SEC database")
    
    except requests.exceptions.Timeout as e:
        print(f"Request timed out: {e}")
        raise
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise
    
    except Exception as e:
        print(f"An error occurred: {e}")
        raise


def get_filings(cik: str, form_type: str = "10-K", limit: int = 5) -> list:
    """Get recent filings of a given type for a company."""
    try:
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        r = requests.get(url, headers={**SEC_HEADERS, "Host": "data.sec.gov"})
        r.raise_for_status()
        data = r.json()

        recent = data["filings"]["recent"]
        results = []

        for i, form in enumerate(recent["form"]):
            if form == form_type:
                results.append({
                    "form": form,
                    "date": recent["filingDate"][i],
                    "accession": recent["accessionNumber"][i],
                    "primary_document": recent["primaryDocument"][i],
                })
            if len(results) >= limit:
                break

        return results
    
    except requests.exceptions.Timeout as e:
        print(f"Timeout error fetching filings for CIK {cik}: {e}")
        raise
    
    except requests.RequestException as e:
        print(f"Error fetching filings for CIK {cik}: {e}")
        raise
    
    except Exception as e:
        print(f"Unexpected error fetching filings for CIK {cik}: {e}")
        raise


def get_document_url(cik: str, accession: str, primary_doc: str) -> str:
    """Build the full URL to the filing document on SEC EDGAR."""
    accession_clean = accession.replace("-", "")
    cik_int = int(cik)
    return f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_clean}/{primary_doc}"


def fetch_and_parse(url: str) -> str:
    """Fetch an SEC filing HTML page and return clean plain text."""
    r = requests.get(url, headers={**HEADERS, "Host": "www.sec.gov"})
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "lxml")

    # Remove noise tags
    for tag in soup(["script", "style", "meta", "noscript", "img", "head"]):
        tag.decompose()

    # Strip inline XBRL tags but keep their text content
    for tag in soup.find_all(re.compile(r"^ix:")):
        tag.unwrap()

    # Remove hidden elements (XBRL metadata often lives here)
    for tag in soup.find_all(style=re.compile(r"display\s*:\s*none", re.I)):
        tag.decompose()
    for tag in soup.find_all(attrs={"hidden": True}):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # Remove blank lines and lines that are pure XBRL namespace garbage
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r"^https?://[a-z./]+#", line):
            continue
        if re.match(r"^[a-z]+:[A-Z][a-zA-Z]+$", line):
            continue
        lines.append(line)

    return "\n".join(lines)


def extract_sections(text: str) -> dict:
    """
    Rule-based section extraction using known 10-K/10-Q header keywords.
    Handles TOC false-matches by requiring sections to have substantial content.
    Many filings (e.g. MSFT) have a TOC where Item headers appear with just page
    numbers, then again in the body with real content. We collect ALL matches per
    section key and keep the one with the most content.
    """
    section_names = {
        "Item 1.": "business",
        "Item 1A.": "risk_factors",
        "Item 1B.": "unresolved_staff_comments",
        "Item 1C.": "cybersecurity",
        "Item 2.": "properties",
        "Item 3.": "legal_proceedings",
        "Item 4.": "mine_safety",
        "Item 5.": "market_for_equity",
        "Item 6.": "reserved",
        "Item 7.": "mda",
        "Item 7A.": "market_risk",
        "Item 8.": "financial_statements",
        "Item 9.": "accountant_changes",
        "Item 9A.": "controls_procedures",
        "Item 9B.": "other_information",
    }

    section_keywords = list(section_names.keys())

    # Collect all occurrences of each section
    # sections_all maps section_key -> list of content strings
    sections_all: dict[str, list[str]] = {}
    lines = text.splitlines()
    current_key = "header"
    buffer: list[str] = []

    for line in lines:
        matched_kw = next(
            (kw for kw in section_keywords if line.strip().startswith(kw) and len(line) < 120),
            None
        )
        if matched_kw:
            # Save current buffer under current key
            content = "\n".join(buffer).strip()
            if content:
                sections_all.setdefault(current_key, []).append(content)
            current_key = section_names.get(matched_kw, matched_kw)
            buffer = [line]
        else:
            buffer.append(line)

    # Save last buffer
    content = "\n".join(buffer).strip()
    if content:
        sections_all.setdefault(current_key, []).append(content)

    # For each section keep the occurrence with the most content (skips TOC stubs)
    sections: dict[str, str] = {}
    for key, occurrences in sections_all.items():
        best = max(occurrences, key=len)
        # Only keep if it has at least 200 chars of real content
        if len(best) >= 200:
            sections[key] = best

    # Drop header if it's mostly XBRL noise
    if "header" in sections:
        header = sections["header"]
        if len(re.findall(r"[.!?]", header)) < 5:
            del sections["header"]

    return sections


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


# ─── HELPERS ────────────────────────────────────────────────────────────────

def _parse_number(raw: str) -> float | None:
    """Convert a string like '416,161' or '7.46' to a float."""
    try:
        return float(raw.replace(",", "").strip())
    
    except Exception as e:
        print(f"Error parsing number from '{raw}': {e}")
        raise


def _search(pattern: str, text: str, flags=re.IGNORECASE) -> str | None:
    """Return first capture group or None."""
    try:
        m = re.search(pattern, text, flags)
        return m.group(1).strip() if m else None
    
    except Exception as e:
        print(f"Error searching for pattern '{pattern}' in text: {e}")
        raise     

# ─── INCOME STATEMENT ───────────────────────────────────────────────────────

def extract_income_statement(text: str) -> dict:
    try:
        out = {}

        pairs = [
            ("total_revenue_millions",       r"[Tt]otal\s+net\s+sales\s*\$?\s*([\d,]+)"),
            ("product_revenue_millions",     r"[Pp]roducts?\s*\$?\s*([\d,]+)\s*\$?\s*[\d,]+\s*\$?\s*[\d,]+"),
            ("services_revenue_millions",    r"[Ss]ervices?\s*(?:\(1\))?\s*\$?\s*([\d,]+)\s*\$?\s*[\d,]+\s*\$?\s*[\d,]+"),
            ("gross_margin_millions",        r"[Gg]ross\s+margin\s*\$?\s*([\d,]+)"),
            ("gross_margin_pct",             r"[Tt]otal\s+gross\s+margin\s+percentage\s+([\d.]+)\s*%"),
            ("operating_income_millions",    r"[Oo]perating\s+income\s*\$?\s*([\d,]+)"),
            ("net_income_millions",          r"[Nn]et\s+income\s*\$?\s*([\d,]+)"),
            ("eps_basic",                    r"[Bb]asic\s*\$?\s*([\d.]+)"),
            ("eps_diluted",                  r"[Dd]iluted\s*\$?\s*([\d.]+)"),
            ("rd_expense_millions",          r"[Rr]esearch\s+and\s+development\s*\$?\s*([\d,]+)"),
            ("sga_expense_millions",         r"[Ss]elling,?\s+general\s+and\s+administrative\s*\$?\s*([\d,]+)"),
            ("total_opex_millions",          r"[Tt]otal\s+operating\s+expenses\s*\$?\s*([\d,]+)"),
            ("income_tax_millions",          r"[Pp]rovision\s+for\s+income\s+taxes\s*\$?\s*([\d,]+)"),
            ("effective_tax_rate_pct",       r"[Ee]ffective\s+tax\s+rate\s+([\d.]+)\s*%"),
        ]

        for key, pattern in pairs:
            raw = _search(pattern, text)
            if raw:
                out[key] = _parse_number(raw)

        # YoY revenue growth — look for a % change figure near "Total net sales"
        growth = _search(r"[Tt]otal\s+net\s+sales.*?([\d]+)\s*%", text, re.DOTALL)
        if growth:
            out["revenue_yoy_growth_pct"] = _parse_number(growth)

        return out
    
    except Exception as e:
        print(f"Error extracting income statement metrics: {e}")
        raise


# ─── BALANCE SHEET ──────────────────────────────────────────────────────────

def extract_balance_sheet(text: str) -> dict:
    try:
        out = {}

        pairs = [
            ("cash_and_equivalents_millions",   r"[Cc]ash\s+and\s+cash\s+equivalents\s*\$?\s*([\d,]+)"),
            ("marketable_securities_current",   r"[Mm]arketable\s+securities\s*\n.*?([\d,]+)"),
            ("total_current_assets_millions",   r"[Tt]otal\s+current\s+assets\s*\$?\s*([\d,]+)"),
            ("total_assets_millions",           r"[Tt]otal\s+assets\s*\$?\s*([\d,]+)"),
            ("total_current_liabilities",       r"[Tt]otal\s+current\s+liabilities\s*\$?\s*([\d,]+)"),
            ("total_liabilities_millions",      r"[Tt]otal\s+liabilities\s*\$?\s*([\d,]+)"),
            ("shareholders_equity_millions",    r"[Tt]otal\s+shareholders.?\s+equity\s*\$?\s*([\d,]+)"),
            ("long_term_debt_millions",         r"[Tt]otal\s+non.current\s+portion\s+of\s+term\s+debt\s*\$?\s*([\d,]+)"),
            ("retained_earnings_millions",      r"[Aa]ccumulated\s+deficit\s*\(?\s*([\d,]+)"),
            ("ppe_net_millions",                r"[Pp]roperty,\s+plant\s+and\s+equipment,\s+net\s*\$?\s*([\d,]+)"),
            ("inventories_millions",            r"[Ii]nventor(?:y|ies)\s*\$?\s*([\d,]+)"),
            ("accounts_receivable_millions",    r"[Aa]ccounts\s+receivable,?\s+net\s*\$?\s*([\d,]+)"),
            ("deferred_revenue_millions",       r"[Dd]eferred\s+revenue\s*\$?\s*([\d,]+)"),
            ("commercial_paper_millions",       r"[Cc]ommercial\s+paper\s*\$?\s*([\d,]+)"),
        ]

        for key, pattern in pairs:
            raw = _search(pattern, text)
            if raw:
                out[key] = _parse_number(raw)

        # Working capital (computed)
        if out.get("total_current_assets_millions") and out.get("total_current_liabilities"):
            out["working_capital_millions"] = (
                out["total_current_assets_millions"] - out["total_current_liabilities"]
            )

        return out
    
    except Exception as e:
        print(f"Error extracting balance sheet metrics: {e}")
        raise


# ─── CASH FLOW ──────────────────────────────────────────────────────────────

def extract_cash_flow(text: str) -> dict:
    try:
        out = {}

        pairs = [
            ("operating_cash_flow_millions",    r"[Cc]ash\s+generated\s+by\s+operating\s+activities\s*\$?\s*([\d,]+)"),
            ("investing_cash_flow_millions",    r"[Cc]ash\s+generated\s+by\s+investing\s+activities\s*\$?\s*([\d,]+)"),
            ("capex_millions",                  r"[Pp]ayments\s+for\s+acquisition\s+of\s+property.*?([\d,]+)"),
            ("dividends_paid_millions",         r"[Pp]ayments\s+for\s+dividends.*?([\d,]+)"),
            ("share_repurchases_millions",      r"[Rr]epurchases?\s+of\s+common\s+stock\s*\(?\s*([\d,]+)"),
            ("depreciation_amortization",       r"[Dd]epreciation\s+and\s+amortization\s*\$?\s*([\d,]+)"),
            ("share_based_comp_millions",       r"[Ss]hare.based\s+compensation\s+expense\s*\$?\s*([\d,]+)"),
        ]

        for key, pattern in pairs:
            raw = _search(pattern, text)
            if raw:
                out[key] = _parse_number(raw)

        # Free cash flow (computed)
        if out.get("operating_cash_flow_millions") and out.get("capex_millions"):
            out["free_cash_flow_millions"] = (
                out["operating_cash_flow_millions"] - out["capex_millions"]
            )

        return out
    
    except Exception as e:
        print(f"Error extracting cash flow metrics: {e}")
        raise


# ─── COMPUTED RATIOS ────────────────────────────────────────────────────────

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


# ─── QUALITATIVE EXTRACTION ─────────────────────────────────────────────────

def extract_qualitative(sections: dict) -> dict:
    try:
        out = {}

        mda = sections.get("mda", "")
        risks = sections.get("risk_factors", "")
        business = sections.get("business", "")

        # Guidance — look for forward-looking language near revenue/growth
        guidance_patterns = [
            r"(expect[s]?\s+.{20,150}(?:revenue|growth|sales|margin).{0,100})",
            r"(anticipate[s]?\s+.{20,150}(?:revenue|growth|sales|margin).{0,100})",
            r"(outlook.{0,20}:.{20,200})",
            r"(guidance.{0,20}:.{20,200})",
        ]
        guidance_hits = []
        for pat in guidance_patterns:
            hits = re.findall(pat, mda, re.IGNORECASE)
            guidance_hits.extend(hits[:2])
        if guidance_hits:
            out["forward_guidance_excerpts"] = guidance_hits[:5]

        # Macro risks mentioned
        macro_keywords = ["tariff", "inflation", "interest rate", "recession", "supply chain",
                        "foreign exchange", "currency", "geopolitical", "trade"]
        macro_mentioned = [kw for kw in macro_keywords if kw.lower() in (mda + risks).lower()]
        out["macro_risks_mentioned"] = macro_mentioned

        # Segment breakdown — capture lines with segment names and dollar amounts
        segment_pattern = r"(Americas|Europe|Greater China|Japan|Rest of Asia Pacific|North America|International)\s*\$?\s*([\d,]+)"
        segments = re.findall(segment_pattern, mda, re.IGNORECASE)
        if segments:
            out["segment_revenue"] = {seg: _parse_number(val) for seg, val in segments[:10]}

        # Product revenue breakdown
        product_pattern = r"(iPhone|Mac|iPad|Wearables|Services|Windows|Cloud|Azure|Advertising|Search)\s*\$?\s*([\d,]+)"
        products = re.findall(product_pattern, mda, re.IGNORECASE)
        if products:
            out["product_revenue"] = {prod: _parse_number(val) for prod, val in products[:10]}

        # Key risk themes from risk factors
        risk_themes = []
        risk_keywords = {
            "competition": r"competi",
            "regulation": r"regulat",
            "cybersecurity": r"cybersecur|data breach|ransomware",
            "supply_chain": r"supply chain|component shortage",
            "ai_risk": r"artificial intelligence|machine learning",
            "ip_risk": r"intellectual property|patent infringement",
            "tax_risk": r"tax rate|tax liabilit",
            "fx_risk": r"foreign exchange|currency fluctuat",
            "geopolitical_risk": r"geopolitical|trade war|sanction",
        }
        for theme, pattern in risk_keywords.items():
            if re.search(pattern, risks, re.IGNORECASE):
                risk_themes.append(theme)
                
        out["key_risk_themes"] = risk_themes

        # Employee count
        emp_match = re.search(r"([\d,]+)\s+full.time\s+equivalent\s+employees", business, re.IGNORECASE)
        if emp_match:
            out["full_time_employees"] = _parse_number(emp_match.group(1))

        # Fiscal year end
        fy_match = re.search(r"fiscal\s+year(?:\s+ended)?\s+(September|December|June|March|January)\s*[\d,]+,?\s*(\d{4})", mda, re.IGNORECASE)
        
        if fy_match:
            out["fiscal_year_end"] = f"{fy_match.group(1)} {fy_match.group(2)}"

        return out
    
    except Exception as e:
        print(f"Error extracting qualitative insights: {e}")
        raise


# ─── MAIN PIPELINE ──────────────────────────────────────────────────────────

def extract_all_metrics(sections: dict) -> dict:
    """Run all extraction layers and return unified metrics dict."""
    try:
        combined_text = " ".join(sections.values())
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
    try:
        """Full pipeline: ticker symbol → structured JSON."""
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