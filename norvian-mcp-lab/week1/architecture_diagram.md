# Solution Architecture
## High Level
```mermaid
flowchart TD
    User[MCP User] <--> MCP[MCP Server] 
```

## Detailed diagram
```mermaid
flowchart LR
    User[MCP User] -->|MCP Connection| MCP[MCP Server]
    MCP --> |Accept connection| User
    User --> |discover phase| MCP
    User --> |tools/list| MCP