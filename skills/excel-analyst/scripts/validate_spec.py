"""Validate a model spec YAML. Thin wrapper around excel-model CLI."""
from excel_model.cli import validate

if __name__ == "__main__":
    validate(standalone_mode=True)
