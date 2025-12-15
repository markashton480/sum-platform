# Repository Hygiene Standards

To maintain a deterministic and quiet development environment, please follow these guidelines.

## Verification

Before pushing code, run the standard suite:

```bash
make format  # Auto-format code
make lint    # Check style and types
make test    # Run tests
```

## Dependencies

- **No ad-hoc `pip install`**: All dependencies must be declared in `pyproject.toml`.
- **No `types-requests`**: Use modern stubs or `mypy` configuration if needed, but avoid ad-hoc type packages if possible.

## Logging in Tests

If you need to test log output where `propagate=False` (e.g. strict logging config), use the `caplog_propagate` fixture:

```python
def test_logging(caplog_propagate):
    with caplog_propagate("my.logger"):
        # run code
    assert "Expected Log" in caplog.text
```
