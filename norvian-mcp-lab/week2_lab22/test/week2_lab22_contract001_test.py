from unittest.mock import patch

import pytest
from mcp import Client

from week2_lab22_contract001_strict_server import (
    TOOL_NAME,
    create_server
)

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.mark.anyio
async def test_01_schema_is_strict():
    async with Client (create_server("alice")) as client:
        result = await client.list_tools()
        tool = next(t for t in result.tools if t.name == TOOL_NAME)

        assert tool.input_schema["additionalProperties"] is False
        assert list(tool.input_schema["properties"]) == ["policy_id"]

@pytest.mark.anyio
async def test_02_valid_request():
    async with Client(create_server("alice")) as client:
        result = await client.call_tool(
            TOOL_NAME,
            {"policy_id": "POL-001"},
        )

        assert result.is_error is not True
        assert result.structured_content["allowed"] is True
        assert result.structured_content["reason_code"] == "AUTHORIZED"


@pytest.mark.anyio
async def test_03_extra_args_rejected_before_service():
    with patch(
        "week2_lab22_contract001_strict_server"
        ".authorize_cancellation_request"
    ) as auth_mock:
        async with Client(create_server("bob")) as client:
            result = await client.call_tool(
                TOOL_NAME,
                {
                    "policy_id": "POL-001",
                    "user_id": "alice",
                    "agent_id": "insurance-agent",
                    "is_admin": True,
                },
            )

        assert result.is_error is True
        assert "INVALID_ARGUMENTS" in result.content[0].text
        auth_mock.assert_not_called()


@pytest.mark.anyio
async def test_04_missing_required_field():
    async with Client(create_server("alice")) as client:
        result = await client.call_tool(TOOL_NAME, {})

        assert result.is_error is True


@pytest.mark.anyio
async def test_05_wrong_field_type():
    async with Client(create_server("alice")) as client:
        result = await client.call_tool(
            TOOL_NAME,
            {"policy_id": 123},
        )

        assert result.is_error is True


@pytest.mark.anyio
async def test_06_bob_still_denied():
    async with Client(create_server("bob")) as client:
        result = await client.call_tool(
            TOOL_NAME,
            {"policy_id": "POL-001"},
        )

        assert result.is_error is not True
        assert result.structured_content["allowed"] is False
        assert (
            result.structured_content["reason_code"]
            == "RESOURCE_NOT_ACCESSIBLE"
        )


@pytest.mark.anyio
async def test_07_missing_identity_denied():
    with patch(
        "week2_lab22_contract001_strict_server"
        ".authorize_cancellation_request"
    ) as auth_mock:

        async with Client(create_server()) as client:
            result = await client.call_tool(
                TOOL_NAME,
                {"policy_id": "POL-001"},
            )

        assert result.is_error is True
        assert result.structured_content is None

        assert (
            "AUTHENTICATION_REQUIRED"
            in result.content[0].text
        )

        # Authentication failure must prevent authorization.
        auth_mock.assert_not_called()