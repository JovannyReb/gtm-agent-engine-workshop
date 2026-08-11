"""Tests for the data-access layer in gtm_agent.data_service."""

import copy

import pytest

from gtm_agent import data_service
from gtm_agent.gtm_records import PROSPECTS

PROSPECT_ID = "LEAD-12853"


@pytest.fixture(autouse=True)
def restore_records():
    original = copy.deepcopy(PROSPECTS[PROSPECT_ID])
    data_service._PROFILES.clear()
    yield
    PROSPECTS[PROSPECT_ID] = original
    data_service._PROFILES.clear()


def test_update_prospect_info_persists_to_source_record():
    result = data_service.update_prospect_info(PROSPECT_ID, "Snowflake")

    assert result == {
        "updated": True,
        "found": True,
        "tech_stack": data_service.fetch_tech_stack(PROSPECT_ID),
    }
    assert "Snowflake" in data_service.fetch_tech_stack(PROSPECT_ID)


def test_update_prospect_info_is_idempotent():
    data_service.update_prospect_info(PROSPECT_ID, "Snowflake")
    data_service.update_prospect_info(PROSPECT_ID, "Snowflake")

    assert data_service.fetch_tech_stack(PROSPECT_ID).count("Snowflake") == 1


def test_update_prospect_info_invalidates_cached_profile():
    data_service.save_profile_to_db(PROSPECT_ID, {"tech_stack": ["Salesforce"]})

    data_service.update_prospect_info(PROSPECT_ID, "Snowflake")

    assert PROSPECT_ID not in data_service._PROFILES
    assert data_service.get_profile_from_db(PROSPECT_ID) == {"prospect_profile": None}


def test_update_prospect_info_unknown_prospect():
    assert data_service.update_prospect_info("LEAD-00000", "Snowflake") == {
        "updated": False,
        "found": False,
    }
