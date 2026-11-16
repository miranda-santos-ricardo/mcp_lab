from mcp.server.mcpserver import MCPServer, Context
from mcp.server.auth.middleware.auth_context import get_access_token 
from pydantic import BaseModel, ConfigDict

mcp = MCPServer(
    title="Norvian Context Security Lab",
    version="0.1.0"
)

class ContextInspection(BaseModel):
    model_config = ConfigDict(extra="forbid")
  
    request_id : str
    has_authenticated_token : bool
    authenticated_client_id : str | None
    authenticated_subject : str | None
    metadata_present: bool
    headers_present: bool

@mcp.tool()
def inspect_request_context(ctx: Context) -> ContextInspection:
    """Inspect request context without exposing credentials"""
    token = get_access_token()

    return ContextInspection(
        request_id=str(ctx.request_id),
        has_authenticated_token=token is not None,
        authenticated_client_id=(
            token.client_id if token else None
        ),
        authenticated_subject=(
            token.subject if token else None
        ),
        metadata_present=bool(ctx.request_context.meta),
        headers_present=bool(ctx.headers),
    )

if __name__ == "__main__":
    mcp.run()