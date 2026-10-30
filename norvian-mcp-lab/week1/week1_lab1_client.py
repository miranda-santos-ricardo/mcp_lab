
import asyncio
import json
from mcp import Client
from week1_lab1_server import mcp


async def main() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()

        print("Available tools:")
        for tool in tools.tools:
            #print(tool)
            print(f"- {tool.name}")

        result = await client.call_tool(
            "get_tool_risk",
            {"tool_name": "payment.execute"},
        )

        if result.is_error:
            print("Tool execution failed")

        print("\nTool result:")
        if result.structured_content is not None:
            print(result.structured_content)
        else:
            data = json.loads(result.content[0].text)
            print(f"Risk Level:{data["risk_level"]} | Require Approval: {data["requires_approval"]}")

        total = await client.call_tool(
            "calculate_purchase_total",
            {
                "unit_price": 125.0,
                "quantity": 4,
            },
        )

        print("\nPurchase calculation:")
        print(total.structured_content)


if __name__ == "__main__":
    asyncio.run(main())
