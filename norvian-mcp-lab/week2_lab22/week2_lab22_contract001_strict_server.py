import json 
import os

from dotenv import load_dotenv

from jsonschema import Draft202012Validator

from mcp.server import Server, ServerRequestContext
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    ListToolsResult,
    PaginatedRequestParams,
    TextContent,
    Tool
)

from week2_lab222_authorization import (
    build_trusted_context,
    authorize_cancellation_request
)


TOOL_NAME = "check_cancellation_authorization"

INPUT_SCHEMA = {
    "type":"object",
    "properties": {
        "policy_id": {
            "type":"string",
            "pattern":r"^POL-[0-9]{3}$",
        },
    },
    "required":["policy_id"],
    "additionalProperties": False
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "allowed": {"type":"boolean"},
        "reason_code":{"type":"string"},
        "policy_id":{"type":"string"},
    },
    "required":["allowed","reason_code","policy_id"],
    "additionalProperties": False
}

Draft202012Validator.check_schema(INPUT_SCHEMA)
INPUT_VALIDATOR = Draft202012Validator(INPUT_SCHEMA)

TOOL = Tool(
    name=TOOL_NAME,
    description="check permission to request policy cancellations",
    input_schema=INPUT_SCHEMA,
    output_schema=OUTPUT_SCHEMA
)

LAB_PROFILES = {
    "alice": ("alice", "insurance-agent"),
    "bob": ("bob", "insurance-agent"),
    "charlie": ("charlie", "insurance-agent"),
    "alice-readonly": ("alice", "read-only-agent"),
}


def resolve_identity(profile_name):
    """Resolve an internally selected laboratory identity."""

    profile = LAB_PROFILES.get(profile_name)

    if profile is None:
        return None

    try:
        return build_trusted_context(*profile)
    except PermissionError:
        return None

def tool_error(code: str) -> CallToolResult:
    """Return a controlled tool-execution error."""
    return CallToolResult(
        content=[TextContent(type="text",text=code)],
        is_error=True
    )

def create_server(profile_name=None) -> Server:
    """
    Create an isolated low-level MCP server.

    The profile is chosen by the trusted test harness or
    local startup configuration, never by tool arguments.
    """

    identity = resolve_identity(profile_name)

    async def list_tools(
        ctx: ServerRequestContext,
        params:PaginatedRequestParams|None
    ) -> ListToolsResult:
        return ListToolsResult(tools=[TOOL])

    async def call_tool(
        ctx: ServerRequestContext,
        params: CallToolRequestParams
    ) -> CallToolResult:

        if params.name != TOOL_NAME:
            return tool_error("UNKNOW_TOOL")

        # Layer 1: strict contract validation.
        arguments = params.arguments

        if not isinstance (arguments, dict):
            return tool_error("INVALID_ARGUMENTS")

        errors = list(INPUT_VALIDATOR.iter_errors(arguments))

        if errors:
            return tool_error("INVALID_ARGUMENTS")

        # Only validated arguments reach the service.
        policy_id = arguments["policy_id"]

        # Layer 2: trusted identity.
        if identity is None:
            return tool_error("AUTHENTICATION_REQUIRED")

        # Layer 3: delegated/object-level authorization.
        decision = authorize_cancellation_request(
            context=identity,
            policy_id=policy_id
        )

        decision_data ={
            "allowed":decision.allowed,
            "reason_code":decision.reason_code,
            "policy_id":policy_id
        }

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(decision_data)
                )
            ],
            structured_content=decision_data
        )

    return Server(
        "Norvian Strict Contract Lab",
        on_list_tools=list_tools,
        on_call_tool=call_tool
    )


# Local demonstration only.
# Do not expose this as a production authentication mechanism.
load_dotenv() 
user = os.getenv("NORVIAN_LAB_PROFILE")
user = "bob"
server = create_server(user)

# ASGI application for optional MCP Inspector testing.
app = server.streamable_http_app()
