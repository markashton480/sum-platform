"""
Name: health
Path: core/sum_core/ops/health.py
Purpose: Runtime health checks for monitoring (/health/).
Family: Ops/Monitoring (Milestone 4)
Dependencies: Django DB connection, cache backend, optional Celery app config
"""

import os
import time
from dataclasses import asdict, dataclass
from typing import Any

from celery.app import app_or_default
from django.conf import settings
from django.core.cache import cache
from django.db import connection


@dataclass
class CheckResult:
    status: str  # "ok" or "fail"
    latency_ms: float | None = None
    detail: str | None = None


def measure_latency(func) -> CheckResult:
    start = time.perf_counter()
    try:
        func()
        status = "ok"
        detail = None
    except Exception as e:
        status = "fail"
        detail = str(e)
    end = time.perf_counter()
    latency = (end - start) * 1000.0
    return CheckResult(
        status=status, latency_ms=latency if status == "ok" else None, detail=detail
    )


def check_db() -> CheckResult:
    def _run():
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

    return measure_latency(_run)


def check_cache() -> CheckResult:
    def _run():
        test_key = "health_check_probe"
        cache.set(test_key, 1, timeout=5)
        val = cache.get(test_key)
        if val != 1:
            raise Exception("Cache set/get mismatch")
        cache.delete(test_key)

    return measure_latency(_run)


def check_celery() -> CheckResult:
    # Check if Celery is required/enabled. Default to assuming it is part of the stack
    # unless explicitly disabled or if we want to be linient in dev.
    # The requirement says: "If celery is optional in local dev... treat it as required in production-like settings"
    # For now, we will attempt checks if a broker is configured.

    broker_url = getattr(settings, "CELERY_BROKER_URL", None)
    if not broker_url:
        return CheckResult(status="ok", detail="Not configured (skipped)")

    try:
        app = app_or_default()
        # This is a bit heavy, but 'ping' is the standard way.
        # app.control.ping() returns a list of responses from workers.
        # If no workers are running, this might return empty or timeout.
        # Use a short timeout to avoid blocking the health check too long.

        # NOTE: app.control.ping(timeout=0.5) is synchronous and waits for workers.
        # If we just want to know if the BROKER is reachable, we might need `app.connection().connect()`.
        # However, monitoring usually wants to know if workers are consuming.

        # Requirement: "If you have a broker/backend configured, do a lightweight check that the app can connect
        # (or that the broker URL is present + a ping-style call if available)."

        # Let's try a connection check first as it's lighter and tests availability.
        with app.connection_for_read() as conn:
            conn.ensure_connection(max_retries=1)

        return CheckResult(status="ok")
    except Exception as e:
        return CheckResult(status="fail", detail=str(e))


def get_health_status() -> dict[str, Any]:
    checks = {
        "db": check_db(),
        "cache": check_cache(),
        "celery": check_celery(),
    }

    # Determine overall status
    is_degraded = any(r.status == "fail" for r in checks.values())

    # Format response
    response = {
        "status": "degraded" if is_degraded else "ok",
        "version": {
            "git_sha": os.environ.get("GIT_SHA", "unknown"),
            "build": os.environ.get("BUILD_ID", "unknown"),
        },
        "checks": {k: asdict(v) for k, v in checks.items()},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # Clean up empty optional fields for cleaner JSON
    for check_data in response["checks"].values():
        if check_data["detail"] is None:
            del check_data["detail"]
        if check_data["latency_ms"] is None:
            del check_data["latency_ms"]

    return response
