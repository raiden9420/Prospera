
# backend/data_processor.py
"""
Processes and categorizes financial transactions.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any

class TransactionProcessor:
    """
    A class to process, categorize, and analyze financial transactions.
    """

    @staticmethod
    def parse_bank_transactions(bank_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parses raw bank transaction data into a structured list of transactions.
        """
        transactions = []
        if not bank_data or 'bankTransactions' not in bank_data:
            return transactions

        for account in bank_data.get('bankTransactions', []):
            for txn in account.get('txns', []):
                try:
                    txn_type_int = int(txn[3])
                    txn_type = 'CREDIT'
                    if txn_type_int in [2, 6, 8]:
                        txn_type = 'DEBIT'

                    transactions.append({
                        'date': txn[2],
                        'amount': float(txn[0]),
                        'narration': txn[1],
                        'txn_type': txn_type,
                        'category': TransactionProcessor.categorize_transaction(txn[1]),
                    })
                except (ValueError, IndexError):
                    continue
        return transactions

    @staticmethod
    def categorize_transaction(narration: str) -> str:
        """
        Categorizes a transaction based on its narration.
        """
        if not narration:
            return "Others"

        narration_lower = narration.lower()

        if "salary" in narration_lower:
            return "Salary"
        if any(keyword in narration_lower for keyword in ["rent", "landlord"]):
            return "Rent"
        if any(keyword in narration_lower for keyword in ["emi", "loan"]):
            return "EMI"
        if any(keyword in narration_lower for keyword in ["investment", "sip", "mutual fund"]):
            return "Investment"
        if any(keyword in narration_lower for keyword in ["food", "restaurant", "swiggy", "zomato"]):
            return "Food"
        if any(keyword in narration_lower for keyword in ["transport", "uber", "ola", "taxi"]):
            return "Transport"
        if any(keyword in narration_lower for keyword in ["shopping", "amazon", "flipkart", "myntra"]):
            return "Shopping"
        if any(keyword in narration_lower for keyword in ["bills", "electricity", "water", "internet"]):
            return "Bills"
        if "credit card" in narration_lower:
            return "Credit Card Payment"
        if any(keyword in narration_lower for keyword in ["entertainment", "movie", "netflix", "spotify"]):
            return "Entertainment"
        
        return "Others"
    
    @staticmethod
    def merge_all_transactions(bank_data, mf_data, stock_data) -> List[Dict[str, Any]]:
        """
        Merge transactions from all sources into a single list.
        """
        transactions = []

        # Bank transactions
        if bank_data and 'bankTransactions' in bank_data:
            for account in bank_data.get('bankTransactions', []):
                for txn in account.get('txns', []):
                    try:
                        txn_type_int = int(txn[3])
                        txn_type = 'CREDIT'
                        if txn_type_int in [2, 6, 8]:
                            txn_type = 'DEBIT'
                        
                        transactions.append({
                            'date': txn[2],
                            'amount': float(txn[0]),
                            'narration': txn[1],
                            'txn_type': txn_type,
                            'category': TransactionProcessor.categorize_transaction(txn[1]),
                            'source': 'bank'
                        })
                    except (ValueError, IndexError):
                        continue

        # Mutual fund transactions
        if mf_data and 'mfTransactions' in mf_data:
            for mf in mf_data.get('mfTransactions', []):
                for txn in mf.get('txns', []):
                    try:
                        transactions.append({
                            'date': txn[1],
                            'amount': float(txn[4]),
                            'narration': mf.get('schemeName'),
                            'txn_type': 'DEBIT' if int(txn[0]) == 1 else 'CREDIT',
                            'category': 'Investment',
                            'source': 'mf'
                        })
                    except (ValueError, IndexError):
                        continue

        # Stock transactions
        if stock_data and 'stockTransactions' in stock_data:
            for stock in stock_data.get('stockTransactions', []):
                for txn in stock.get('txns', []):
                    try:
                        transactions.append({
                            'date': txn[1],
                            'amount': float(txn[4]),
                            'narration': stock.get('stockName'),
                            'txn_type': 'DEBIT' if int(txn[0]) == 1 else 'CREDIT',
                            'category': 'Investment',
                            'source': 'stock'
                        })
                    except (ValueError, IndexError):
                        continue
        
        return transactions

    @staticmethod
    def get_payment_nudges(bank_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identifies potential upcoming payments based on recurring transactions.
        """
        # This is a simplified implementation. A real-world scenario would involve
        # more sophisticated pattern detection.
        
        transactions = TransactionProcessor.parse_bank_transactions(bank_data)
        
        # Look for recurring debits in the last 90 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        recurring_candidates = {}
        for txn in transactions:
            try:
                txn_date = datetime.strptime(txn['date'], '%Y-%m-%d')
                if start_date <= txn_date <= end_date and txn['txn_type'] == 'DEBIT':
                    # Group by narration and amount
                    key = (txn['narration'], txn['amount'])
                    if key not in recurring_candidates:
                        recurring_candidates[key] = []
                    recurring_candidates[key].append(txn_date)
            except (ValueError, TypeError):
                continue

        nudges = []
        for (narration, amount), dates in recurring_candidates.items():
            if len(dates) > 1:  # More than one occurrence
                # Simple check for monthly recurrence
                dates.sort()
                gaps = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
                avg_gap = sum(gaps) / len(gaps)
                
                if 25 <= avg_gap <= 35:
                    last_payment_date = dates[-1]
                    next_payment_date = last_payment_date + timedelta(days=30)
                    
                    if next_payment_date > end_date:
                        nudges.append({
                            "category": TransactionProcessor.categorize_transaction(narration),
                            "merchant": narration,
                            "amount": amount,
                            "due_date": next_payment_date.strftime('%Y-%m-%d'),
                            "days_away": (next_payment_date - end_date).days,
                            "type": "recurring_payment"
                        })
        return nudges

    @staticmethod
    def calculate_daily_spend(transactions: List[Dict[str, Any]], from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """
        Calculates daily spending aggregates for a given date range.
        """
        daily_spend = {}
        start = datetime.strptime(from_date, '%Y-%m-%d')
        end = datetime.strptime(to_date, '%Y-%m-%d')

        for txn in transactions:
            try:
                txn_date = datetime.strptime(txn['date'], '%Y-%m-%d')
                if start <= txn_date <= end and (txn.get('txn_type') == 'DEBIT' or txn.get('type') == 'expense'):
                    date_str = txn_date.strftime('%Y-%m-%d')
                    daily_spend[date_str] = daily_spend.get(date_str, 0) + txn['amount']
            except (ValueError, TypeError):
                continue
        
        # Format for chart
        return [{"date": date, "amount": amount} for date, amount in sorted(daily_spend.items())]

    @staticmethod
    def calculate_monthly_spend(transactions: List[Dict[str, Any]], from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """
        Calculates monthly spending aggregates for a given date range.
        """
        monthly_spend = {}
        start = datetime.strptime(from_date, '%Y-%m-%d')
        end = datetime.strptime(to_date, '%Y-%m-%d')

        for txn in transactions:
            try:
                txn_date = datetime.strptime(txn['date'], '%Y-%m-%d')
                if start <= txn_date <= end and (txn.get('txn_type') == 'DEBIT' or txn.get('type') == 'expense'):
                    month_str = txn_date.strftime('%Y-%m')
                    monthly_spend[month_str] = monthly_spend.get(month_str, 0) + txn['amount']
            except (ValueError, TypeError):
                continue
        
        # Format for chart
        return [{"month": month, "amount": amount} for month, amount in sorted(monthly_spend.items())]

    @staticmethod
    def calculate_category_breakdown(transactions: List[Dict[str, Any]], from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """
        Calculates spending breakdown by category for a given date range.
        """
        category_spend = {}
        start = datetime.strptime(from_date, '%Y-%m-%d')
        end = datetime.strptime(to_date, '%Y-%m-%d')

        for txn in transactions:
            try:
                txn_date = datetime.strptime(txn['date'], '%Y-%m-%d')
                if start <= txn_date <= end and (txn.get('txn_type') == 'DEBIT' or txn.get('type') == 'expense'):
                    category = txn.get('category', 'Others')
                    category_spend[category] = category_spend.get(category, 0) + txn['amount']
            except (ValueError, TypeError):
                continue
        
        # Format for chart
        return [{"category": category, "amount": amount} for category, amount in sorted(category_spend.items(), key=lambda item: item[1], reverse=True)]

    @staticmethod
    def whatif_simulator(scenario: str, **kwargs) -> Dict[str, Any]:
        """
        Runs what-if financial simulations.
        """
        if scenario == 'mf_return':
            amount = kwargs.get('amount', 100000)
            horizon_months = kwargs.get('horizon_months', 60)
            annual_rate = kwargs.get('annual_rate', 0.12)
            
            monthly_rate = (1 + annual_rate)**(1/12) - 1
            future_value = amount * ((1 + monthly_rate)**horizon_months)
            
            return {
                "scenario": "Mutual Fund Returns",
                "investment": amount,
                "horizon_months": horizon_months,
                "annual_rate_percent": annual_rate * 100,
                "future_value": round(future_value, 2),
                "total_growth": round(future_value - amount, 2)
            }
            
        elif scenario == 'spend_reduction':
            percent = kwargs.get('percent', 10)
            avg_monthly_spend = kwargs.get('avg_monthly_spend', 50000)
            
            monthly_savings = avg_monthly_spend * (percent / 100)
            annual_savings = monthly_savings * 12
            
            return {
                "scenario": "Spending Reduction",
                "reduction_percent": percent,
                "avg_monthly_spend": avg_monthly_spend,
                "monthly_savings": round(monthly_savings, 2),
                "annual_savings": round(annual_savings, 2)
            }
            
        else:
            return {"error": "Invalid scenario"}
