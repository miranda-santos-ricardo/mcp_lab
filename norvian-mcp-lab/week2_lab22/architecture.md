```mermaid 
flowchart TD
    A[MCP Client] --> B[MCP Tool Handler]
    B --> C[Authorization Service]
    C --> D[Cancellation Service] 
    D --> E[Cancellation Request]

```