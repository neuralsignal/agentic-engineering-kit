"""Build an Excel financial model. Thin wrapper around excel-model CLI."""
from excel_model.cli import build

if __name__ == "__main__":
    build(standalone_mode=True)
