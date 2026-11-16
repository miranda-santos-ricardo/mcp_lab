from dataclasses import dataclass
from typing import FrozenSet

REQUEST_CANCELLATION = "policy:cancellation:request"

@dataclass(frozen=True)
class AuthorizationContext:
    principal_id: str
    agent_id: str
    tenant_id: str
    principal_permissions: FrozenSet[str]
    agent_permissions: FrozenSet[str]

@dataclass(frozen=True)
class PolicyRecord:
    policy_id: str
    owner_id: str
    tenant_id: str
    status: str

@dataclass(frozen=True)
class AuthorizationDecision:
    allowed: bool
    reason_code: str

# fixtures internas do lab
# Nao sao argumentos publ no contrato (MCP)

IDENTITIES = {
    "alice": {
        "tenant": "TENANT-A",
        "permissions":frozenset({REQUEST_CANCELLATION})
    },
    "bob":{
        "tenant": "TENANT-A",
        "permissions":frozenset({REQUEST_CANCELLATION})
    },
    "charlie": {
        "tenant":"TENANT-A",
        "permissions": frozenset()
    }
}

AGENTS = {
    "insurance-agent": frozenset({REQUEST_CANCELLATION}),
    "read-only-agent": frozenset({"policy:read"})
}

# relacoes confiaveis de delegacao simulada
DELEGATIONS = {
    ("alice", "insurance-agent"),
    ("bob", "insurance-agent"),
    ("charlie", "insurance-agent"),
    ("alice","read-only-agent")
}

POLICIES = {
    "POL-001": PolicyRecord(
        policy_id="POL-001",
        owner_id="alice",
        tenant_id="TENANT-A",
        status="ACTIVE",
    ),
    "POL-002": PolicyRecord(
        policy_id="POL-002",
        owner_id="bob",
        tenant_id="TENANT-A",
        status="ACTIVE",
    ),
    "POL-003": PolicyRecord(
        policy_id="POL-003",
        owner_id="alice",
        tenant_id="TENANT-B",
        status="ACTIVE",
    ),
}

def build_trusted_context(
        principal_id: str,
        agent_id: str
) -> AuthorizationContext:
    """
    Simula um identity provider confiável.

    Apenas o harness de teste deve chamar esta função.
    Nunca construa este contexto com argumentos livres do LLM.
    """
    identity = IDENTITIES.get(principal_id)
    agent_permissions = AGENTS.get(agent_id)

    if identity is None or agent_permissions is None:
        raise PermissionError("UNKNOW_IDENTITY")

    if (principal_id, agent_id) not in DELEGATIONS:
        raise PermissionError("DELEGATION_NOT_FOUND")

    return AuthorizationContext(
        principal_id=principal_id,
        agent_id=agent_id,
        tenant_id=identity["tenant"],
        principal_permissions=identity["permissions"],
        agent_permissions=agent_permissions
    )

def authorize_cancellation_request(
        context: AuthorizationContext,
        policy_id: str
) -> AuthorizationDecision:

    #JAMAIS DEVE PRESSUPOR AUTORIZACAO
    if REQUEST_CANCELLATION not in context.principal_permissions:
        return AuthorizationDecision(False, "USER_PERMISSION_DENIED")

    if REQUEST_CANCELLATION not in context.agent_permissions:
        return AuthorizationDecision(False, "AGENT_PERMISSION_DENIED")

    policy = POLICIES.get(policy_id)

    if policy is None:
        return AuthorizationDecision(False, "RESOURCE_NOT_ACCESSIBLE")

    if policy.tenant_id != context.tenant_id:
        return AuthorizationDecision(False, "RESOURCE_NOT_ACCESSIBLE")

    if policy.owner_id != context.principal_id:
        return AuthorizationDecision(False,  "RESOURCE_NOT_ACCESSIBLE")

    return AuthorizationDecision(True, "AUTHORIZED")

