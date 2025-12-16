from __future__ import annotations

import sys

from sum_cli.cli import main as _main


def main() -> None:
    sys.exit(_main())


if __name__ == "__main__":
    main()
