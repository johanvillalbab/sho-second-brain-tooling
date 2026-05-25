"""CLI wrapper around the calendar half of LifeOSClient.

Designed to be called from slash commands (`/obsidian-agenda`,
`/obsidian-schedule`, `/obsidian-focus-day`) without each command needing
to inline httpx/auth/parsing logic. All subcommands print JSON so Claude
can parse the response.

Examples:
    python3 -m scripts.sync.calendar_cli status
    python3 -m scripts.sync.calendar_cli events --start 2026-05-25 --end 2026-05-26
    python3 -m scripts.sync.calendar_cli create-event \\
        --title "Deep work" --start 2026-05-26T09:00:00-05:00 --end 2026-05-26T10:30:00-05:00
    python3 -m scripts.sync.calendar_cli schedule-day --date 2026-05-26 --scope big3_high
    python3 -m scripts.sync.calendar_cli schedule-task --task-id 42 \\
        --start 2026-05-26T09:00:00-05:00 --end 2026-05-26T10:30:00-05:00
    python3 -m scripts.sync.calendar_cli unschedule-task --task-id 42
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .lifeos_client import LifeOSClient, LifeOSError


def _emit(data: Any) -> int:
    print(json.dumps(data, indent=2, sort_keys=True, default=str))
    return 0


def _emit_error(exc: LifeOSError) -> int:
    print(json.dumps({"error": str(exc), "status": exc.status, "body": exc.body}, indent=2, default=str))
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="calendar CLI for second-brain commands")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="GET /calendar/status — is OAuth wired?")

    p_events = sub.add_parser("events", help="GET /calendar/events")
    p_events.add_argument("--start", help="ISO 8601 datetime; default today 00:00 local")
    p_events.add_argument("--end", help="ISO 8601 datetime; default start + 7 days")
    p_events.add_argument("--calendar-id", default="primary")

    p_create = sub.add_parser("create-event", help="POST /calendar/events")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--start", required=True, help="ISO 8601 datetime with tz")
    p_create.add_argument("--end", required=True, help="ISO 8601 datetime with tz")
    p_create.add_argument("--description")
    p_create.add_argument("--location")
    p_create.add_argument("--calendar-id", default="primary")

    p_del = sub.add_parser("delete-event", help="DELETE /calendar/events/{id}")
    p_del.add_argument("--event-id", required=True)
    p_del.add_argument("--calendar-id", default="primary")

    p_day = sub.add_parser("schedule-day", help="POST /calendar/schedule-day")
    p_day.add_argument("--date", required=True, help="YYYY-MM-DD")
    p_day.add_argument("--scope", default="big3_high", choices=["big3", "big3_high", "selected"])
    p_day.add_argument("--task-ids", nargs="*", type=int, help="for scope=selected")
    p_day.add_argument("--dry-run", action="store_true")

    p_task = sub.add_parser("schedule-task", help="POST /calendar/tasks/{id}/schedule")
    p_task.add_argument("--task-id", required=True, type=int)
    p_task.add_argument("--start", help="ISO datetime; omit to let life-os find a slot")
    p_task.add_argument("--end")
    p_task.add_argument("--dry-run", action="store_true")

    p_un = sub.add_parser("unschedule-task", help="DELETE /calendar/tasks/{id}/schedule")
    p_un.add_argument("--task-id", required=True, type=int)

    args = parser.parse_args(argv)
    client = LifeOSClient()

    try:
        if args.cmd == "status":
            return _emit(client.calendar_status())
        if args.cmd == "events":
            return _emit(client.calendar_events(
                start=args.start, end=args.end, calendar_id=args.calendar_id,
            ))
        if args.cmd == "create-event":
            return _emit(client.calendar_create_event(
                title=args.title,
                start_datetime=args.start,
                end_datetime=args.end,
                description=args.description,
                location=args.location,
                calendar_id=args.calendar_id,
            ))
        if args.cmd == "delete-event":
            client.calendar_delete_event(args.event_id, calendar_id=args.calendar_id)
            return _emit({"deleted": args.event_id})
        if args.cmd == "schedule-day":
            return _emit(client.calendar_schedule_day(
                date_iso=args.date, scope=args.scope,
                task_ids=args.task_ids, dry_run=args.dry_run,
            ))
        if args.cmd == "schedule-task":
            return _emit(client.calendar_schedule_task(
                task_id=args.task_id,
                start_datetime=args.start,
                end_datetime=args.end,
                dry_run=args.dry_run,
            ))
        if args.cmd == "unschedule-task":
            return _emit(client.calendar_unschedule_task(args.task_id))
    except LifeOSError as exc:
        return _emit_error(exc)

    parser.error(f"unknown command: {args.cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
