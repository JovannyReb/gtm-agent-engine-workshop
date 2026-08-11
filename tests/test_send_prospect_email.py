import pytest

from langchain.tools import ToolRuntime

from gtm_agent.gtm_agent import send_prospect_email
from gtm_agent.gtm_records import PROSPECTS

DISQUALIFIED_ID = "LEAD-50001"


@pytest.fixture
def runtime():
    return ToolRuntime(
        state=None,
        context=None,
        stream_writer=None,
        tool_call_id="test-tool-call",
        store=None,
        config={"metadata": {"user_id": "REP-1001"}},
    )


@pytest.fixture
def disqualified_prospect():
    record = PROSPECTS[DISQUALIFIED_ID]
    assert record["disqualified"] is True
    # The model passes a trimmed dict with the disqualified field dropped.
    return {
        "prospect_id": DISQUALIFIED_ID,
        "name": record["name"],
        "email": record["email"],
    }


def test_send_is_blocked_for_disqualified_prospect(runtime, disqualified_prospect):
    result = send_prospect_email.func(
        prospect=disqualified_prospect,
        subject="Pricing collateral",
        body="Here is the pricing overview.",
        runtime=runtime,
    )
    assert result["status"] == "blocked"
    assert "message_id" not in result


def test_send_proceeds_for_disqualified_prospect_with_override(runtime, disqualified_prospect):
    result = send_prospect_email.func(
        prospect=disqualified_prospect,
        subject="Pricing collateral",
        body="Here is the pricing overview.",
        runtime=runtime,
        override_disqualified=True,
    )
    assert result["status"] == "sent"
    assert result["to"] == disqualified_prospect["email"]


def test_send_fails_without_email_address(runtime):
    result = send_prospect_email.func(
        prospect={"prospect_id": "LEAD-99999", "name": "No Contact"},
        subject="Intro",
        body="Hello.",
        runtime=runtime,
    )
    assert result["status"] == "failed"
