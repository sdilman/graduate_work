# How to run application and tests

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# Sync packages to local environment
uv sync --frozen
# ❗ setup pre-commit for local environment
make setup_precommit
# To install dependencies
cd services/billing
# For app
uv add 'package'
# For tests common
uv add 'package' --optional test
# For tests functional
uv add 'package' --optional test-functional
# For tests integration
uv add 'package' --optional test-integration
```

See Makefile for commands
