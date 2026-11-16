# TITULO
```mermaid
flowchart LR
    User[User] -->|requests| WebApp[Web Application]
    WebApp -->|calls API| API[REST API]
    API -->|reads/writes| DB[(Database)]
    API -->|stores files| Storage[(File Storage)]

    User -->|uploads files| Storage
```

This example shows a simple architecture:
- User interacts with the web app
- Web app sends requests to the API
- API reads and writes data in the database
- API stores uploaded files in file storage
- The user can also upload directly to storage when needed

# Architect - lab 2.1
- The objective of this lab is test the creation of models based on Pydantic to answer client questions with a structured output schema
```mermaid
flowchart TD
    A[User] -->|ToolCallRequest| B[MCP Server]
    B -->|ToolCallResponse| A
```