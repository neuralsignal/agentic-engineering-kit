"""Describe a model spec. Thin wrapper around excel-model CLI."""
from excel_model.cli import describe

if __name__ == "__main__":
    describe(standalone_mode=True)
