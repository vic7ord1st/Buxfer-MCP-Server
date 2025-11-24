# Buxfer MCP Server

A Model Context Protocol (MCP) server for managing [Buxfer](https://www.buxfer.com/) transactions and accounts. This server allows Claude to interact with your financial data securely, enabling you to add transactions, check balances, and analyze spending using natural language.

## Features

- **Add Transactions**: Record expenses, income, transfers, and loans.
- **List Accounts**: View all your Buxfer accounts with current balances and sync status.
- **List Transactions**: Query your transaction history with powerful filters (date, tag, account, status).
- **Secure Authentication**: Uses token-based authentication stored locally.
- **Dockerized**: Runs in an isolated container for security and consistency.

## Prerequisites

- **Docker**: Ensure Docker is installed and running on your system. [Get Docker](https://docs.docker.com/get-docker/)
- **Buxfer Account**: You need a Buxfer account.
- **Claude Desktop**: The [Claude Desktop app](https://claude.ai/download) is required to use this MCP server.

## Installation

### 1. Get Your Buxfer Token

You need an API token to authenticate with Buxfer.

1.  Open your terminal.
2.  Run the following command (replace with your actual email and password):

    ```bash
    curl -X POST https://www.buxfer.com/api/login \
      -d "email=YOUR_EMAIL" \
      -d "password=YOUR_PASSWORD"
    ```

3.  Copy the `token` from the response. **Keep this secure.**

### 2. Build the Docker Image

Navigate to the project directory and build the Docker image:

```bash
cd buxfer-mcp-server
docker build -t buxfer-mcp-server .
```

### 3. Configure Claude Desktop

Add the server configuration to your Claude Desktop config file.

-   **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
-   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following to the `mcpServers` object (replace `YOUR_BUXFER_TOKEN` with the token you obtained in Step 1):

```json
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
```

### 4. Restart Claude Desktop

Completely quit and restart the Claude Desktop application for the changes to take effect.

## Usage

Once installed, you can interact with your Buxfer data using natural language in Claude.

### Managing Accounts

-   "Show me all my Buxfer accounts"
-   "What is the balance of my Checking account?"
-   "List my accounts and their last sync times"

### Adding Transactions

-   "Add a $50 grocery expense to my Cash account"
-   "Record a $2000 paycheck as income to my Checking account"
-   "Log a $30 lunch expense with tag 'dining'"
-   "Add a pending transfer of $500 from Savings to Checking"

### Viewing Transactions

-   "Show me my recent transactions"
-   "List all expenses from last month"
-   "Find all transactions tagged 'travel' from January 2024"
-   "Show me pending transactions in my Credit Card account"

## Troubleshooting

| Problem | Solution |
| :--- | :--- |
| **Server not showing up** | Restart Claude Desktop. Check `claude_desktop_config.json` syntax. Verify Docker image exists (`docker images`). |
| **"BUXFER_TOKEN not set"** | Check the config file. Ensure `BUXFER_TOKEN` is passed in `args`. Verify token validity. |
| **Connection Refused** | Check internet connection. Ensure Docker is running. |
| **Build Fails** | Verify `requirements.txt` and `Dockerfile` are present. Check Docker daemon status. |

## Security

-   **Token Safety**: Your Buxfer token is sensitive. Never share it or commit it to version control.
-   **Local Storage**: The token is stored only in your local Claude configuration.
-   **HTTPS**: All communication with Buxfer is encrypted via HTTPS.
-   **Containerization**: The server runs in a secure, isolated Docker container.

## Technical Details

-   **Language**: Python 3.11
-   **Framework**: FastMCP
-   **Transport**: stdio
-   **API**: Buxfer API v1

## License

This project is for personal use. Use at your own discretion.
