#!/usr/bin/env python3
"""Analyze nginx JSON access logs for IP-level visitor intelligence."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


RELATIVE_SINCE_RE = re.compile(r"^\s*(\d+)\s*([smhdw])\s*$", re.IGNORECASE)

KNOWN_BOT_TOKENS = (
    "bot",
    "spider",
    "crawler",
    "slurp",
    "bingpreview",
    "yandex",
    "duckduckbot",
    "facebookexternalhit",
    "linkedinbot",
    "googleinspectiontool",
    "semrush",
    "ahrefs",
    "mj12bot",
)

PROGRAMMATIC_TOKENS = (
    "curl/",
    "wget/",
    "python-requests",
    "httpclient",
    "go-http-client",
    "okhttp",
    "aiohttp",
    "libwww-perl",
    "java/",
    "postmanruntime",
)

RECRUITER_REFERRER_DOMAINS = (
    "linkedin.com",
    "indeed.com",
    "glassdoor.com",
    "greenhouse.io",
    "lever.co",
    "workday.com",
    "ziprecruiter.com",
    "wellfound.com",
)

BOT_PATH_HINTS = {
    "/robots.txt",
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/wp-login.php",
    "/wp-admin",
    "/xmlrpc.php",
}

STATIC_EXTENSIONS = {
    ".css",
    ".js",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".webp",
    ".woff",
    ".woff2",
    ".ttf",
    ".map",
}


@dataclass
class LogEvent:
    ts: datetime
    ip: str
    method: str
    path: str
    status: int
    referer_domain: str
    user_agent: str
    request_time: float
    is_static: bool


@dataclass
class SessionSummary:
    ip: str
    user_agent: str
    start: datetime
    end: datetime
    request_count: int
    unique_paths: int
    page_views: int
    resume_hits: int
    robots_hits: int
    recruiter_ref_hits: int
    req_per_min: float
    browser_ua: bool
    known_bot_ua: bool
    programmatic_ua: bool
    business_hour_hits: int
    statuses: Counter[int]
    paths: Counter[str]


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_iso8601(value: str) -> datetime | None:
    if not value or value == "-":
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_since(since_value: str | None, now: datetime) -> datetime | None:
    if not since_value:
        return None
    match = RELATIVE_SINCE_RE.match(since_value)
    if match:
        amount = int(match.group(1))
        unit = match.group(2).lower()
        seconds_per_unit = {
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400,
            "w": 604800,
        }[unit]
        return now - timedelta(seconds=amount * seconds_per_unit)
    normalized = since_value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def extract_client_ip(remote_addr: str, x_forwarded_for: str) -> str:
    if x_forwarded_for and x_forwarded_for != "-":
        first = x_forwarded_for.split(",")[0].strip()
        if first:
            return first
    if remote_addr and remote_addr != "-":
        return remote_addr
    return "unknown"


def normalize_path(request_uri: str) -> str:
    try:
        parsed = urlsplit(request_uri)
        path = parsed.path
    except ValueError:
        path = request_uri
    return path or "/"


def referer_domain(referer: str) -> str:
    if not referer or referer == "-":
        return ""
    try:
        host = urlsplit(referer).netloc.lower()
    except ValueError:
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host


def is_static_path(path: str) -> bool:
    return Path(path).suffix.lower() in STATIC_EXTENSIONS


def looks_like_browser_ua(user_agent: str) -> bool:
    lower = user_agent.lower()
    if "mozilla/" not in lower:
        return False
    return any(token in lower for token in ("chrome/", "safari/", "firefox/", "edg/", "opr/"))


def has_token(text: str, tokens: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(token in lower for token in tokens)


def is_recruiter_referer(host: str) -> bool:
    return any(domain in host for domain in RECRUITER_REFERRER_DOMAINS)


def clamp_score(value: int) -> int:
    return max(0, min(100, value))


def build_session(ip: str, user_agent: str, events: list[LogEvent]) -> SessionSummary:
    start = events[0].ts
    end = events[-1].ts
    request_count = len(events)
    path_counts: Counter[str] = Counter(event.path for event in events)
    status_counts: Counter[int] = Counter(event.status for event in events)
    page_views = sum(1 for event in events if not event.is_static)
    resume_hits = sum(1 for event in events if "resume" in event.path.lower())
    robots_hits = sum(1 for event in events if event.path.lower() in BOT_PATH_HINTS)
    recruiter_ref_hits = sum(1 for event in events if is_recruiter_referer(event.referer_domain))

    duration_minutes = max((end - start).total_seconds() / 60.0, 1 / 60)
    req_per_min = request_count / duration_minutes

    browser_ua = looks_like_browser_ua(user_agent)
    known_bot_ua = has_token(user_agent, KNOWN_BOT_TOKENS)
    programmatic_ua = has_token(user_agent, PROGRAMMATIC_TOKENS)
    business_hour_hits = sum(1 for event in events if 8 <= event.ts.astimezone().hour < 19)

    return SessionSummary(
        ip=ip,
        user_agent=user_agent,
        start=start,
        end=end,
        request_count=request_count,
        unique_paths=len(path_counts),
        page_views=page_views,
        resume_hits=resume_hits,
        robots_hits=robots_hits,
        recruiter_ref_hits=recruiter_ref_hits,
        req_per_min=req_per_min,
        browser_ua=browser_ua,
        known_bot_ua=known_bot_ua,
        programmatic_ua=programmatic_ua,
        business_hour_hits=business_hour_hits,
        statuses=status_counts,
        paths=path_counts,
    )


def calculate_scores(state: dict[str, Any]) -> tuple[int, int, int, str]:
    requests = max(state["requests"], 1)
    unique_paths = len(state["paths"])
    status_404 = state["statuses"].get(404, 0)
    ratio_404 = status_404 / requests
    static_ratio = state["static_hits"] / requests
    business_ratio = state["business_hour_hits"] / requests

    bot_score = 0
    if state["known_bot_sessions"] > 0:
        bot_score += 65
    if state["programmatic_sessions"] > 0 and state["browser_sessions"] == 0:
        bot_score += 30
    if state["robots_hits"] > 0:
        bot_score += min(25, 10 + state["robots_hits"] * 3)
    if state["max_req_per_min"] >= 120:
        bot_score += 35
    elif state["max_req_per_min"] >= 60:
        bot_score += 25
    elif state["max_req_per_min"] >= 20:
        bot_score += 12
    if ratio_404 >= 0.4:
        bot_score += 20
    elif ratio_404 >= 0.2:
        bot_score += 12
    if unique_paths <= 2 and requests >= 20:
        bot_score += 10
    if state["recruiter_ref_hits"] > 0:
        bot_score -= 10
    bot_score = clamp_score(bot_score)

    human_score = 0
    if state["browser_sessions"] > 0:
        human_score += 30
    if state["resume_hits"] > 0:
        human_score += 20
    if unique_paths >= 5:
        human_score += 20
    elif unique_paths >= 3:
        human_score += 12
    if state["sessions"] >= 2:
        human_score += 10
    if len(state["return_days"]) >= 2:
        human_score += 10
    if 0.15 <= static_ratio <= 0.92:
        human_score += 10
    if state["max_req_per_min"] < 20:
        human_score += 10
    if ratio_404 < 0.1:
        human_score += 5
    human_score -= state["known_bot_sessions"] * 20
    if state["programmatic_sessions"] > 0 and state["browser_sessions"] == 0:
        human_score -= 20
    if state["robots_hits"] > 0:
        human_score -= 15
    human_score = clamp_score(human_score)

    recruiter_score = 0
    if state["resume_hits"] > 0:
        recruiter_score += 35
    if state["recruiter_ref_hits"] > 0:
        recruiter_score += 35
    if state["browser_sessions"] > 0:
        recruiter_score += 10
    if 2 <= requests <= 80:
        recruiter_score += 10
    if unique_paths >= 2:
        recruiter_score += 5
    if business_ratio >= 0.6:
        recruiter_score += 10
    if len(state["return_days"]) >= 2:
        recruiter_score += 5
    recruiter_score -= max(0, bot_score - 40)
    if human_score < 35:
        recruiter_score -= 15
    recruiter_score = clamp_score(recruiter_score)

    if bot_score >= 70:
        label = "bot"
    elif recruiter_score >= 65 and human_score >= 45:
        label = "likely_recruiter"
    elif human_score >= 45:
        label = "likely_human"
    else:
        label = "uncertain"

    return bot_score, human_score, recruiter_score, label


def format_timespan(start: datetime | None, end: datetime | None) -> str:
    if not start or not end:
        return "n/a"
    return f"{start.astimezone().isoformat(timespec='seconds')} -> {end.astimezone().isoformat(timespec='seconds')}"


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    if not rows:
        print("(no rows)")
        return
    widths = [len(header) for header in headers]
    for row in rows:
        for idx, value in enumerate(row):
            widths[idx] = max(widths[idx], len(value))
    separator = " | "
    print(separator.join(header.ljust(widths[idx]) for idx, header in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(separator.join(value.ljust(widths[idx]) for idx, value in enumerate(row)))


def analyze(log_path: Path, since: datetime | None, session_gap_minutes: int) -> dict[str, Any]:
    grouped_events: dict[tuple[str, str], list[LogEvent]] = defaultdict(list)
    summary = {
        "total_lines": 0,
        "malformed_lines": 0,
        "filtered_by_since": 0,
        "accepted_events": 0,
        "first_seen": None,
        "last_seen": None,
    }
    path_counts: Counter[str] = Counter()
    path_404_counts: Counter[str] = Counter()
    referer_counts: Counter[str] = Counter()
    status_counts: Counter[int] = Counter()
    method_counts: Counter[str] = Counter()

    with log_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            summary["total_lines"] += 1
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                summary["malformed_lines"] += 1
                continue

            ts = parse_iso8601(str(payload.get("time_iso8601", "")))
            if ts is None:
                summary["malformed_lines"] += 1
                continue
            if since and ts < since:
                summary["filtered_by_since"] += 1
                continue

            remote_addr = str(payload.get("remote_addr", ""))
            xff = str(payload.get("x_forwarded_for", ""))
            ip = extract_client_ip(remote_addr, xff)
            method = str(payload.get("request_method", "GET")).upper()
            path = normalize_path(str(payload.get("request_uri", "/")))
            status = to_int(payload.get("status"), 0)
            referer_host = referer_domain(str(payload.get("http_referer", "")))
            user_agent = str(payload.get("http_user_agent", ""))
            request_time = to_float(payload.get("request_time"), 0.0)

            event = LogEvent(
                ts=ts,
                ip=ip,
                method=method,
                path=path,
                status=status,
                referer_domain=referer_host,
                user_agent=user_agent,
                request_time=request_time,
                is_static=is_static_path(path),
            )
            grouped_events[(ip, user_agent)].append(event)

            summary["accepted_events"] += 1
            summary["first_seen"] = ts if summary["first_seen"] is None else min(summary["first_seen"], ts)
            summary["last_seen"] = ts if summary["last_seen"] is None else max(summary["last_seen"], ts)

            path_counts[path] += 1
            if status == 404:
                path_404_counts[path] += 1
            if referer_host:
                referer_counts[referer_host] += 1
            status_counts[status] += 1
            method_counts[method] += 1

    ip_state: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "requests": 0,
            "first_seen": None,
            "last_seen": None,
            "paths": Counter(),
            "statuses": Counter(),
            "methods": Counter(),
            "referers": Counter(),
            "user_agents": Counter(),
            "static_hits": 0,
            "page_hits": 0,
            "resume_hits": 0,
            "robots_hits": 0,
            "recruiter_ref_hits": 0,
            "request_time_total": 0.0,
            "sessions": 0,
            "browser_sessions": 0,
            "known_bot_sessions": 0,
            "programmatic_sessions": 0,
            "max_req_per_min": 0.0,
            "return_days": set(),
            "business_hour_hits": 0,
        }
    )
    sessions: list[SessionSummary] = []
    session_gap = timedelta(minutes=session_gap_minutes)

    for (ip, user_agent), events in grouped_events.items():
        events.sort(key=lambda event: event.ts)
        current: list[LogEvent] = []
        for event in events:
            if current and (event.ts - current[-1].ts) > session_gap:
                sessions.append(build_session(ip, user_agent, current))
                current = [event]
            else:
                current.append(event)
        if current:
            sessions.append(build_session(ip, user_agent, current))

    for session in sessions:
        state = ip_state[session.ip]
        state["sessions"] += 1
        state["browser_sessions"] += 1 if session.browser_ua else 0
        state["known_bot_sessions"] += 1 if session.known_bot_ua else 0
        state["programmatic_sessions"] += 1 if session.programmatic_ua else 0
        state["max_req_per_min"] = max(state["max_req_per_min"], session.req_per_min)
        state["business_hour_hits"] += session.business_hour_hits

        state["first_seen"] = session.start if state["first_seen"] is None else min(state["first_seen"], session.start)
        state["last_seen"] = session.end if state["last_seen"] is None else max(state["last_seen"], session.end)

        for status, count in session.statuses.items():
            state["statuses"][status] += count
        for path, count in session.paths.items():
            state["paths"][path] += count
            if "resume" in path.lower():
                state["resume_hits"] += count
            if path.lower() in BOT_PATH_HINTS:
                state["robots_hits"] += count
            if is_static_path(path):
                state["static_hits"] += count
            else:
                state["page_hits"] += count
        state["recruiter_ref_hits"] += session.recruiter_ref_hits

        for day in {event_day.date() for event_day in (session.start, session.end)}:
            state["return_days"].add(day.isoformat())

        state["user_agents"][session.user_agent] += session.request_count

    for (ip, user_agent), events in grouped_events.items():
        state = ip_state[ip]
        for event in events:
            state["requests"] += 1
            state["methods"][event.method] += 1
            if event.referer_domain:
                state["referers"][event.referer_domain] += 1
            state["request_time_total"] += event.request_time

    ip_reports: list[dict[str, Any]] = []
    for ip, state in ip_state.items():
        bot_score, human_score, recruiter_score, label = calculate_scores(state)
        ip_reports.append(
            {
                "ip": ip,
                "label": label,
                "bot_score": bot_score,
                "human_score": human_score,
                "recruiter_likelihood": recruiter_score,
                "requests": state["requests"],
                "sessions": state["sessions"],
                "unique_paths": len(state["paths"]),
                "resume_hits": state["resume_hits"],
                "robots_hits": state["robots_hits"],
                "max_req_per_min": round(state["max_req_per_min"], 2),
                "first_seen": state["first_seen"].isoformat() if state["first_seen"] else None,
                "last_seen": state["last_seen"].isoformat() if state["last_seen"] else None,
                "top_paths": state["paths"].most_common(5),
                "top_referers": state["referers"].most_common(3),
                "top_user_agents": state["user_agents"].most_common(2),
            }
        )

    ip_reports.sort(key=lambda item: item["requests"], reverse=True)

    return {
        "summary": summary,
        "top_paths": path_counts,
        "top_404_paths": path_404_counts,
        "top_referers": referer_counts,
        "status_counts": status_counts,
        "method_counts": method_counts,
        "sessions": sessions,
        "ip_reports": ip_reports,
    }


def print_report(result: dict[str, Any], top_n: int) -> None:
    summary = result["summary"]
    print("Visitor Intelligence Report")
    print("===========================")
    print(f"Accepted events: {summary['accepted_events']} / {summary['total_lines']} lines")
    print(f"Malformed lines: {summary['malformed_lines']}")
    print(f"Filtered by --since: {summary['filtered_by_since']}")
    print(f"Observed window: {format_timespan(summary['first_seen'], summary['last_seen'])}")
    print()

    if summary["accepted_events"] == 0:
        print("No events found for the given filters.")
        return

    print("Top Status Codes")
    print_table(
        ["Status", "Count"],
        [[str(status), str(count)] for status, count in result["status_counts"].most_common(top_n)],
    )
    print()

    print("Top Paths")
    print_table(
        ["Path", "Hits"],
        [[path, str(count)] for path, count in result["top_paths"].most_common(top_n)],
    )
    print()

    print("Top 404 Paths")
    print_table(
        ["Path", "404 Hits"],
        [[path, str(count)] for path, count in result["top_404_paths"].most_common(top_n)],
    )
    print()

    ip_rows = []
    for item in result["ip_reports"][:top_n]:
        ip_rows.append(
            [
                item["ip"],
                item["label"],
                str(item["requests"]),
                str(item["sessions"]),
                str(item["bot_score"]),
                str(item["human_score"]),
                str(item["recruiter_likelihood"]),
                ",".join(path for path, _ in item["top_paths"][:2]) or "-",
            ]
        )
    print("Top IP Activity")
    print_table(["IP", "Label", "Req", "Sess", "Bot", "Human", "Recruiter", "Top Paths"], ip_rows)
    print()

    bot_rows = []
    for item in sorted(result["ip_reports"], key=lambda row: row["bot_score"], reverse=True):
        if item["bot_score"] < 40:
            continue
        bot_rows.append(
            [
                item["ip"],
                str(item["bot_score"]),
                str(item["requests"]),
                str(item["robots_hits"]),
                f"{item['max_req_per_min']:.1f}",
                item["top_user_agents"][0][0][:48] if item["top_user_agents"] else "-",
            ]
        )
        if len(bot_rows) >= top_n:
            break
    print("Most Likely Bots")
    print_table(["IP", "Bot Score", "Req", "Robots Hits", "Req/Min", "User Agent"], bot_rows)
    print()

    recruiter_rows = []
    for item in sorted(result["ip_reports"], key=lambda row: row["recruiter_likelihood"], reverse=True):
        if item["recruiter_likelihood"] < 45:
            continue
        recruiter_rows.append(
            [
                item["ip"],
                item["label"],
                str(item["recruiter_likelihood"]),
                str(item["human_score"]),
                str(item["resume_hits"]),
                ",".join(domain for domain, _ in item["top_referers"][:2]) or "-",
            ]
        )
        if len(recruiter_rows) >= top_n:
            break
    print("Likely Recruiter Traffic")
    print_table(["IP", "Label", "Recruiter", "Human", "Resume Hits", "Top Referrers"], recruiter_rows)


def build_json_payload(result: dict[str, Any], top_n: int) -> dict[str, Any]:
    return {
        "summary": {
            "total_lines": result["summary"]["total_lines"],
            "accepted_events": result["summary"]["accepted_events"],
            "malformed_lines": result["summary"]["malformed_lines"],
            "filtered_by_since": result["summary"]["filtered_by_since"],
            "first_seen": result["summary"]["first_seen"].isoformat() if result["summary"]["first_seen"] else None,
            "last_seen": result["summary"]["last_seen"].isoformat() if result["summary"]["last_seen"] else None,
        },
        "top_status_codes": result["status_counts"].most_common(top_n),
        "top_paths": result["top_paths"].most_common(top_n),
        "top_404_paths": result["top_404_paths"].most_common(top_n),
        "top_referers": result["top_referers"].most_common(top_n),
        "ip_reports": result["ip_reports"][:top_n],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="IP-level visitor intelligence analyzer for nginx JSON logs.")
    parser.add_argument(
        "--log-file",
        default="logs/access.log",
        help="Path to JSON-formatted nginx access log (default: logs/access.log).",
    )
    parser.add_argument(
        "--since",
        default=None,
        help="Filter events newer than this value (e.g. 24h, 7d, or 2026-04-20T08:00:00+03:00).",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="How many rows to show in tables and JSON summaries (default: 10).",
    )
    parser.add_argument(
        "--session-gap-minutes",
        type=int,
        default=30,
        help="Idle time in minutes to split sessions for same IP+UA (default: 30).",
    )
    parser.add_argument(
        "--json-output",
        default=None,
        help="Optional output path for machine-readable JSON summary.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    log_path = Path(args.log_file)
    if not log_path.exists():
        print(f"Log file not found: {log_path}")
        print("Run docker compose first, then execute this script again.")
        return 1

    try:
        since = parse_since(args.since, datetime.now(timezone.utc))
    except ValueError:
        print("Invalid --since value. Use relative values like 24h/7d or full ISO datetime.")
        return 1

    result = analyze(log_path, since, args.session_gap_minutes)
    print_report(result, args.top)

    if args.json_output:
        output_path = Path(args.json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = build_json_payload(result, args.top)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print()
        print(f"JSON summary written to: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
