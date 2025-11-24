"""
Visualization Service for generating chart data.
"""
import logging
from typing import Dict, Any, List, Optional, Sequence
from datetime import datetime, timedelta
from collections import defaultdict
from data_processor import TransactionProcessor

logger = logging.getLogger(__name__)

class VisualizationService:
    """Service to generate data for visualizations."""
    
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        
    async def get_spending_trend(self, sessionid: str, period: str = "last_6_months") -> Dict[str, Any]:
        """
        Generate spending trend data for Line Chart.
        Returns data in Google Charts format: [[Label, Value], ...]
        """
        try:
            # Fetch bank transactions
            bank_data = await self.mcp_client.get_bank_transactions(sessionid)
            transactions = TransactionProcessor.parse_bank_transactions(bank_data)
            
            if not transactions:
                return {"error": "No transaction data available"}
                
            # Filter and aggregate by month
            monthly_spending = defaultdict(float)
            
            # Determine date range
            # DEMO HACK: Use fixed date since mock data is from 2024
            end_date = datetime(2024, 8, 1) 
            if period == "last_6_months":
                start_date = end_date - timedelta(days=180)
            elif period == "last_year":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=90) # Default 3 months
                
            for txn in transactions:
                if txn.get('txn_type') == 'DEBIT':
                    try:
                        txn_date = datetime.strptime(txn['date'], '%Y-%m-%d')
                        if start_date <= txn_date <= end_date:
                            month_key = txn_date.strftime('%b %Y')
                            monthly_spending[month_key] += txn.get('amount', 0)
                    except:
                        continue
            
            # Format for Google Charts
            # Header
            chart_data = [["Month", "Spending"]]
            
            # Sort months chronologically
            sorted_months = sorted(monthly_spending.keys(), key=lambda x: datetime.strptime(x, '%b %Y'))
            
            for month in sorted_months:
                chart_data.append([month, monthly_spending[month]])
                
            return {
                "chartType": "LineChart",
                "data": chart_data,
                "options": {
                    "title": "Monthly Spending Trend",
                    "hAxis": {"title": "Month"},
                    "vAxis": {"title": "Amount (₹)"},
                    "legend": {"position": "bottom"}
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating spending trend: {e}")
            return {"error": str(e)}

    async def get_category_breakdown(self, sessionid: str, period: str = "last_month", demo_transactions: Optional[Sequence[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate category breakdown for Pie Chart.
        """
        try:
            # Fetch data from all sources and merge
            bank_data = await self.mcp_client.get_bank_transactions(sessionid)
            mf_data = await self.mcp_client.get_mf_transactions(sessionid)
            stock_data = await self.mcp_client.get_stock_transactions(sessionid)

            transactions = TransactionProcessor.merge_all_transactions(bank_data, mf_data, stock_data)

            # Include demo transactions if provided (API layer may pass them)
            if demo_transactions:
                transactions.extend(demo_transactions)

            if not transactions:
                return {"error": "No transaction data available"}

            category_spending = defaultdict(float)

            # Determine date range
            # DEMO HACK: Use fixed date since mock data is from 2024 when running demo data
            try:
                now = datetime.now()
                # If running in later years without updated mock data, fall back to 2024 demo window
                if now.year > 2024:
                    end_date = datetime(2024, 8, 1)
                else:
                    end_date = now
            except Exception:
                end_date = datetime(2024, 8, 1)

            if period == "last_month":
                start_date = end_date - timedelta(days=30)
            elif period == "last_3_months":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)

            for txn in transactions:
                if txn.get('txn_type') == 'DEBIT':
                    try:
                        txn_date = datetime.strptime(txn['date'], '%Y-%m-%d')
                        if start_date <= txn_date <= end_date:
                            category = txn.get('category', 'Others')
                            category_spending[category] += txn.get('amount', 0)
                    except:
                        continue

            # Aggregate totals and group small categories into 'Others' for clarity
            total_spend = sum(category_spending.values())

            # If nothing to show
            if total_spend <= 0:
                return {"error": "No spending found in the requested period"}

            # Sort categories by amount desc
            sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)

            # Group small slices (<5%) into Others
            threshold = 0.05
            grouped = []
            others_total = 0.0
            for category, amount in sorted_categories:
                if amount / total_spend < threshold:
                    others_total += amount
                else:
                    grouped.append((category, amount))

            if others_total > 0:
                grouped.append(("Others", others_total))

            # Prepare chart data for Google Charts
            chart_data = [["Category", "Amount"]] + [[c, a] for c, a in grouped]

            # Generate a simple color palette
            palette = [
                '#7C3AED', '#06B6D4', '#F97316', '#10B981', '#EF4444', '#3B82F6', '#F59E0B', '#8B5CF6', '#EC4899'
            ]

            # Map slices to colors
            slices = {}
            for i, (category, _) in enumerate(grouped):
                slices[str(i)] = {"color": palette[i % len(palette)]}

            options = {
                "title": f"Spending by Category ({period.replace('_', ' ').title()})",
                "pieHole": 0.35,
                "pieSliceText": 'label',
                "tooltip": {"text": 'percentage'},
                "legend": {"position": 'right', "alignment": 'center', "textStyle": {"fontSize": 12}},
                "chartArea": {"width": '60%', "height": '70%'},
                "slices": slices
            }

            # Also include a simple breakdown list for UI convenience
            breakdown_list = [{"category": c, "amount": a, "percent": round((a/total_spend)*100, 1)} for c, a in grouped]

            return {
                "chartType": "PieChart",
                "data": chart_data,
                "options": options,
                "breakdown": breakdown_list,
                "total": total_spend
            }
            
        except Exception as e:
            logger.error(f"Error generating category breakdown: {e}")
            return {"error": str(e)}

    async def get_investment_portfolio(self, sessionid: str) -> Dict[str, Any]:
        """
        Generate investment portfolio distribution for Pie Chart.
        """
        try:
            # Fetch MF and Stock data
            mf_data = await self.mcp_client.get_mf_transactions(sessionid)
            stock_data = await self.mcp_client.get_stock_transactions(sessionid)
            
            portfolio = defaultdict(float)
            
            # Process Mutual Funds
            if mf_data and 'mfTransactions' in mf_data:
                for fund in mf_data['mfTransactions']:
                    # Calculate current value for each fund
                    # Simple logic: sum of (units * latest_nav)
                    # For hackathon, we'll just sum the investment amounts as a proxy for value
                    # or use the last transaction's price * total units if available.
                    # Let's stick to total invested amount for simplicity and reliability with mock data.
                    total_invested = 0
                    for txn in fund.get('txns', []):
                        # txn schema: [orderType, date, price, units, amount]
                        # orderType 1 is BUY
                        if txn[0] == 1:
                            total_invested += float(txn[4])
                        # orderType 2 is SELL
                        elif txn[0] == 2:
                            total_invested -= float(txn[4])
                            
                    if total_invested > 0:
                        portfolio['Mutual Funds'] += total_invested
                    
            # Process Stocks
            if stock_data and 'stockTransactions' in stock_data:
                for stock in stock_data['stockTransactions']:
                    # Similar logic for stocks if data existed
                    pass
            
            # If no data found, return error
            if not portfolio:
                return {"error": "No investment data found"}
            
            # Format for Google Charts
            chart_data = [["Asset Class", "Value"]]
            for asset, value in portfolio.items():
                chart_data.append([asset, value])
                
            return {
                "chartType": "PieChart",
                "data": chart_data,
                "options": {
                    "title": "Investment Portfolio Allocation",
                    "pieHole": 0.4,
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating investment portfolio: {e}")
            return {"error": str(e)}
