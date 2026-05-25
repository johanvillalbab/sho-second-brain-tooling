"""Thin HTTP client against life-os.

Uses the static service token (SYNC_SERVICE_TOKEN on life-os side) so the
sync bridge can run unattended in the nightly routine. Endpoints follow
life-os's `/api/...` prefix.

Designed as a stable surface so future fases (goals, dates, calendar) can
extend it without restructuring the sync engine.
"""

from __future__ import annotations

from typing import Any, Optional

import requests

from . import config


class LifeOSError(RuntimeError):
    """Raised when life-os returns a non-2xx or the network fails."""

    def __init__(self, message: str, status: Optional[int] = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body


class LifeOSClient:
    """Single-instance HTTP client. Reuses one requests.Session."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        service_token: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.base_url = (base_url or config.lifeos_base_url()).rstrip("/")
        token = service_token or config.lifeos_service_token()
        self.timeout = timeout or config.request_timeout()
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "second-brain-sync/0.1",
            }
        )

    # ── internals ────────────────────────────────────────────────────────────

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}/api{path}"

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = self._url(path)
        try:
            resp = self._session.request(method, url, timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:
            raise LifeOSError(f"{method} {url} network error: {exc}") from exc

        if not resp.ok:
            body: Any
            try:
                body = resp.json()
            except ValueError:
                body = resp.text
            raise LifeOSError(
                f"{method} {url} -> HTTP {resp.status_code}: {body}",
                status=resp.status_code,
                body=body,
            )

        if resp.status_code == 204 or not resp.content:
            return None
        try:
            return resp.json()
        except ValueError as exc:
            raise LifeOSError(
                f"{method} {url} returned non-JSON: {resp.text[:200]}"
            ) from exc

    # ── health ───────────────────────────────────────────────────────────────

    def health(self) -> dict:
        # /health lives at root, not under /api — use a manual call.
        url = f"{self.base_url}/api/health"
        resp = self._session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    # ── tasks ────────────────────────────────────────────────────────────────

    def tasks_list(
        self,
        task_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        params: dict[str, str] = {}
        if task_date:
            params["task_date"] = task_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/tasks", params=params)

    def tasks_changed_since(self, since_iso: str) -> dict:
        """Pull only tasks whose updated_at > since_iso. Cheap delta for the bridge."""
        return self._request("GET", "/tasks/changed-since", params={"since": since_iso})

    def tasks_create(self, payload: dict) -> dict:
        return self._request("POST", "/tasks", json=payload)

    def tasks_update(self, task_id: int, payload: dict) -> dict:
        return self._request("PUT", f"/tasks/{task_id}", json=payload)

    def tasks_delete(self, task_id: int) -> None:
        self._request("DELETE", f"/tasks/{task_id}")

    # ── goals ───────────────────────────────────────────────────────────────

    def goals_list(self) -> dict:
        return self._request("GET", "/goals")

    def goals_get(self, number: int) -> dict:
        return self._request("GET", f"/goals/{number}")

    def goals_update_status(self, number: int, quarter: int, status: str) -> dict:
        return self._request(
            "PUT",
            f"/goals/{number}/status",
            json={"quarter": quarter, "status": status},
        )

    def goals_add_next_step(self, number: int, text: str, order_index: int = 0) -> dict:
        return self._request(
            "POST",
            f"/goals/{number}/nextsteps",
            json={"text": text, "order_index": order_index},
        )

    def goals_update_next_step(
        self,
        number: int,
        step_id: int,
        text: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> dict:
        payload: dict = {}
        if text is not None:
            payload["text"] = text
        if completed is not None:
            payload["completed"] = completed
        return self._request("PUT", f"/goals/{number}/nextsteps/{step_id}", json=payload)

    def goals_delete_next_step(self, number: int, step_id: int) -> None:
        self._request("DELETE", f"/goals/{number}/nextsteps/{step_id}")

    # ── dates ───────────────────────────────────────────────────────────────

    def dates_list(self) -> dict:
        return self._request("GET", "/dates")

    def dates_create(self, payload: dict) -> dict:
        return self._request("POST", "/dates", json=payload)

    def dates_update(self, date_id: int, payload: dict) -> dict:
        return self._request("PUT", f"/dates/{date_id}", json=payload)

    def dates_delete(self, date_id: int) -> None:
        self._request("DELETE", f"/dates/{date_id}")

    def dates_get_by_sync_id(self, sync_id: str) -> Optional[dict]:
        """Returns None on 404 instead of raising, so the bridge can use it
        for idempotency lookups without try/except clutter."""
        try:
            return self._request("GET", f"/dates/by-sync-id/{sync_id}")
        except LifeOSError as exc:
            if exc.status == 404:
                return None
            raise

    # ── calendar ────────────────────────────────────────────────────────────

    def calendar_status(self) -> dict:
        return self._request("GET", "/calendar/status")

    def calendar_events(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        calendar_id: str = "primary",
    ) -> dict:
        params = {"calendar_id": calendar_id}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return self._request("GET", "/calendar/events", params=params)

    def calendar_create_event(
        self,
        title: str,
        start_datetime: str,
        end_datetime: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_id: str = "primary",
    ) -> dict:
        payload: dict = {
            "title": title,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "calendar_id": calendar_id,
        }
        if description:
            payload["description"] = description
        if location:
            payload["location"] = location
        return self._request("POST", "/calendar/events", json=payload)

    def calendar_delete_event(self, event_id: str, calendar_id: str = "primary") -> None:
        self._request(
            "DELETE",
            f"/calendar/events/{event_id}",
            params={"calendar_id": calendar_id},
        )

    def calendar_schedule_day(
        self,
        date_iso: str,
        scope: str = "big3_high",
        task_ids: Optional[list[int]] = None,
        dry_run: bool = False,
    ) -> dict:
        payload: dict = {"date": date_iso, "scope": scope, "dry_run": dry_run}
        if task_ids:
            payload["task_ids"] = task_ids
        return self._request("POST", "/calendar/schedule-day", json=payload)

    def calendar_schedule_task(
        self,
        task_id: int,
        start_datetime: Optional[str] = None,
        end_datetime: Optional[str] = None,
        dry_run: bool = False,
    ) -> dict:
        payload: dict = {"dry_run": dry_run}
        if start_datetime:
            payload["start_datetime"] = start_datetime
        if end_datetime:
            payload["end_datetime"] = end_datetime
        return self._request("POST", f"/calendar/tasks/{task_id}/schedule", json=payload)

    def calendar_unschedule_task(self, task_id: int) -> dict:
        return self._request("DELETE", f"/calendar/tasks/{task_id}/schedule")
