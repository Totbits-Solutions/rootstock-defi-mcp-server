# Rootstock DeFi MCP Server

MCP server for **on-chain DeFi analysis on Rootstock (RSK)**. Allows MCP clients (Claude, Cursor, custom agents) to query token prices, stablecoin health, and lending rates directly from smart contracts.

All data is read in real time from the Rootstock blockchain — no external APIs, no intermediaries.

## Supported Protocols

| Protocol | Type | Tokens / Markets | Description |
|---|---|---|---|
| **Money on Chain (MoC)** | Pricing + Stablecoin | RBTC, BPRO, DOC | BTC-collateralized stablecoin system. DOC pegged to USD, BPRO is the leveraged token |
| **RIF on Chain V2 (RoC)** | Pricing + Stablecoin | RIF, RIFPRO, USDRIF | RIF-collateralized stablecoin system. USDRIF pegged to USD, RIFPRO is the leveraged token |
| **Tropykus** | Lending | kRBTC, kDOC, kUSDRIF, kBPRO | Compound v2 fork. Supply/borrow markets with per-block rate conversion |
| **Sovryn** | Lending | iRBTC, iDOC, iUSDT, iBPro, iXUSD, iDLLR | bZx fork. Supply/borrow markets with annualized rates |

## Available Tools

### `get_token_prices`

Query current token prices from on-chain oracles.

**Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `tokens` | `list[str]` | No | Filter by tokens. Valid: `RBTC`, `BPRO`, `RIF`, `RIFPRO`, `DOC`, `USDRIF`. Omit for all |

**Example response:**
```json
[
  {
    "token": "RBTC",
    "price_usd": 67000.0,
    "price_btc": 1.0,
    "source": "MoC oracle",
    "protocol": "moc"
  },
  {
    "token": "DOC",
    "price_usd": 1.0,
    "source": "MoC protocol",
    "protocol": "moc"
  }
]
```

---

### `get_stablecoin_health`

Analyze stablecoin peg health and protocol coverage. Only **DOC** and **USDRIF** are supported.

**Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `tokens` | `list[str]` | No | Filter by stablecoins. Valid: `DOC`, `USDRIF`. Omit for all |

**Example response:**
```json
[
  {
    "token": "DOC",
    "protocol_price_usd": 1.0,
    "market_price_usd": 0.9953,
    "peg_deviation_pct": -0.47,
    "collateral": {
      "asset": "RBTC",
      "locked_amount": 62.85,
      "value_usd": 4661362.0
    },
    "coverage": {
      "current": 9.15,
      "target": 4.0,
      "liquidation_threshold": 1.04
    },
    "supply": {
      "DOC": 4666729.0,
      "BPRO": 430.4
    },
    "status": "HEALTHY",
    "protocol": "moc"
  }
]
```

**Status values:** `HEALTHY` (coverage > target), `WARNING` (coverage > liquidation but below target), `LIQUIDATION_RISK` (coverage below liquidation threshold).

---

### `get_lending_rates`

Get supply and borrow rates (APR/APY) for lending markets. Only **Tropykus** and **Sovryn** are supported.

**Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `protocol` | `str` | No | Filter by protocol. Valid: `tropykus`, `sovryn`. Omit for all |
| `market` | `str` | No | Filter by market (e.g. `kDOC`, `iRBTC`). **Requires `protocol`** |

**Example response:**
```json
[
  {
    "market": "kDOC",
    "protocol": "tropykus",
    "rates": {
      "supply_apr": 5.85,
      "supply_apy": 6.03,
      "borrow_apr": 10.99,
      "borrow_apy": 11.61
    },
    "pool": {
      "total_supply_usd": 3665876.0,
      "total_borrows_usd": 3247711.0,
      "available_liquidity_usd": 418164.0,
      "utilization_rate": 88.77
    }
  }
]
```

## Requirements

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/)

## Installation

```bash
git clone https://github.com/Totbits-Solutions/rootstock-defi-mcp-server.git
cd rootstock-defi-mcp-server
uv sync
cp .env.example .env
```

## Configuration

Environment variables (prefix `MCP_`, nested with `__`):

| Variable | Description | Default |
|---|---|---|
| `MCP_RSK_NODE_URL` | Rootstock RPC node URL | `https://public-node.rsk.co` |
| `MCP_LOG_LEVEL` | Log level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `MCP_LOG_FORMAT` | Log format (`pretty` for dev, `json` for prod) | `pretty` |

All tools are **read-only** (on-chain queries only, no transactions). The default `.env.example` values work without changes.

## AI Client Configuration

The server runs locally via **stdio** transport. Add it to your MCP client configuration:

### Claude Desktop

File: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "rootstock-defi": {
      "command": "uv",
      "args": ["run", "python", "run_server.py"],
      "cwd": "/absolute/path/to/rootstock-defi-mcp-server"
    }
  }
}
```

### Claude Code

File: `.mcp.json` in your project root (or `~/.claude/mcp.json` for global)

```json
{
  "mcpServers": {
    "rootstock-defi": {
      "command": "uv",
      "args": ["run", "python", "run_server.py"],
      "cwd": "/absolute/path/to/rootstock-defi-mcp-server"
    }
  }
}
```

### Cursor

File: `.cursor/mcp.json` in your project root

```json
{
  "mcpServers": {
    "rootstock-defi": {
      "command": "uv",
      "args": ["run", "python", "run_server.py"],
      "cwd": "/absolute/path/to/rootstock-defi-mcp-server"
    }
  }
}
```

> **Note:** Replace `/absolute/path/to/rootstock-defi-mcp-server` with the actual path where you cloned the repo.

### Testing with MCP Inspector

To visually explore and test the tools:

```bash
npx @modelcontextprotocol/inspector uv run python run_server.py
```

Open the printed URL, click **Connect**, go to **Tools** > **List Tools**.

## Development

```bash
uv run pytest -v                        # run all tests
uv run pytest tests/unit/ -v            # unit tests only
uv run pytest -k "test_name"            # single test by name
uv run ruff check src/ tests/           # lint
uv run ruff format src/ tests/          # format
uv run mypy src/                        # type check
uv run pre-commit run --all-files       # run all pre-commit hooks
```

Pre-commit hooks (ruff lint + format, trailing whitespace, end-of-file) run automatically on every `git commit`.

## Architecture

The server follows a **hexagonal architecture** (ports and adapters) with two bounded contexts:

```
src/
  domain/
    pricing/        # Token prices + stablecoin health (MoC, RoC V2)
    lending/        # Supply/borrow rates (Tropykus, Sovryn)
    shared/         # Token, Protocol enums, exceptions, gateway port
  infrastructure/
    blockchain/     # Web3 gateway, contract registry, constants
    providers/      # Adapters implementing domain ports
  application/      # Use cases (orchestration, no business logic)
  tools/            # MCP tool functions (@mcp.tool decorators)
  server.py         # FastMCP instance + async lifespan for DI
  dependencies.py   # Service getters from lifespan context
  config.py         # Pydantic Settings (env vars)
```

Data flows inward: **Tool** > **Use Case** > **Domain Service** > **Provider (adapter)** > **Blockchain Gateway**.

The domain layer has zero dependencies on infrastructure — providers implement domain ports (ABCs), injected at startup via the lifespan context.

## License

[MIT](LICENSE) - Totbits Solutions
