import os

from pydantic import BaseModel, ConfigDict
from mcp.server.mcpserver import MCPServer, Context

from week2_lab222_authorization import (
    build_trusted_context,
    authorize_cancellation_request
)
from dotenv import load_dotenv

load_dotenv()

class AuthorizationResult(BaseModel):
    model_config  = ConfigDict(extra="forbid")

    allowed: bool
    reason_code: str
    policy_id: str


# Perfis selecionáveis somente na configuração de startup
# do laboratório. Nunca via argumentos da ferramenta.
LAB_PROFILES = {
    "alice": ("alice","insurance-agent"),
    "bob":("bob", "insurance-agent"),
    "charlie": ("charlie","insurance-agent"),
    "alice_readonly": ("alice","read-only-agent")
}

def resolve_lab_identity():
    """
    Simula uma identidade já estabelecida.

    ATENÇÃO:
    Variáveis de ambiente não são autenticação.
    Este mecanismo é exclusivo do laboratório local.
    """
    profile_name = os.environ.get("NORVIAN_LAB_PROFILE")
    print(profile_name)
    profile = LAB_PROFILES.get(profile_name)

    print(profile)

    if profile is None:
        return None

    principal_id, agent_id = profile

    try:
        return build_trusted_context (
            principal_id=principal_id,
            agent_id=agent_id
        )
    except PermissionError:
        return None

# O perfil é resolvido uma única vez no startup.
LAB_IDENTITY = resolve_lab_identity()
print(LAB_IDENTITY)
mcp = MCPServer("Norvian Authorization Lab")

@mcp.tool()
def check_cancellation_authorization(
    policy_id: str,
    ctx: Context
) -> AuthorizationResult:

    """
    Check whether the authenticated principal and delegated
    agent may request cancellation of the given policy.

    This tool does not cancel or modify policies.
    """

    # Context injetado pelo SDK, não pelo LLM.
    # Não utilizamos _meta como fonte de identidade.

    _request_id = ctx.request_id

    # Fail-closed: ausência de identidade confiável.
    if LAB_IDENTITY is None:
        return AuthorizationResult(
            allowed=False,
            reason_code="AUTHENTICATION_REQUIRED",
            policy_id=policy_id
        )

    decision = authorize_cancellation_request(
        context=LAB_IDENTITY,
        policy_id=policy_id
    )

    return AuthorizationResult(
        allowed=decision.allowed,
        reason_code=decision.reason_code,
        policy_id=policy_id
    )

if __name__ == "__main__":
    mcp.run()