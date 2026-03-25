# Rootstock DeFi MCP Server

Servidor MCP para analisis DeFi on-chain en Rootstock (RSK). Permite a clientes MCP (Claude, GPT, agentes custom) consultar precios de tokens, salud de stablecoins y tasas de lending directamente desde smart contracts.

Protocolos soportados: **Money on Chain**, **RIF on Chain V2**, **Tropykus**, **Sovryn**.

## Requisitos

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/)

## Instalacion

```bash
git clone <repo-url>
cd rootstock-defi-mcp-server
uv sync
```

## Configuracion

```bash
cp .env.example .env
```

Variables de entorno (prefijo `MCP_`):

| Variable | Descripcion | Default |
|----------|-------------|---------|
| `MCP_RSK_NODE_URL` | URL del nodo RPC de Rootstock | `https://public-node.rsk.co` |
| `MCP_LOG_LEVEL` | Nivel de logging (DEBUG, INFO, WARNING, ERROR) | `INFO` |

## Uso

```bash
# Arrancar el servidor (stdio)
uv run python run_server.py

# Listar tools disponibles
uv run fastmcp list run_server.py
```

## Desarrollo

```bash
uv run pytest -v                # ejecutar tests
uv run ruff check src/          # lint
uv run ruff format src/         # formatear
```
