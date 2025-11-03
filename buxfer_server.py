#!/usr/bin/env python3
"""
Simple Buxfer MCP Server - Manage your Buxfer transactions and accounts
"""
import os
import sys
import logging
from datetime import datetime
import json
import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("buxfer-server")

# Initialize MCP server - NO PROMPT PARAMETER!
mcp = FastMCP("buxfer")

# Configuration
BUXFER_API_BASE = "https://www.buxfer.com/api"
BUXFER_TOKEN = os.environ.get("BUXFER_TOKEN", "")

# === UTILITY FUNCTIONS ===

def format_account(account):
    """Format a single account for display."""
    balance = account.get("balance", 0)
    last_synced = account.get("lastSynced", "Never")
    return f"• {account.get('name', 'Unknown')} ({account.get('bank', 'N/A')})\n  ID: {account.get('id', 'N/A')}\n  Balance: ${balance:,.2f}\n  Last Synced: {last_synced}"

def format_transaction(txn):
    """Format a single transaction for display."""
    amount = txn.get("amount", 0)
    txn_type = txn.get("type", "unknown")
    status = txn.get("status", "")
    tags = txn.get("tags", "")
    account_name = txn.get("accountName", "Unknown")
    
    result = f"• {txn.get('description', 'No description')} ({txn.get('date', 'No date')})\n"
    result += f"  ID: {txn.get('id', 'N/A')}\n"
    result += f"  Type: {txn_type} | Amount: ${amount:,.2f}\n"
    result += f"  Account: {account_name}"
    
    if status:
        result += f" | Status: {status}"
    if tags:
        result += f" | Tags: {tags}"
    
    extra_info = txn.get("extraInfo", "")
    if extra_info:
        result += f"\n  Info: {extra_info}"
    
    return result

async def make_buxfer_request(method, endpoint, params=None, data=None):
    """Make a request to the Buxfer API."""
    if not BUXFER_TOKEN:
        raise ValueError("BUXFER_TOKEN environment variable not set")
    
    url = f"{BUXFER_API_BASE}/{endpoint}"
    
    # Add token to query params
    if params is None:
        params = {}
    params["token"] = BUXFER_TOKEN
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        if method.upper() == "GET":
            response = await client.get(url, params=params)
        elif method.upper() == "POST":
            response = await client.post(url, params=params, data=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        result = response.json()
        
        # Check for API-level errors
        if "response" in result:
            status = result["response"].get("status", "")
            if status.startswith("ERROR"):
                raise ValueError(f"Buxfer API error: {status}")
        
        return result

# === MCP TOOLS ===

@mcp.tool()
async def add_transaction(description: str = "", amount: str = "", account_id: str = "", account_name: str = "", date: str = "", tags: str = "", transaction_type: str = "expense", status: str = "cleared") -> str:
    """Add a new transaction to Buxfer with description, amount, account, date, tags, type (expense/income/transfer/loan/etc), and status (cleared/pending)."""
    logger.info(f"Adding transaction: {description}")
    
    try:
        if not description:
            return "❌ Error: Description is required"
        if not amount:
            return "❌ Error: Amount is required"
        if not account_id and not account_name:
            return "❌ Error: Either account_id or account_name is required"
        
        # Prepare data
        data = {
            "description": description,
            "amount": amount,
            "type": transaction_type,
            "status": status
        }
        
        if account_id:
            data["accountId"] = account_id
        if account_name:
            data["accountName"] = account_name
        if date:
            data["date"] = date
        if tags:
            data["tags"] = tags
        
        result = await make_buxfer_request("POST", "transaction_add", data=data)
        
        if "response" in result:
            txn = result["response"]
            response_text = "✅ Transaction added successfully!\n\n"
            response_text += f"ID: {txn.get('id', 'N/A')}\n"
            response_text += f"Description: {txn.get('description', 'N/A')}\n"
            response_text += f"Amount: ${txn.get('amount', 0):,.2f}\n"
            response_text += f"Type: {txn.get('type', 'N/A')}\n"
            response_text += f"Date: {txn.get('date', 'N/A')}\n"
            response_text += f"Account: {txn.get('accountName', 'N/A')}\n"
            response_text += f"Status: {txn.get('status', 'N/A')}"
            
            if txn.get('tags'):
                response_text += f"\nTags: {txn.get('tags')}"
            
            return response_text
        
        return "❌ Error: Unexpected response format from Buxfer API"
        
    except Exception as e:
        logger.error(f"Error adding transaction: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def list_accounts() -> str:
    """Get all Buxfer accounts with their current balances, IDs, banks, and last sync times."""
    logger.info("Fetching accounts list")
    
    try:
        result = await make_buxfer_request("GET", "accounts")
        
        if "response" in result and "accounts" in result["response"]:
            accounts = result["response"]["accounts"]
            
            if not accounts:
                return "ℹ️ No accounts found"
            
            response_text = f"📊 **Buxfer Accounts** ({len(accounts)} total)\n\n"
            
            for account in accounts:
                response_text += format_account(account) + "\n\n"
            
            # Calculate total balance
            total_balance = sum(acc.get("balance", 0) for acc in accounts)
            response_text += f"**Total Balance: ${total_balance:,.2f}**"
            
            return response_text
        
        return "❌ Error: Unexpected response format from Buxfer API"
        
    except Exception as e:
        logger.error(f"Error listing accounts: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def list_transactions(account_id: str = "", account_name: str = "", tag_name: str = "", start_date: str = "", end_date: str = "", month: str = "", status: str = "", page: str = "1") -> str:
    """Get transactions from Buxfer with optional filters: account_id, account_name, tag_name, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), month (e.g. 'jan 2024'), status (pending/cleared/reconciled), page number for pagination."""
    logger.info("Fetching transactions")
    
    try:
        params = {}
        
        if account_id:
            params["accountId"] = account_id
        if account_name:
            params["accountName"] = account_name
        if tag_name:
            params["tagName"] = tag_name
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if month:
            params["month"] = month
        if status:
            params["status"] = status
        if page:
            params["page"] = page
        
        result = await make_buxfer_request("GET", "transactions", params=params)
        
        if "response" in result and "transactions" in result["response"]:
            transactions = result["response"]["transactions"]
            num_total = result["response"].get("numTransactions", 0)
            
            if not transactions:
                return "ℹ️ No transactions found matching your criteria"
            
            current_page = int(page) if page else 1
            response_text = f"📋 **Buxfer Transactions** (Page {current_page}, {len(transactions)} of {num_total} total)\n\n"
            
            # Add filter info if filters were applied
            filters_applied = []
            if account_name:
                filters_applied.append(f"Account: {account_name}")
            elif account_id:
                filters_applied.append(f"Account ID: {account_id}")
            if tag_name:
                filters_applied.append(f"Tag: {tag_name}")
            if start_date and end_date:
                filters_applied.append(f"Date: {start_date} to {end_date}")
            elif month:
                filters_applied.append(f"Month: {month}")
            if status:
                filters_applied.append(f"Status: {status}")
            
            if filters_applied:
                response_text += f"**Filters:** {', '.join(filters_applied)}\n\n"
            
            for txn in transactions:
                response_text += format_transaction(txn) + "\n\n"
            
            # Add pagination info
            if num_total > len(transactions):
                total_pages = (num_total + 99) // 100  # Round up
                response_text += f"**Page {current_page} of {total_pages}** (Use page parameter to view more)"
            
            return response_text
        
        return "❌ Error: Unexpected response format from Buxfer API"
        
    except Exception as e:
        logger.error(f"Error listing transactions: {e}")
        return f"❌ Error: {str(e)}"

# === SERVER STARTUP ===
if __name__ == "__main__":
    logger.info("Starting Buxfer MCP server...")
    
    if not BUXFER_TOKEN:
        logger.warning("BUXFER_TOKEN not set - server will not be able to make API calls")
    
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
