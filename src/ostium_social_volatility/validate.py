from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


@dataclass
class CheckResult:
    level: str
    name: str
    message: str


@dataclass
class ValidationReport:
    study_path: Path
    repo_root: Path
    checks: list[CheckResult] = field(default_factory=list)

    def ok(self, name: str, message: str) -> None:
        self.checks.append(CheckResult("ok", name, message))

    def warn(self, name: str, message: str) -> None:
        self.checks.append(CheckResult("warn", name, message))

    def fail(self, name: str, message: str) -> None:
        self.checks.append(CheckResult("fail", name, message))

    @property
    def failed(self) -> bool:
        return any(c.level == "fail" for c in self.checks)

    def summary(self) -> dict[str, int]:
        return {
            "ok": sum(c.level == "ok" for c in self.checks),
            "warn": sum(c.level == "warn" for c in self.checks),
            "fail": sum(c.level == "fail" for c in self.checks),
        }


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return line[:i].rstrip()
    return line.rstrip()


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.lower() in {"null", "none"}:
        return None
    try:
        if any(ch in value for ch in [".", "e", "E"]):
            return float(value)
        return int(value)
    except ValueError:
        return value


def _split_key_value(text: str) -> tuple[str, str | None]:
    in_single = False
    in_double = False
    for i, ch in enumerate(text):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == ":" and not in_single and not in_double:
            return text[:i].strip(), text[i + 1 :].strip()
    return text.strip(), None


def _next_container(lines: list[tuple[int, str]], index: int, current_indent: int) -> Any:
    for indent, text in lines[index + 1 :]:
        if indent <= current_indent:
            break
        return [] if text.startswith("- ") else {}
    return {}


def load_simple_yaml(path: Path) -> dict[str, Any]:
    """Parse the study YAML used by this repo without requiring PyYAML.

    This intentionally supports only the subset used by configs/study.*.yaml:
    nested mappings, scalar values, scalar lists, and lists of mappings.
    """
    raw_lines: list[tuple[int, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = _strip_comment(raw)
        if not line.strip():
            continue
        raw_lines.append((len(line) - len(line.lstrip(" ")), line.lstrip()))

    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    for idx, (indent, text) in enumerate(raw_lines):
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if text.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError(f"List item without list parent at {path}:{idx + 1}: {text}")
            item_text = text[2:].strip()
            key, value = _split_key_value(item_text)
            if value is None:
                item = _parse_scalar(item_text)
                parent.append(item)
            else:
                item = {key: _next_container(raw_lines, idx, indent) if value == "" else _parse_scalar(value)}
                parent.append(item)
                if value == "":
                    stack.append((indent, item[key]))
                else:
                    stack.append((indent, item))
            continue

        if not isinstance(parent, dict):
            raise ValueError(f"Mapping entry without mapping parent at {path}:{idx + 1}: {text}")
        key, value = _split_key_value(text)
        if value is None:
            raise ValueError(f"Expected key/value mapping at {path}:{idx + 1}: {text}")
        parent[key] = _next_container(raw_lines, idx, indent) if value == "" else _parse_scalar(value)
        if value == "":
            stack.append((indent, parent[key]))

    return root


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def as_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(f):
        return None
    return f


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def repo_root_for(study_path: Path) -> Path:
    # configs/study.*.yaml -> repo root; otherwise use cwd as a conservative fallback.
    if study_path.parent.name == "configs":
        return study_path.parent.parent.resolve()
    return Path.cwd().resolve()


def resolve_path(repo_root: Path, rel: str) -> Path:
    p = Path(rel)
    return p if p.is_absolute() else repo_root / p


def get_nested(data: dict[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        out: list[str] = []
        for v in value.values():
            out.extend(flatten_strings(v))
        return out
    if isinstance(value, list):
        out: list[str] = []
        for v in value:
            out.extend(flatten_strings(v))
        return out
    return []


def require_columns(report: ValidationReport, name: str, columns: list[str], required: list[str]) -> None:
    missing = [c for c in required if c not in columns]
    if missing:
        report.fail(f"{name}.columns", f"Missing required columns: {', '.join(missing)}")
    else:
        report.ok(f"{name}.columns", f"Required columns present: {', '.join(required)}")


def compare_count(report: ValidationReport, name: str, actual: int, expected: int, noun: str = "rows") -> None:
    if actual == expected:
        report.ok(name, f"{actual} {noun} matches expected {expected}")
    else:
        report.fail(name, f"{actual} {noun}; expected {expected}")


def configured_market_labels(config: dict[str, Any]) -> list[str]:
    return [str(market["label"]) for market in get_nested(config, ["markets"], []) if isinstance(market, dict) and "label" in market]


def fixture_expectations(config: dict[str, Any]) -> dict[str, Any]:
    # fixture_expectations are optional and study-specific. Portable/new-study configs
    # should omit this section until they intentionally freeze baseline counts.
    return get_nested(config, ["validation", "fixture_expectations"], {}) or {}


def market_expectations(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    expectations = fixture_expectations(config).get("markets", [])
    return {
        str(item["label"]): item
        for item in expectations
        if isinstance(item, dict) and "label" in item
    }


def validate_optional_count(report: ValidationReport, name: str, actual: int, expected: Any, noun: str) -> None:
    if expected is not None:
        compare_count(report, name, actual, int(expected), noun)
    else:
        report.ok(name, f"observed {actual} {noun}")


def validate_public_safety(report: ValidationReport, config: dict[str, Any]) -> None:
    public = get_nested(config, ["validation", "public_safety"], {}) or {}
    forbids = [str(x).lower() for x in public.get("forbid_files", [])]
    patterns = [str(x).lower() for x in public.get("forbid_path_patterns", [])]
    configured_paths = flatten_strings(config.get("paths", {})) + [str(x) for x in get_nested(config, ["validation", "required_outputs"], [])]
    bad: list[str] = []
    for rel in configured_paths:
        lowered = rel.lower()
        if Path(rel).name.lower() in forbids or any(pattern in lowered for pattern in patterns):
            bad.append(rel)
    if bad:
        report.fail("public_safety.configured_paths", f"Forbidden-looking configured output/input paths: {bad}")
    else:
        report.ok("public_safety.configured_paths", "Configured study paths avoid forbidden secret/auth/token patterns")


def validate_study(study_path: Path) -> ValidationReport:
    study_path = study_path.resolve()
    config = load_simple_yaml(study_path)
    repo_root = repo_root_for(study_path)
    report = ValidationReport(study_path=study_path, repo_root=repo_root)

    report.ok("study_config.parse", f"Parsed {study_path.relative_to(repo_root) if study_path.is_relative_to(repo_root) else study_path}")

    required_outputs = get_nested(config, ["validation", "required_outputs"], []) or []
    for rel in required_outputs:
        path = resolve_path(repo_root, str(rel))
        if path.exists():
            report.ok("required_output.exists", f"Found {rel}")
        else:
            report.fail("required_output.exists", f"Missing {rel}")

    expectations = fixture_expectations(config)
    event_expectations = expectations.get("event_study", {}) if isinstance(expectations.get("event_study", {}), dict) else {}
    expected_markets = market_expectations(config)
    market_labels = configured_market_labels(config)
    event_csv_rel = get_nested(config, ["paths", "reports", "event_study_csv"])
    control_csv_rel = get_nested(config, ["paths", "reports", "volatility_control_csv"])
    processed_control_rel = get_nested(config, ["paths", "processed", "volatility_control_days"])
    processed_posts_rel = get_nested(config, ["paths", "processed", "posts"])

    event_rows: list[dict[str, str]] = []
    if event_csv_rel:
        event_path = resolve_path(repo_root, str(event_csv_rel))
        if event_path.exists():
            event_cols, event_rows = read_csv(event_path)
            event_required = ["tweet_id", "url", "created_at", "date_utc", "post_type", "impressions"]
            event_required.extend(f"{market}_range_event0_2_lift_pct" for market in market_labels)
            require_columns(report, "event_study_csv", event_cols, event_required)
            validate_optional_count(report, "event_study_csv.posts", len(event_rows), event_expectations.get("posts"), "posts")
            unique_tweets = {r.get("tweet_id", "") for r in event_rows if r.get("tweet_id")}
            compare_count(report, "event_study_csv.unique_tweet_ids", len(unique_tweets), len(event_rows), "unique tweet IDs")
            validate_optional_count(
                report,
                "event_study_csv.unique_post_dates",
                len({r.get("date_utc", "") for r in event_rows if r.get("date_utc")}),
                event_expectations.get("unique_post_dates"),
                "unique post dates",
            )
        else:
            report.fail("event_study_csv.exists", f"Missing {event_csv_rel}")

    if processed_posts_rel:
        posts_path = resolve_path(repo_root, str(processed_posts_rel))
        if posts_path.exists():
            posts_cols, posts_rows = read_csv(posts_path)
            require_columns(report, "processed_posts", posts_cols, ["tweet_id", "created_at", "date_utc", "text", "impressions", "engagement_count"])
            validate_optional_count(report, "processed_posts.rows", len(posts_rows), event_expectations.get("posts"), "posts")
        else:
            report.warn("processed_posts.exists", f"Configured processed posts file is absent: {processed_posts_rel}")

    control_rows: list[dict[str, str]] = []
    if control_csv_rel:
        control_path = resolve_path(repo_root, str(control_csv_rel))
        if control_path.exists():
            control_cols, control_rows = read_csv(control_path)
            require_columns(report, "volatility_control_csv", control_cols, ["date_utc", "market", "range_lift_pct", "range_percentile_vs_baseline", "has_oil_post", "oil_post_count", "oil_original_count", "activity_event0_2_lift_pct"])
            high_threshold = as_float(get_nested(config, ["volatility", "high_volatility_definition", "range_percentile_gte"], 75)) or 75.0
            lift_gt = as_float(get_nested(config, ["volatility", "high_volatility_definition", "range_lift_pct_gt"], 0))
            lift_gt = 0.0 if lift_gt is None else lift_gt
            high_vol = [
                r for r in control_rows
                if (as_float(r.get("range_lift_pct")) is not None and as_float(r.get("range_lift_pct")) > lift_gt)
                and (as_float(r.get("range_percentile_vs_baseline")) is not None and as_float(r.get("range_percentile_vs_baseline")) >= high_threshold)
            ]
            for market in sorted({r.get("market", "") for r in control_rows if r.get("market")} | set(market_labels)):
                market_expected = expected_markets.get(market, {})
                market_rows = [r for r in control_rows if r.get("market") == market]
                mhv = [r for r in high_vol if r.get("market") == market]
                validate_optional_count(
                    report,
                    f"volatility_control.{market}.eligible_days",
                    len(market_rows),
                    market_expected.get("eligible_days"),
                    "eligible days",
                )
                validate_optional_count(
                    report,
                    f"volatility_control.{market}.high_vol_days",
                    len(mhv),
                    market_expected.get("high_vol_days"),
                    "high-volatility days",
                )
                post_days = sum(as_bool(r.get("has_oil_post")) for r in mhv)
                no_post_days = sum(not as_bool(r.get("has_oil_post")) for r in mhv)
                if "high_vol_post_days" in market_expected:
                    compare_count(report, f"volatility_control.{market}.high_vol_post_days", post_days, int(market_expected["high_vol_post_days"]), "high-volatility post days")
                if "high_vol_no_post_days" in market_expected:
                    compare_count(report, f"volatility_control.{market}.high_vol_no_post_days", no_post_days, int(market_expected["high_vol_no_post_days"]), "high-volatility no-post days")
                report.ok(
                    f"volatility_control.{market}.high_vol_post_split",
                    f"high-vol post/no-post days: {post_days}/{no_post_days}",
                )
        else:
            report.fail("volatility_control_csv.exists", f"Missing {control_csv_rel}")

    if processed_control_rel and control_csv_rel:
        processed_path = resolve_path(repo_root, str(processed_control_rel))
        control_path = resolve_path(repo_root, str(control_csv_rel))
        if processed_path.exists() and control_path.exists():
            processed_cols, processed_rows = read_csv(processed_path)
            control_cols, control_rows = read_csv(control_path)
            if processed_cols == control_cols and processed_rows == control_rows:
                report.ok("processed_control.matches_report_csv", f"{processed_control_rel} matches {control_csv_rel}")
            else:
                report.fail("processed_control.matches_report_csv", f"{processed_control_rel} differs from {control_csv_rel}")

    validate_public_safety(report, config)
    return report


def format_report(report: ValidationReport) -> str:
    summary = report.summary()
    lines = [
        "Ostium social-volatility cached validation",
        f"study: {report.study_path}",
        f"repo: {report.repo_root}",
        f"summary: {summary['ok']} ok, {summary['warn']} warn, {summary['fail']} fail",
        "",
    ]
    for check in report.checks:
        marker = {"ok": "OK", "warn": "WARN", "fail": "FAIL"}[check.level]
        lines.append(f"[{marker}] {check.name}: {check.message}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate cached Ostium social-volatility study artifacts.")
    parser.add_argument("--study", required=True, type=Path, help="Path to study YAML config")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON summary")
    args = parser.parse_args(argv)

    report = validate_study(args.study)
    if args.json:
        print(json.dumps({"summary": report.summary(), "checks": [c.__dict__ for c in report.checks]}, indent=2))
    else:
        print(format_report(report))
    return 1 if report.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
