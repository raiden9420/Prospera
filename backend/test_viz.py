import asyncio
from visualization import VisualizationService
from unittest.mock import AsyncMock, MagicMock

async def test_visualization():
    # Mock MCP Client
    mock_mcp = AsyncMock()
    
    # Mock bank transactions
    mock_transactions = {
        "bankTransactions": [
            {
                "txns": [
                    # amount, narration, date, type_int (2=DEBIT, 1=CREDIT)
                    ["100.0", "Lunch", "2024-05-15", "2"],
                    ["200.0", "Uber", "2024-06-20", "2"],
                    ["5000.0", "Salary", "2024-07-10", "1"]
                ]
            }
        ]
    }
    mock_mcp.get_bank_transactions.return_value = mock_transactions
    
    service = VisualizationService(mock_mcp)
    
    print("Testing get_spending_trend...")
    try:
        result = await service.get_spending_trend("test_session")
        print("Result:", result)
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_visualization())
