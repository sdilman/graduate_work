# How to run application and tests

```bash
# Sync project dependencies
make setup
```

```bash
# https://docs.astral.sh/uv/reference/cli/
# ❗ Example: How to add package to project for de
uv add 'package_name_example' --dev
# ❗ Example: How to manage dependencies for particular service
# For core
uv add --package billing 'package_name_example'
# For optional tests common
uv add --package billing 'package_name_example' --optional test
# For optional tests functional
uv add --package billing 'package_name_example' --optional test-functional
# For optional tests integration
uv add --package billing 'package_name_example' --optional test-integration
# For removing package
uv remove --package billing 'package_name_example' '--optional test | test-functional | test-integration'
```

See Makefile for commands
