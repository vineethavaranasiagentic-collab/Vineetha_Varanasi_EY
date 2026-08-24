from rules.opportunity_rules import detect_opportunities
from rules.risk_rules import detect_risks


def test_payment_and_covenant_risks_are_detected():
    profile = {
        "transactions": [{"transaction_type": "delayed_payment"}],
        "covenants": [{"status": "warning"}],
        "industry_news": [],
    }
    risks = detect_risks(profile)
    assert {risk["risk"] for risk in risks} == {"Payment risk", "Covenant stress"}


def test_working_capital_opportunity_requires_activity_and_missing_product():
    profile = {"transactions": [{}, {}], "products": []}
    opportunities = detect_opportunities(profile)
    assert opportunities[0]["opportunity"] == "Working Capital Facility"
