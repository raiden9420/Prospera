from pathlib import Path
import json
from data_processor import TransactionProcessor

# Path to mock data
p = Path(__file__).resolve().parents[2] / 'fi-mcp-dev' / 'test_data_dir' / '1010101010' / 'fetch_bank_transactions.json'
print('Loading:', p)
raw = json.loads(p.read_text())
transactions = TransactionProcessor.parse_bank_transactions(raw)
print(f'Parsed {len(transactions)} transactions')
# Use last 90 days window around 2024-07-31 to match demo code
from datetime import datetime
start_date = '2024-02-01'
end_date = '2024-09-01'
breakdown = TransactionProcessor.calculate_category_breakdown(transactions, start_date, end_date)
print('Category breakdown:')
print(json.dumps(breakdown, indent=2))
