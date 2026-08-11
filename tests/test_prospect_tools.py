"""Prospect tools must never surface billing/identity fields."""

import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("LANGSMITH_TRACING", "false")

from gtm_agent.gtm_agent import build_prospect_profile, get_prospect

PROSPECT_ID = "LEAD-12853"

SENSITIVE_KEYS = (
    "billing_qualification",
    "tax_id",
    "date_of_birth",
    "card_on_file",
    "credit_check_ref",
)


def assert_no_sensitive_keys(value):
    "Recursively assert no sensitive key appears anywhere in value."
    if isinstance(value, dict):
        for key, nested in value.items():
            assert key not in SENSITIVE_KEYS, f"sensitive key {key!r} present"
            assert_no_sensitive_keys(nested)
    elif isinstance(value, (list, tuple)):
        for item in value:
            assert_no_sensitive_keys(item)


def test_get_prospect_omits_sensitive_fields():
    result = get_prospect.invoke({"prospect_id": PROSPECT_ID})
    assert result["found"] is True
    assert result["prospect"]["email"] == "omar.okafor@lakesideanalytics.com"
    assert_no_sensitive_keys(result)


def test_build_prospect_profile_omits_sensitive_fields_fresh_and_cached():
    fresh = build_prospect_profile.invoke({"prospect_id": PROSPECT_ID})
    assert fresh["found"] is True
    assert fresh["prospect_profile"]["tech_stack"]
    assert_no_sensitive_keys(fresh)

    cached = build_prospect_profile.invoke({"prospect_id": PROSPECT_ID})
    assert cached["prospect_profile"] == fresh["prospect_profile"]
    assert_no_sensitive_keys(cached)
