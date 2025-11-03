================================================================================
BUXFER MCP SERVER - README
================================================================================

OVERVIEW
--------
A Model Context Protocol (MCP) server for managing Buxfer transactions and accounts.
This server provides three main tools:
1. Add transactions to Buxfer
2. List all accounts with balances
3. List transactions with filtering options

FEATURES
--------
✅ Add new transactions (expense, income, transfer, loan, etc.)
✅ List all accounts with current balances
✅ List transactions with filters (account, date range, tags, status)
✅ Pagination support for large transaction lists
✅ Formatted, readable responses
✅ Docker-based deployment for isolation
✅ Automatic token authentication via environment variable

REQUIREMENTS
------------
- Docker installed on your system
- Buxfer API token (obtain by logging in to https://www.buxfer.com/api/login)
- Claude Desktop application

INSTALLATION INSTRUCTIONS
-------------------------

STEP 1: GET YOUR BUXFER TOKEN
------------------------------
You need to obtain your Buxfer API token first:

1. Make a POST request to https://www.buxfer.com/api/login
   with your email and password:
   
   curl -X POST https://www.buxfer.com/api/login \
     -d "email=YOUR_EMAIL" \
     -d "password=YOUR_PASSWORD"
   
2. The response will contain a "token" field - copy this token.
3. Keep this token secure - you'll need it for configuration.

STEP 2: BUILD THE DOCKER IMAGE
-------------------------------
Navigate to the directory containing these files and run:

cd buxfer-mcp-server
docker build -t buxfer-mcp-server .

STEP 3: CONFIGURE CLAUDE DESKTOP
---------------------------------
Edit your Claude Desktop configuration file:

MacOS: ~/Library/Application Support/Claude/claude_desktop_config.json
Windows: %APPDATA%\Claude\claude_desktop_config.json

Add this configuration (replace YOUR_BUXFER_TOKEN with your actual token):

{
  "mcpServers": {
    "buxfer": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "BUXFER_TOKEN=YOUR_BUXFER_TOKEN",
        "buxfer-mcp-server"
      ]
    }
  }
}

If you already have other MCP servers configured, add the "buxfer" entry
to your existing "mcpServers" object.

STEP 4: RESTART CLAUDE DESKTOP
-------------------------------
Completely quit and restart Claude Desktop for the changes to take effect.

STEP 5: VERIFY INSTALLATION
----------------------------
In Claude Desktop, you should see the Buxfer tools available. You can verify by:
- Checking the available tools list
- Asking Claude to "list my Buxfer accounts"

AVAILABLE TOOLS
---------------

1. add_transaction
   - Description: Add a new transaction to Buxfer
   - Parameters:
     * description (required): Transaction description
     * amount (required): Transaction amount
     * account_id OR account_name (required): Target account
     * date (optional): Date in YYYY-MM-DD format
     * tags (optional): Comma-separated tags
     * transaction_type (optional): expense/income/transfer/loan (default: expense)
     * status (optional): cleared/pending (default: cleared)
   
   Example: "Add a $50 grocery expense to my Cash account"

2. list_accounts
   - Description: Get all Buxfer accounts with balances
   - Parameters: None
   
   Example: "Show me all my Buxfer accounts"

3. list_transactions
   - Description: Get transactions with filtering options
   - Parameters (all optional):
     * account_id: Filter by account ID
     * account_name: Filter by account name
     * tag_name: Filter by tag
     * start_date: Start date (YYYY-MM-DD)
     * end_date: End date (YYYY-MM-DD)
     * month: Filter by month (e.g., "jan 2024")
     * status: Filter by status (pending/cleared/reconciled)
     * page: Page number for pagination (default: 1)
   
   Example: "Show me all transactions from my Amex account this month"

USAGE EXAMPLES
--------------

1. List all accounts:
   "Show me all my Buxfer accounts"

2. Add an expense:
   "Add a $25 lunch expense to my Cash account with tag 'food'"

3. View recent transactions:
   "Show me my recent transactions from my checking account"

4. Filter by date:
   "Show me all transactions from January 2024"

5. Check specific account:
   "List all pending transactions in my Credit Card account"

TROUBLESHOOTING
---------------

Problem: Server doesn't appear in Claude Desktop
Solution: 
- Verify the Docker image was built successfully
- Check the configuration file syntax (must be valid JSON)
- Restart Claude Desktop completely
- Check Docker is running: docker ps

Problem: "BUXFER_TOKEN not set" error
Solution:
- Verify you added your token to the configuration file
- Make sure the token is correct (no extra spaces)
- Restart Claude Desktop after updating the config

Problem: "Connection refused" or timeout errors
Solution:
- Check your internet connection
- Verify the Buxfer API is accessible
- Try refreshing your token (tokens may expire)

Problem: Docker image fails to build
Solution:
- Ensure Docker is installed and running
- Check that all files are in the correct directory
- Verify requirements.txt contains the correct dependencies

TOKEN SECURITY
--------------
⚠️ IMPORTANT: Your Buxfer token provides access to your financial data.

- Never share your token publicly
- Don't commit it to version control
- Store it securely in the Claude Desktop config file
- The token is only stored locally on your machine
- Tokens may expire - regenerate if API calls fail

SUPPORT
-------
For issues with:
- MCP Server: Check the logs in Claude Desktop
- Buxfer API: Visit https://www.buxfer.com/help/api/
- Docker: Visit https://docs.docker.com/

TECHNICAL DETAILS
-----------------
- Language: Python 3.11
- Framework: FastMCP
- HTTP Client: httpx
- Transport: stdio
- Container: Docker (non-root user)

API REFERENCE
-------------
This server uses the Buxfer API v1:
- Base URL: https://www.buxfer.com/api
- Authentication: Token-based (query parameter)
- Documentation: https://www.buxfer.com/help/api/

UPDATES AND MAINTENANCE
-----------------------
To update the server:
1. Modify the source files as needed
2. Rebuild the Docker image:
   docker build -t buxfer-mcp-server .
3. Restart Claude Desktop

To check server logs:
- Logs are written to stderr
- View them in Claude Desktop's developer console

VERSION INFORMATION
-------------------
Version: 1.0.0
Last Updated: 2024
License: Use at your own discretion

================================================================================
