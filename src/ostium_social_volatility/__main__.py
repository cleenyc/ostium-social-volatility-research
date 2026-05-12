from __future__ import annotations

import sys

from ostium_social_volatility import pipeline, validate


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("Usage: python -m ostium_social_volatility <validate|report|run> [args...]", file=sys.stderr)
        return 2
    command, rest = args[0], args[1:]
    if command == "validate":
        return validate.main(rest)
    if command == "report":
        return pipeline.report_main(rest)
    if command == "run":
        return pipeline.run_main(rest)
    print(f"Unknown command: {command}", file=sys.stderr)
    print("Available commands: validate, report, run", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
