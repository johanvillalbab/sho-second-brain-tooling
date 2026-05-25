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
