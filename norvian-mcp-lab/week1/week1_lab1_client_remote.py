import asyncio
import json
from mcp import Client

async def main():
    async with Client(
        "http://127.0.0.1:8000/mcp"
    ) as client:
        result = await client.call_tool(
            "get_tool_risk",
            {"tool_name": "payment.execute"}
        )
    #print (result)
    if result.structured_content is not None:
        print(result.structured_content)
    else:
        data = json.loads(result.content[0].text)
        print(f"Risk Level:{data["risk_level"]} | Require Approval: {data["requires_approval"]}")

asyncio.run(main())