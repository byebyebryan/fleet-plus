#!/usr/bin/env python3
"""Capture released Agent Observer a14 from owned fictional cached sources.

The companion shell recipe downloads the two public release wheels, checks their
published SHA-256 values, installs pinned dashboard/VT-renderer dependencies in
a temporary environment, and passes the installed wheel files here. The script
starts only its own synthetic Service/Mesh publishers and the released CLI.
It never reads user configuration or invokes native providers.

Capture gates in this file deliberately cover media only: installed package
wheel parity, fixture projection/source health, expected PTY states, terminal
cleanup, media geometry/codec/duration and output hashes. They do not qualify
native classification, sustained resources, physical devices or deployment.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import fcntl
import hashlib
import html
import importlib.metadata
import importlib.util
import json
import os
import pty
import re
import select
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import termios
import threading
import time
import zipfile
import platform
from uuid import NAMESPACE_URL, uuid5
from pathlib import Path
from typing import Any

# The fixture subprocess enables Python's safe-path mode, which omits the
# script directory. Import the adjacent reviewed helper explicitly in both
# the capture process and that owned child.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pyte
from terminal_colors import color as _color, xterm_color as _xterm_color


OBSERVER_VERSION = "0.7.0a14"
OBSERVER_WHEEL_SHA256 = "46a1158023023b60d9b839184a45f7b7eeb21b04dce67aad808fa8277522518f"
OBSERVER_SOURCE_REVISION = "dcbd69d9debed39eaff3f898815dfb52c6711174"
OBSERVER_TAG = "v0.7.0a14"
OBSERVER_TAG_REVISION = "7dbcd611f7b0ecfbebf7b2e8053963fb25915999"
MESH_VERSION = "0.1.0a25"
MESH_WHEEL_SHA256 = "0055e42162827744add4f817d3918cfc20471e5ec5a3cdf0840d254f76f5dc3a"
TEXTUAL_VERSION = "8.2.8"
PYTE_VERSION = "0.8.2"
WIDE_STILL = (140, 24)
DEMO = (140, 32)
COMPACT = (60, 20)
VIDEO_SEGMENTS = (5, 4, 6, 5)
VIDEO_FRAMES_PER_SECOND = 30
WINDOW_MS = 72 * 60 * 60 * 1000
FONT_FAMILY = "Noto Sans Mono"
FONT_SIZE = 20
CELL_WIDTH = 12
CELL_HEIGHT = 24
DEFAULT_FG = "#e6edf3"
DEFAULT_BG = "#0d1117"


class CaptureError(RuntimeError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_checked(command: list[str], *, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def version(name: str) -> str:
    return importlib.metadata.version(name)


def check_capture_requirements() -> dict[str, Any]:
    """Verify every auxiliary runtime package against the committed exact pins."""
    requirements_path = Path(__file__).with_name("terminal-capture-requirements.txt")
    pinned: dict[str, str] = {}
    for raw in requirements_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        name, separator, expected = line.partition("==")
        if not separator or not name or not expected:
            raise CaptureError(f"unsupported capture requirement line: {line!r}")
        actual = version(name)
        if actual != expected:
            raise CaptureError(f"capture dependency mismatch: {name} expected {expected}, got {actual}")
        pinned[name] = actual
    return {
        "file": "scripts/terminal-capture-requirements.txt",
        "sha256": sha256_file(requirements_path),
        "pinnedVersions": pinned,
        "pythonVersion": platform.python_version(),
    }


def capture_recipe_evidence() -> list[dict[str, str]]:
    """Hash the exact capture entrypoint and renderer used for this run."""
    repo_root = Path(__file__).resolve().parent.parent
    return [
        {"path": "scripts/capture-terminal-media.sh", "sha256": sha256_file(repo_root / "scripts/capture-terminal-media.sh")},
        {"path": "scripts/capture_terminal_media.py", "sha256": sha256_file(Path(__file__).resolve())},
        {"path": "scripts/terminal_colors.py", "sha256": sha256_file(repo_root / "scripts/terminal_colors.py")},
        {"path": "tests/test_terminal_colors.py", "sha256": sha256_file(repo_root / "tests/test_terminal_colors.py")},
    ]


def check_release_inputs(observer_wheel: Path, mesh_wheel: Path) -> dict[str, Any]:
    """Bind the imported app and projection libraries to the exact release wheels."""
    expected = (
        (observer_wheel, OBSERVER_WHEEL_SHA256, "agent-observer", OBSERVER_VERSION, "agent_observer"),
        (mesh_wheel, MESH_WHEEL_SHA256, "mesh-plus", MESH_VERSION, "mesh_plus"),
    )
    result: dict[str, Any] = {"wheels": []}
    for wheel_path, expected_sha, distribution_name, expected_version, top_level in expected:
        wheel_path = wheel_path.resolve()
        actual_sha = sha256_file(wheel_path)
        if actual_sha != expected_sha:
            raise CaptureError(f"{distribution_name} wheel SHA-256 does not match the public release")
        installed_version = version(distribution_name)
        if installed_version != expected_version:
            raise CaptureError(
                f"{distribution_name} version mismatch: expected {expected_version}, got {installed_version}"
            )
        distribution = importlib.metadata.distribution(distribution_name)
        site_root = Path(distribution.locate_file("")).resolve()
        checked = 0
        missing: list[str] = []
        different: list[str] = []
        with zipfile.ZipFile(wheel_path) as archive:
            dist_info = next(
                (name.split("/", 1)[0] for name in archive.namelist() if name.endswith(".dist-info/METADATA")),
                None,
            )
            if dist_info is None:
                raise CaptureError(f"{distribution_name} wheel has no dist-info metadata")
            for member in archive.namelist():
                if member.endswith("/") or ".data/" in member:
                    continue
                if not (member.startswith(top_level + "/") or member.startswith(dist_info + "/")):
                    continue
                leaf = member.rsplit("/", 1)[-1]
                if leaf in {"RECORD", "INSTALLER", "REQUESTED", "direct_url.json"}:
                    continue
                installed_path = site_root / member
                if not installed_path.is_file():
                    missing.append(member)
                    continue
                if installed_path.read_bytes() != archive.read(member):
                    different.append(member)
                    continue
                checked += 1
        if missing or different or checked < 20:
            raise CaptureError(
                f"{distribution_name} installed-wheel parity failed: "
                f"checked={checked} missing={missing[:4]} different={different[:4]}"
            )
        result["wheels"].append(
            {
                "distribution": distribution_name,
                "version": installed_version,
                "wheelSha256": actual_sha,
                "installedParityFiles": checked,
                "installedPackagePath": str(site_root / top_level),
            }
        )
    for package, expected_version in (
        ("textual", TEXTUAL_VERSION),
        ("pyte", PYTE_VERSION),
    ):
        actual = version(package)
        if actual != expected_version:
            raise CaptureError(f"{package} version mismatch: expected {expected_version}, got {actual}")
    module = importlib.util.find_spec("agent_observer.terminal.dashboard")
    if module is None or module.origin is None:
        raise CaptureError("released Agent Observer dashboard module is not installed")
    result["dashboardModule"] = str(Path(module.origin).resolve())
    result["dashboardModuleSha256"] = sha256_file(Path(module.origin))
    result["versions"] = {
        "agent-observer": OBSERVER_VERSION,
        "mesh-plus": MESH_VERSION,
        "textual": TEXTUAL_VERSION,
        "pyte": PYTE_VERSION,
    }
    return result


def _fact(value: str, observed_at: int | None, source: str | None, health: str, reason: str) -> dict[str, Any]:
    return {
        "value": value,
        "observedAt": observed_at,
        "source": source,
        "health": health,
        "reason": reason,
        "clock": "sample" if observed_at is not None else None,
    }


def make_snapshot(host: dict[str, Any], uid: int) -> dict[str, Any]:
    """Create one contract-shaped cache document from fictional fixture labels."""
    from agent_observer.contract import store_namespace

    now_ms = int(time.time() * 1000)
    config_home = "/fixture/codex"
    namespace = store_namespace("codex", config_home, "explicit", uid)
    runtime_namespace = "sha256:" + hashlib.sha256((host["id"] + ":runtime").encode()).hexdigest()
    source_health = host["health"]
    saved_status = "partial" if source_health == "partial" else "complete"
    source = {
        "provider": "codex",
        "namespace": namespace,
        "runtimeNamespace": runtime_namespace,
        "configHome": config_home,
        "configHomeKind": "explicit",
        "runtime": {
            "version": "fictional-cache",
            "binarySha256": "0" * 64,
            "topology": "native_managed_endpoint",
            "bootId": "e1000000-0000-4000-8000-000000000001",
            "pid": None,
            "startTicks": 1,
            "endpoint": None,
        },
        "sourceHealth": source_health,
        "coverage": {
            "saved": {
                "status": saved_status,
                "reason": "metadata_scan" if saved_status == "partial" else "native_snapshot",
            },
            "runtime": {
                "status": "complete",
                "reason": "native_snapshot",
                "scope": "daemon_threads",
            },
        },
        "capabilities": {
            "phase": ["working", "blocked", "waiting"],
            "blockedReasons": ["approval"],
            "runtime": ["running", "parked"],
            "activity": True,
            "timing": {"lastUpdated": False, "latestTurn": False},
        },
        "errors": [],
        "limitations": ["fictional_demo_cache"],
        "discovery": None,
    }
    sessions = []
    for item in host["sessions"]:
        observed_at = now_ms - item["activitySecondsAgo"] * 1000
        runtime_value = item["runtime"]
        phase = None if item["phase"] is None else _fact(
            item["phase"], observed_at, "codex_rpc", "current", "native_snapshot"
        )
        runtime_fact = _fact(runtime_value, observed_at, "codex_rpc", "current", "native_snapshot")
        workspace = {
            "health": "current",
            "reason": "mapped",
            "root": item["workspaceRoot"],
            "rootKey": item["workspaceKey"],
            "relativePath": item["workspacePath"],
            "projectKey": item["projectKey"],
            "repo": {
                "root": item["repoRoot"],
                "commonDir": item["repoRoot"] + "/.git",
                "relativePath": item["repoPath"],
            },
        }
        sessions.append(
            {
                "identity": {
                    "hostScope": host["id"],
                    "provider": "codex",
                    "namespace": namespace,
                    "nativeIdKind": "thread",
                    "nativeId": item["id"],
                },
                "nativeIds": {"threadId": item["id"], "sessionTreeRootId": item["id"]},
                "title": item["title"],
                "kind": "user",
                "cwd": item["cwd"],
                "cwdSource": "codex_rpc",
                "inventory": "saved" if runtime_value == "parked" else "live",
                "hasSavedHistory": True,
                "phase": phase,
                "runtime": runtime_fact,
                "outcome": _fact("unknown", None, None, "unsupported", "outcome_source_unproved"),
                "blockedReasons": item["blockedReasons"],
                "createdAt": observed_at - 60_000,
                "activity": {
                    "at": observed_at,
                    "source": "codex_rpc",
                    "health": "current",
                    "reason": "native_timestamp",
                },
                "lastUpdated": {
                    "at": None,
                    "timestampPrecisionMs": None,
                    "observedAt": None,
                    "source": None,
                    "health": "unsupported",
                    "reason": "timing_source_unproved",
                    "receipt": None,
                },
                "latestTurn": {
                    "value": None,
                    "observedAt": None,
                    "source": None,
                    "health": "unsupported",
                    "reason": "timing_source_unproved",
                    "receipt": None,
                },
                "workspace": workspace,
                "metadataIssues": [],
            }
        )
    return {
        "schemaVersion": 6,
        "collectionId": str(uuid5(NAMESPACE_URL, "fleet-plus-terminal:" + host["id"])),
        "collectedAt": now_ms,
        "host": {
            "authority": host["id"],
            "authoritySource": "caller",
            "nativeHostname": "fictional-node",
            "uid": uid,
        },
        "sourceHealth": source_health,
        "sources": [source],
        "sessions": sessions,
        "errors": [],
        "limitations": ["fictional_demo_cache"],
    }


def _write_config(directory: Path, hosts: list[dict[str, Any]], declarations: list[dict[str, Any]]) -> Path:
    lines = [
        "version = 1",
        "default_sources = " + json.dumps([item["id"] for item in declarations]),
    ]
    for item in declarations:
        lines.extend(["", "[[sources]]"])
        lines.extend(f"{key} = {json.dumps(value)}" for key, value in item.items())
    config = directory / "terminal.toml"
    config.write_text("\n".join(lines) + "\n", encoding="utf-8")
    config.chmod(0o600)
    return config


def _start_native_service(host: dict[str, Any], directory: Path) -> tuple[Any, threading.Event, threading.Thread, list[BaseException]]:
    from agent_observer.service_runtime import Runtime
    from agent_observer.service_state import ServiceState

    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    directory.chmod(0o700)
    state = ServiceState(
        host_scope=host["id"],
        configs={"codex": ("/fixture/codex", "explicit")},
        uid=os.geteuid(),
        working_set_window_ms=WINDOW_MS,
    )
    runtime_snapshot = make_snapshot(host, os.geteuid())
    history_snapshot = copy.deepcopy(runtime_snapshot)
    history_snapshot["collectionId"] = str(uuid5(NAMESPACE_URL, "fleet-plus-terminal-history:" + host["id"]))
    for component in ("runtime", "history"):
        snapshot = runtime_snapshot if component == "runtime" else history_snapshot
        sampled = state.clock()
        state.attempt("codex", component)
        accepted = state.accept(
            "codex",
            component,
            snapshot,
            sampled_ms=sampled,
            ttl_ms=36_000_000,
            runtime_ttl_ms=36_000_000,
            accepted_boottime_ms=state.clock(),
        )
        if not accepted:
            raise CaptureError(f"fictional cache fixture was refused by source state ({component})")
    service_path = directory / "reader.sock"
    runtime = Runtime(
        state,
        service_path,
        collect=False,
        io_timeout_ms=1000,
        heartbeat_ms=500,
    )
    stop = threading.Event()
    errors: list[BaseException] = []

    def serve() -> None:
        try:
            runtime.run(stop)
        except BaseException as error:
            errors.append(error)

    thread = threading.Thread(target=serve, name=f"fixture-service-{host['id']}", daemon=True)
    thread.start()
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and not errors:
        try:
            if service_path.stat().st_mode & 0o777 == 0o600:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as probe:
                    probe.settimeout(0.2)
                    probe.connect(str(service_path))
                return runtime, stop, thread, errors
        except OSError:
            pass
        time.sleep(0.01)
    stop.set()
    thread.join(2)
    raise CaptureError(f"fictional cache service did not become ready: {errors}")


async def serve_fixture_publishers(directory: Path, scenario_path: Path) -> None:
    """Own local Service sockets and synthetic Mesh publishers until SIGTERM."""
    from mesh_plus.api import Bridge
    from mesh_plus.transport import IPCServer
    from agent_observer.mesh_working_set_publisher import make_working_set_publisher

    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    directory.chmod(0o700)
    loop = asyncio.get_running_loop()
    stopping = asyncio.Event()
    for signum in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(signum, stopping.set)
    runtimes: list[tuple[Any, threading.Event, threading.Thread, list[BaseException]]] = []
    servers: list[Any] = []
    channels: list[set[Any]] = []
    declarations: list[dict[str, Any]] = []
    try:
        for index, host in enumerate(scenario["hosts"], 1):
            native_dir = directory / f"native-{index}"
            runtime_data = _start_native_service(host, native_dir)
            runtimes.append(runtime_data)
            publisher = make_working_set_publisher(
                host["id"], "agent_working_set", native_dir / "reader.sock", window_ms=WINDOW_MS
            )
            live_channels: set[Any] = set()
            channels.append(live_channels)

            async def handle(channel: Any, *, owned_publisher: Any = publisher, owned_channels: set[Any] = live_channels) -> None:
                owned_channels.add(channel)
                try:
                    await Bridge(owned_publisher).serve(channel)
                finally:
                    owned_channels.discard(channel)

            mesh_socket = directory / f"mesh-{index}.sock"
            servers.append(await IPCServer(mesh_socket, handle).start())
            snapshot = make_snapshot(host, os.geteuid())
            declarations.append(
                {
                    "id": host["id"],
                    "host": host["id"],
                    "home": "default",
                    "label": host["label"],
                    "mesh_source": "agent_working_set",
                    "scope": "local",
                    "socket": str(mesh_socket),
                    "namespace": snapshot["sources"][0]["namespace"],
                    "window_hours": WINDOW_MS // 3_600_000,
                    "max_identities": 1024,
                    "max_payload_mib": 4,
                }
            )
        config = _write_config(directory, scenario["hosts"], declarations)
        ready = {
            "status": "ready",
            "synthetic": True,
            "nativeProviderCalls": 0,
            "hosts": [host["id"] for host in scenario["hosts"]],
            "members": sum(len(host["sessions"]) for host in scenario["hosts"]),
            "fixtureSha256": sha256_file(scenario_path),
            "config": str(config),
        }
        staging = directory / "ready.json.tmp"
        staging.write_text(json.dumps(ready, sort_keys=True) + "\n", encoding="utf-8")
        staging.chmod(0o600)
        staging.replace(directory / "ready.json")
        print(json.dumps(ready, sort_keys=True), flush=True)
        await stopping.wait()
    finally:
        await asyncio.gather(
            *(channel.close() for group in channels for channel in tuple(group)),
            return_exceptions=True,
        )
        await asyncio.gather(*(server.close() for server in servers), return_exceptions=True)
        for _, stop, thread, _ in runtimes:
            stop.set()
        for _, _, thread, errors in runtimes:
            thread.join(4)
            if thread.is_alive():
                raise CaptureError("owned fixture service thread did not stop")
            if errors:
                raise CaptureError(f"owned fixture service exited with errors: {errors}")


def _cleanup_publisher_startup(process: subprocess.Popen[str]) -> dict[str, Any]:
    """Terminate, reap, and close pipes for a publisher that failed readiness."""
    cleanup_errors: list[str] = []
    terminate_requested = False
    kill_requested = False
    if process.poll() is None:
        try:
            process.terminate()
            terminate_requested = True
        except ProcessLookupError:
            pass
        except OSError as error:
            cleanup_errors.append(f"terminate failed: {error}")
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            process.kill()
            kill_requested = True
        except ProcessLookupError:
            pass
        except OSError as error:
            cleanup_errors.append(f"kill failed: {error}")
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            cleanup_errors.append("process did not exit after kill")
        except OSError as error:
            cleanup_errors.append(f"wait after kill failed: {error}")
    except OSError as error:
        cleanup_errors.append(f"wait failed: {error}")

    stderr = ""
    if process.poll() is not None and process.stderr is not None:
        try:
            stderr = process.stderr.read()
        except (OSError, ValueError) as error:
            cleanup_errors.append(f"stderr read failed: {error}")
    for name, stream in (("stdout", process.stdout), ("stderr", process.stderr)):
        if stream is None:
            continue
        try:
            stream.close()
        except OSError as error:
            cleanup_errors.append(f"{name} close failed: {error}")
    return {
        "returnCode": process.poll(),
        "terminateRequested": terminate_requested,
        "killRequested": kill_requested,
        "stdoutClosed": process.stdout is None or process.stdout.closed,
        "stderrClosed": process.stderr is None or process.stderr.closed,
        "stderr": stderr[-2000:],
        "errors": cleanup_errors,
    }


def start_publishers(
    python: Path,
    scenario: Path,
    directory: Path,
    *,
    startup_timeout_seconds: float = 12,
) -> tuple[subprocess.Popen[str], dict[str, Any]]:
    process = subprocess.Popen(
        [str(python), "-B", str(Path(__file__).resolve()), "--serve-fixtures", str(directory), "--scenario", str(scenario)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
        cwd=directory,
        env={**os.environ, "PYTHONSAFEPATH": "1"},
    )
    try:
        deadline = time.monotonic() + startup_timeout_seconds
        if process.stdout is None:
            raise CaptureError("owned fixture publisher stdout pipe was not created")
        while time.monotonic() < deadline:
            ready, _, _ = select.select([process.stdout], [], [], 0.1)
            if ready:
                line = process.stdout.readline()
                if line:
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError as error:
                        preview = line.rstrip()[:500]
                        raise CaptureError(
                            f"owned fixture publisher sent malformed ready JSON: {preview!r}"
                        ) from error
                    if not isinstance(payload, dict):
                        raise CaptureError(
                            f"owned fixture publisher ready JSON must be an object, got {type(payload).__name__}"
                        )
                    if payload.get("status") != "ready" or payload.get("nativeProviderCalls") != 0:
                        raise CaptureError(
                            f"owned fixture publishers did not report a safe ready state: {payload!r}"
                        )
                    return process, payload
            if process.poll() is not None:
                raise CaptureError(f"owned fixture publisher exited {process.returncode} before readiness")
        raise CaptureError("owned fixture publishers timed out before ready")
    except BaseException as error:
        cleanup = _cleanup_publisher_startup(process)
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            raise
        details = (
            f"publisher cleanup: exit={cleanup['returnCode']}, "
            f"terminated={cleanup['terminateRequested']}, killed={cleanup['killRequested']}, "
            f"stdout_closed={cleanup['stdoutClosed']}, stderr_closed={cleanup['stderrClosed']}"
        )
        if cleanup["stderr"]:
            details += f"; publisher stderr: {cleanup['stderr']}"
        if cleanup["errors"]:
            details += "; cleanup errors: " + "; ".join(cleanup["errors"])
        raise CaptureError(f"{error}; {details}") from error


def stop_publishers(process: subprocess.Popen[str]) -> dict[str, Any]:
    if process.poll() is not None:
        if process.returncode != 0:
            detail = process.stderr.read() if process.stderr else ""
            raise CaptureError(f"owned fixture publisher exited {process.returncode}: {detail[-2000:]}")
        return {"exitCode": process.returncode, "sigtermRequested": False, "ownedChildrenClosed": True}
    process.terminate()
    try:
        process.wait(timeout=7)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=3)
        raise CaptureError("owned fixture publisher required SIGKILL during cleanup")
    if process.returncode != 0:
        detail = process.stderr.read() if process.stderr else ""
        raise CaptureError(f"owned fixture publisher exited {process.returncode}: {detail[-2000:]}")
    return {"exitCode": process.returncode, "sigtermRequested": True, "ownedChildrenClosed": True}


class DashboardPTY:
    def __init__(self, python: Path, config: Path, cwd: Path, width: int, height: int, *, color: str = "always"):
        if color not in {"always", "never"}:
            raise ValueError(f"unsupported capture color mode: {color}")
        self.width, self.height = width, height
        self.color_mode = color
        self.master, self.slave = pty.openpty()
        self.original_termios = termios.tcgetattr(self.slave)
        self._set_size(width, height)
        self.screen = AuditedScreen(width, height)
        self.stream = pyte.ByteStream(self.screen)
        self.raw = bytearray()
        self.bytes_read = 0
        child_code = (
            "import fcntl,os,sys,termios;"
            "fcntl.ioctl(0,termios.TIOCSCTTY,0);"
            "os.tcsetpgrp(0,os.getpgrp());"
            "from agent_observer.cli import main;"
            "raise SystemExit(main(sys.argv[1:]))"
        )
        env = {**os.environ, "TERM": "xterm-256color", "COLORTERM": "truecolor", "PYTHONSAFEPATH": "1"}
        for key in ("NO_COLOR", "PYTHONPATH"):
            env.pop(key, None)
        self.process = subprocess.Popen(
            [
                str(python),
                "-B",
                "-c",
                child_code,
                "dashboard",
                "--config",
                str(config),
                "--icons",
                "never",
                "--color",
                color,
            ],
            cwd=cwd,
            stdin=self.slave,
            stdout=self.slave,
            stderr=self.slave,
            close_fds=True,
            start_new_session=True,
            env=env,
        )

    def _set_size(self, width: int, height: int) -> None:
        fcntl.ioctl(self.slave, termios.TIOCSWINSZ, struct.pack("HHHH", height, width, 0, 0))

    def text(self) -> str:
        return "\n".join(self.screen.display)

    def selected(self) -> str | None:
        return next((line.strip() for line in self.screen.display if line.lstrip().startswith(">")), None)

    def read_for(self, seconds: float) -> None:
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            ready, _, _ = select.select([self.master], [], [], min(0.025, max(0, end - time.monotonic())))
            if not ready:
                continue
            try:
                data = os.read(self.master, 65536)
            except OSError:
                break
            if not data:
                break
            self.bytes_read += len(data)
            self.stream.feed(data)
            self.raw.extend(data)
            if len(self.raw) > 4 * 1024 * 1024:
                del self.raw[:-4 * 1024 * 1024]

    def until(self, predicate: Any, *, timeout: float = 12, stage: str) -> None:
        deadline = time.monotonic() + timeout
        while not predicate():
            if self.process.poll() is not None:
                raise CaptureError(f"dashboard exited before {stage}; output:\n{self.text()}")
            if time.monotonic() >= deadline:
                raise CaptureError(f"dashboard timed out at {stage}; output:\n{self.text()}")
            self.read_for(0.02)

    def key(self, value: bytes, predicate: Any, *, stage: str, timeout: float = 12) -> None:
        os.write(self.master, value)
        self.until(predicate, stage=stage, timeout=timeout)
        self.read_for(0.12)

    def resize(self, width: int, height: int) -> None:
        self.width, self.height = width, height
        self.screen.resize(lines=height, columns=width)
        self._set_size(width, height)
        self.process.send_signal(signal.SIGWINCH)
        self.until(lambda: len(self.screen.display) == height, timeout=5, stage=f"resize {width}x{height}")
        self.read_for(0.4)

    def quit(self) -> None:
        if self.process.poll() is not None:
            return
        os.write(self.master, b"\x1bq")
        deadline = time.monotonic() + 6
        while self.process.poll() is None and time.monotonic() < deadline:
            self.read_for(0.05)
        if self.process.poll() is None:
            raise CaptureError("dashboard did not exit after Escape and q")

    def close(self) -> dict[str, Any]:
        if self.process.poll() is None:
            try:
                self.quit()
            except CaptureError:
                self.process.send_signal(signal.SIGTERM)
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(self.process.pid, signal.SIGKILL)
                    self.process.wait(timeout=3)
            if self.process.poll() is None:
                os.killpg(self.process.pid, signal.SIGKILL)
                self.process.wait(timeout=3)
        restored = termios.tcgetattr(self.slave) == self.original_termios
        if not restored:
            termios.tcsetattr(self.slave, termios.TCSANOW, self.original_termios)
        os.close(self.master)
        os.close(self.slave)
        if not restored:
            raise CaptureError("dashboard did not restore PTY terminal flags")
        if self.process.returncode not in {0, -signal.SIGTERM}:
            raise CaptureError(f"dashboard exited unexpectedly with status {self.process.returncode}")
        return {
            "childExit": self.process.returncode,
            "terminalFlagsRestored": restored,
            "ptyBytesRead": self.bytes_read,
            "ansiOutputSha256": sha256_bytes(bytes(self.raw)),
        }


class AuditedScreen(pyte.Screen):
    """Keep a small audit trail tying rendered text to the SGR state that drew it."""

    TARGET_NEEDLES = ("quartz-build/default", "juniper-lab/default")

    def __init__(self, columns: int, lines: int):
        super().__init__(columns, lines)
        self.last_foreground_sgr: tuple[int, ...] = ()
        self.draw_color_events: list[dict[str, Any]] = []

    def select_graphic_rendition(self, *attrs: int) -> None:
        super().select_graphic_rendition(*attrs)
        # 0, 30-38, 39, and 90-97 can set/reset the foreground. pyte
        # converts RGB SGR 38;2;r;g;b to a six-hex string on the cell.
        if any(attr == 0 or attr in {38, 39} or 30 <= attr <= 37 or 90 <= attr <= 97 for attr in attrs):
            self.last_foreground_sgr = tuple(attrs)

    def draw(self, data: str) -> None:
        for needle in self.TARGET_NEEDLES:
            if needle in data:
                self.draw_color_events.append(
                    {
                        "needle": needle,
                        "cursor": {"column": self.cursor.x, "row": self.cursor.y},
                        "text": data,
                        "foreground": str(self.cursor.attrs.fg),
                        "background": str(self.cursor.attrs.bg),
                        "foregroundSgr": list(self.last_foreground_sgr),
                    }
                )
        if len(self.draw_color_events) > 500:
            del self.draw_color_events[:-500]
        super().draw(data)


def screen_svg(screen: pyte.Screen) -> str:
    """Render the actual PTY cell colors and glyphs into an SVG terminal raster."""
    width = screen.columns * CELL_WIDTH
    height = screen.lines * CELL_HEIGHT
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{DEFAULT_BG}"/>',
        f'<g font-family="{FONT_FAMILY}" font-size="{FONT_SIZE}" xml:space="preserve">',
    ]
    for y in range(screen.lines):
        cells = [screen.buffer[y][x] for x in range(screen.columns)]
        x = 0
        while x < screen.columns:
            char = cells[x]
            fg = _color(char.fg, DEFAULT_FG)
            bg = _color(char.bg, DEFAULT_BG)
            reverse = bool(getattr(char, "reverse", False))
            if reverse:
                fg, bg = bg, fg
            bold = bool(getattr(char, "bold", False))
            italic = bool(getattr(char, "italics", False))
            underline = bool(getattr(char, "underscore", False))
            strike = bool(getattr(char, "strikethrough", False))
            end = x + 1
            while end < screen.columns:
                other = cells[end]
                other_fg = _color(other.fg, DEFAULT_FG)
                other_bg = _color(other.bg, DEFAULT_BG)
                other_reverse = bool(getattr(other, "reverse", False))
                if other_reverse:
                    other_fg, other_bg = other_bg, other_fg
                if (
                    (fg, bg, bold, italic, underline, strike)
                    != (
                        other_fg,
                        other_bg,
                        bool(getattr(other, "bold", False)),
                        bool(getattr(other, "italics", False)),
                        bool(getattr(other, "underscore", False)),
                        bool(getattr(other, "strikethrough", False)),
                    )
                ):
                    break
                end += 1
            x_px = x * CELL_WIDTH
            y_px = y * CELL_HEIGHT
            run_width = (end - x) * CELL_WIDTH
            if bg != DEFAULT_BG:
                pieces.append(
                    f'<rect x="{x_px}" y="{y_px}" width="{run_width}" height="{CELL_HEIGHT}" fill="{bg}"/>'
                )
            style = []
            if bold:
                style.append('font-weight="700"')
            if italic:
                style.append('font-style="italic"')
            decorations = []
            if underline:
                decorations.append("underline")
            if strike:
                decorations.append("line-through")
            if decorations:
                style.append('text-decoration="' + " ".join(decorations) + '"')
            content = "".join(cell.data or " " for cell in cells[x:end])
            pieces.append(
                f'<text x="{x_px}" y="{y_px + 19}" fill="{fg}" '
                + " ".join(style)
                + f'>{html.escape(content)}</text>'
            )
            x = end
    pieces.extend(["</g>", "</svg>"])
    return "\n".join(pieces)


def render_png(screen: pyte.Screen, output: Path) -> dict[str, Any]:
    svg = screen_svg(screen)
    with tempfile.TemporaryDirectory(prefix="fleet-terminal-svg-") as temporary:
        svg_path = Path(temporary) / f"{output.stem}.svg"
        svg_path.write_text(svg, encoding="utf-8")
        run_checked(["rsvg-convert", "--output", str(output), str(svg_path)])
    png = output.read_bytes()
    if png[:8] != b"\x89PNG\r\n\x1a\n":
        raise CaptureError(f"SVG renderer did not produce PNG: {output}")
    width = int.from_bytes(png[16:20], "big")
    height = int.from_bytes(png[20:24], "big")
    expected = (screen.columns * CELL_WIDTH, screen.lines * CELL_HEIGHT)
    if (width, height) != expected:
        raise CaptureError(f"unexpected PNG dimensions for {output.name}: {width}x{height} != {expected}")
    return {
        "file": output.name,
        "width": width,
        "height": height,
        "sha256": sha256_bytes(png),
        "terminalGeometry": f"{screen.columns}x{screen.lines}",
        "svgSha256": sha256_bytes(svg.encode()),
    }


def _color_audit(screen: AuditedScreen) -> dict[str, Any]:
    """Tie compact VT cell colors to the exact SGR parameters that drew the text."""
    needles = AuditedScreen.TARGET_NEEDLES
    rows = []
    for y, line in enumerate(screen.display):
        for needle in needles:
            start = line.find(needle)
            if start < 0:
                continue
            end = min(screen.columns, start + len(needle) + 32)
            cells = screen.buffer[y]
            runs = []
            last_style = None
            run_start = None
            run_text = []
            for x in range(start, end + 1):
                if x == end:
                    style = None
                else:
                    cell = cells[x]
                    style = (
                        str(cell.fg),
                        str(cell.bg),
                        bool(getattr(cell, "bold", False)),
                        bool(getattr(cell, "dim", False)),
                        bool(getattr(cell, "reverse", False)),
                    )
                if style != last_style:
                    if run_start is not None:
                        runs.append(
                            {"startColumn": run_start, "text": "".join(run_text), "pyteStyle": last_style}
                        )
                    run_start = x if style is not None else None
                    run_text = []
                    last_style = style
                if style is not None:
                    run_text.append(cells[x].data or " ")
            draw_events = [
                event
                for event in screen.draw_color_events
                if event["needle"] == needle and event["cursor"]["row"] == y
            ]
            if not draw_events:
                raise CaptureError(f"no PTY SGR draw event was recorded for compact row {needle!r}")
            foreground = str(cells[start].fg)
            if foreground == "default":
                raise CaptureError(f"unexpected terminal-default foreground on audited compact row {needle!r}")
            rows.append(
                {
                    "needle": needle,
                    "line": line,
                    "screenForeground": foreground,
                    "screenBackground": str(cells[start].bg),
                    "screenForegroundIsDefault": foreground == "default",
                    "renderedForeground": _color(cells[start].fg, DEFAULT_FG),
                    "runs": runs,
                    "ptyDrawEvents": draw_events[-3:],
                }
            )
    return {"defaultForeground": "default", "defaultForegroundRender": DEFAULT_FG, "rows": rows}


def visible_assertions(text: str, expected: list[str], stage: str) -> None:
    missing = [value for value in expected if value.casefold() not in text.casefold()]
    if missing:
        raise CaptureError(f"{stage} is missing expected native dashboard content {missing}:\n{text}")


def _font_evidence() -> dict[str, str]:
    output = run_checked(
        ["fc-match", "--format=%{family[0]}\t%{style[0]}\t%{file}\n", FONT_FAMILY]
    ).stdout.strip()
    try:
        family, style, file_name = output.split("\t", 2)
    except ValueError as error:
        raise CaptureError(f"fontconfig did not resolve the expected mono font: {output!r}") from error
    font_path = Path(file_name)
    if "Noto Sans Mono" not in family or "Regular" not in style or not font_path.is_file():
        raise CaptureError(f"expected regular Noto Sans Mono, got {output!r}")
    return {"family": family, "style": style, "sha256": sha256_file(font_path)}


def _render_tools() -> dict[str, str]:
    rsvg = run_checked(["rsvg-convert", "--version"]).stdout.splitlines()[0]
    ffmpeg = run_checked(["ffmpeg", "-version"]).stdout.splitlines()[0]
    return {"svgRasterizer": rsvg, "videoEncoder": ffmpeg}


def _encode_video(frames: list[Path], output: Path, work_dir: Path) -> dict[str, Any]:
    if len(frames) != len(VIDEO_SEGMENTS):
        raise CaptureError("demo requires exactly four captured PTY states")
    command: list[str] = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for path, seconds in zip(frames, VIDEO_SEGMENTS, strict=True):
        command.extend(["-loop", "1", "-framerate", str(VIDEO_FRAMES_PER_SECOND), "-t", str(seconds), "-i", str(path)])
    inputs = "".join(f"[{index}:v]" for index in range(len(frames)))
    command.extend(
        [
            "-filter_complex",
            f"{inputs}concat=n={len(frames)}:v=1:a=0,format=yuv420p[v]",
            "-map",
            "[v]",
            "-an",
            "-t",
            str(sum(VIDEO_SEGMENTS)),
            "-r",
            str(VIDEO_FRAMES_PER_SECOND),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "19",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    run_checked(command)
    result = json.loads(
        run_checked(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration:stream=codec_name,width,height,pix_fmt,r_frame_rate",
                "-of",
                "json",
                str(output),
            ]
        ).stdout
    )
    stream = next((item for item in result.get("streams", []) if item.get("codec_name")), None)
    duration = float(result.get("format", {}).get("duration", 0))
    if not stream or stream.get("codec_name") != "h264" or stream.get("pix_fmt") != "yuv420p":
        raise CaptureError(f"demo video is not browser-compatible H.264/yuv420p: {result}")
    if abs(duration - sum(VIDEO_SEGMENTS)) > 0.08:
        raise CaptureError(f"demo duration is {duration:.3f}s; expected {sum(VIDEO_SEGMENTS)}s")
    return {
        "codec": stream["codec_name"],
        "pixelFormat": stream["pix_fmt"],
        "width": stream["width"],
        "height": stream["height"],
        "frameRate": stream["r_frame_rate"],
        "durationSeconds": round(duration, 3),
        "segmentsSeconds": list(VIDEO_SEGMENTS),
        "faststart": True,
        "sha256": sha256_file(output),
    }


def _update_provenance(path: Path, entries: list[dict[str, Any]]) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    media = value.get("media")
    if not isinstance(media, list):
        raise CaptureError("assets/provenance.json has no media list")
    replacements = {entry["file"]: entry for entry in entries}
    kept = [item for item in media if item.get("file") not in replacements]
    value["media"] = [*kept, *(replacements[name] for name in replacements)]
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def capture(args: argparse.Namespace) -> dict[str, Any]:
    # Keep a venv's lexical bin/python path; Path.resolve() would follow its
    # symlink to the base interpreter and discard the installed site-packages.
    python = Path(os.path.abspath(args.python))
    scenario_path = args.scenario.resolve()
    output_dir = args.output_dir.resolve()
    observer_wheel = args.observer_wheel.resolve()
    mesh_wheel = args.mesh_wheel.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    fixture_sha = sha256_file(scenario_path)
    package_evidence = check_release_inputs(observer_wheel, mesh_wheel)
    dependency_evidence = check_capture_requirements()
    recipe_evidence = capture_recipe_evidence()
    font = _font_evidence()
    tools = _render_tools()
    expected_members = sum(len(host["sessions"]) for host in scenario["hosts"])
    if expected_members != 7 or len({item["id"] for host in scenario["hosts"] for item in host["sessions"]}) != 7:
        raise CaptureError("the public demo fixture must contain seven distinct fictional identities")
    if sum(host["health"] == "partial" for host in scenario["hosts"]) != 1:
        raise CaptureError("the public demo fixture must show one deliberately partial source")

    receipt: dict[str, Any] = {
        "status": "running",
        "package": {
            "observerTag": OBSERVER_TAG,
            "observerTagRevision": OBSERVER_TAG_REVISION,
            "observerSourceRevision": OBSERVER_SOURCE_REVISION,
            "captureDependencies": dependency_evidence,
            "captureRecipe": recipe_evidence,
            **package_evidence,
        },
        "fixture": {
            "path": "fixtures/terminal-dashboard-scenario.json",
            "sha256": fixture_sha,
            "hosts": [host["id"] for host in scenario["hosts"]],
            "memberCount": expected_members,
            "workingSetWindowHours": WINDOW_MS // 3_600_000,
            "nativeProviderCalls": 0,
            "partialSourceExample": "juniper-lab is deliberately fictional and partial to show source health, not a live incident",
            "searchTerm": scenario["search"],
            "nativeIdsDistinct": True,
        },
        "capture": {
            "method": "released agent-observer dashboard in a draining Linux PTY; pyte 0.8.2 VT cell parser; SVG text render via librsvg; no UI monkeypatch or redraw",
            "color": (
                "VT SGR parsed by pyte; default foreground stays `default` and maps to #e6edf3; explicit VT RGB "
                "foreground/background/bold/reverse attributes render as emitted. CLI color modes are recorded per asset."
            ),
            "font": font,
            "cellPixels": {"width": CELL_WIDTH, "height": CELL_HEIGHT, "fontSize": FONT_SIZE},
            "tools": tools,
            "geometries": {"wide": "140x24", "compact": "60x20", "demo": "140x32"},
            "workingSetWindowHours": WINDOW_MS // 3_600_000,
            "colorModes": {
                "wide": "--color always",
                "compact": "--color never",
                "compactColorAudit": "--color always at 60x20; audit only, not the published still",
                "demo": "--color always",
            },
            "segmentsSeconds": list(VIDEO_SEGMENTS),
            "transformations": [
                "VT screen cells rendered to SVG at the matching terminal grid without cropping or adding UI fields",
                "SVG rasterized to lossless PNG with librsvg",
                "four actual PTY states encoded as 30 fps H.264 yuv420p MP4 with faststart",
            ],
        },
        "media": [],
    }

    with tempfile.TemporaryDirectory(prefix="fleet-plus-terminal-capture-") as temporary:
        work_dir = Path(temporary)
        publisher_dir = work_dir / "publishers"
        publisher_dir.mkdir(mode=0o700)
        publisher, publisher_ready = start_publishers(python, scenario_path, publisher_dir)
        receipt["fixture"]["publisherReady"] = publisher_ready
        try:
            dashboard = DashboardPTY(python, Path(publisher_ready["config"]), work_dir, *WIDE_STILL, color="always")
            try:
                dashboard.until(
                    lambda: dashboard.selected() is not None
                    and f"{expected_members} members" in dashboard.text().lower(),
                    timeout=18,
                    stage="wide overview",
                )
                dashboard.read_for(0.3)
                wide_text = dashboard.text()
                visible_assertions(
                    wide_text,
                    [
                        "Refresh reader snapshots",
                        "Trace signal map",
                        "working",
                        "waiting",
                        "parked",
                        "blocked",
                        "partial",
                    ],
                    "wide overview",
                )
                wide_path = output_dir / "observer-terminal-wide.png"
                wide_meta = render_png(dashboard.screen, wide_path)
                wide_meta["visibleStateSha256"] = sha256_bytes(wide_text.encode())

                # Record the genuine color SGR state for readability review,
                # then capture the published compact still in supported
                # --color never mode from a separate PTY below.
                dashboard.resize(*COMPACT)
                dashboard.until(
                    lambda: dashboard.selected() is not None
                    and f"{expected_members} members" in dashboard.text().lower(),
                    timeout=8,
                    stage="compact overview",
                )
                dashboard.read_for(0.3)
                compact_color_audit = _color_audit(dashboard.screen)
                compact_color_audit["mode"] = "--color always at 60x20; diagnostic only"
                compact_color_audit["visibleStateSha256"] = sha256_bytes(dashboard.text().encode())

                dashboard.resize(*DEMO)
                dashboard.until(
                    lambda: dashboard.selected() is not None
                    and f"{expected_members} members" in dashboard.text().lower(),
                    timeout=8,
                    stage="wide overview restored",
                )
                dashboard.read_for(0.2)
                overview_frame = work_dir / "frame-01-overview.png"
                overview_frame_meta = render_png(dashboard.screen, overview_frame)

                term = scenario["search"]
                dashboard.key(
                    b"/",
                    lambda: "Type search" in dashboard.text() or "Search sessions" in dashboard.text(),
                    stage="open literal repository search",
                )
                dashboard.read_for(0.08)
                os.write(dashboard.master, b"\x01")
                dashboard.read_for(0.05)
                os.write(dashboard.master, b"\x0b")
                dashboard.read_for(0.05)
                os.write(dashboard.master, term.encode("ascii"))
                dashboard.until(
                    lambda: f"Search {term}" in dashboard.text()
                    and "1 matches" in dashboard.text()
                    and f"{expected_members} members" in dashboard.text(),
                    timeout=10,
                    stage="literal repository search result",
                )
                dashboard.key(
                    b"\r",
                    lambda: "Type search" not in dashboard.text(),
                    stage="commit repository search for demo",
                )
                dashboard.key(
                    b"j",
                    lambda: dashboard.selected() is not None
                    and "Trace signal map" in dashboard.selected(),
                    stage="select the matching repository session",
                )
                dashboard.read_for(0.2)
                search_text = dashboard.text()
                visible_assertions(
                    search_text,
                    ["signal-map", "1 matches", "Trace signal map"],
                    "repository search",
                )
                search_frame = work_dir / "frame-02-repository-search.png"
                search_frame_meta = render_png(dashboard.screen, search_frame)
                dashboard.key(
                    b"\r",
                    lambda: "Details" in dashboard.text() and "Session summary" in dashboard.text(),
                    stage="selected-session details",
                )
                dashboard.read_for(0.25)
                detail_text = dashboard.text()
                visible_assertions(
                    detail_text,
                    [
                        "Trace signal map",
                        "signal-map",
                        "Workspace",
                        "/workspaces/mesh-lab/packages/signal-map",
                        "Session summary",
                    ],
                    "selected-session details",
                )
                receipt["capture"]["selectedDetail"] = {
                    "title": "Trace signal map",
                    "workspace": "/workspaces/mesh-lab/packages/signal-map",
                    "searchTerm": term,
                    "selectedOverviewRow": dashboard.selected(),
                }
                details_frame = work_dir / "frame-03-selected-details.png"
                details_frame_meta = render_png(dashboard.screen, details_frame)
                dashboard.key(b"\x1b", lambda: "SESSION" in dashboard.text(), stage="return to overview")
                dashboard.key(
                    b"/",
                    lambda: "Type search" in dashboard.text() or "Search sessions" in dashboard.text(),
                    stage="clear repository search",
                )
                dashboard.read_for(0.05)
                os.write(dashboard.master, b"\x01")
                dashboard.read_for(0.05)
                os.write(dashboard.master, b"\x0b")
                dashboard.read_for(0.05)
                dashboard.key(
                    b"\r",
                    lambda: f"{expected_members} members" in dashboard.text().lower()
                    and "Type search" not in dashboard.text(),
                    stage="return to unfiltered overview",
                )
                dashboard.read_for(0.25)
                final_overview = dashboard.text()
                visible_assertions(final_overview, ["partial", "Refresh reader snapshots"], "closing overview")
                closing_frame = work_dir / "frame-04-overview-return.png"
                closing_frame_meta = render_png(dashboard.screen, closing_frame)
            finally:
                pty_evidence = dashboard.close()
            compact_dashboard = DashboardPTY(
                python,
                Path(publisher_ready["config"]),
                work_dir,
                *COMPACT,
                color="never",
            )
            try:
                compact_dashboard.until(
                    lambda: compact_dashboard.selected() is not None
                    and f"{expected_members} members" in compact_dashboard.text().lower(),
                    timeout=18,
                    stage="compact overview with native color disabled",
                )
                compact_dashboard.read_for(0.3)
                compact_text = compact_dashboard.text()
                visible_assertions(compact_text, ["partial", "complete"], "compact overview with color disabled")
                if any(
                    cell.fg != "default"
                    for row in compact_dashboard.screen.buffer.values()
                    for cell in row.values()
                    if cell.data.strip()
                ):
                    raise CaptureError("released CLI --color never still emitted colored foregrounds")
                compact_path = output_dir / "observer-terminal-compact.png"
                compact_meta = render_png(compact_dashboard.screen, compact_path)
                compact_meta["visibleStateSha256"] = sha256_bytes(compact_text.encode())
                compact_meta["colorMode"] = "--color never"
            finally:
                compact_pty_evidence = compact_dashboard.close()
        finally:
            cleanup_evidence = stop_publishers(publisher)

        demo_path = output_dir / "observer-terminal-demo.mp4"
        video = _encode_video(
            [overview_frame, search_frame, details_frame, closing_frame],
            demo_path,
            work_dir,
        )
        receipt["capture"]["pty"] = {"wideAndDemo": pty_evidence, "compactNever": compact_pty_evidence}
        receipt["capture"]["publisherCleanup"] = cleanup_evidence
        receipt["capture"]["compactColorAudit"] = compact_color_audit
        receipt["capture"]["screens"] = {
            "wide": wide_meta,
            "compact": compact_meta,
            "videoFrames": [overview_frame_meta, search_frame_meta, details_frame_meta, closing_frame_meta],
        }
        receipt["media"] = [
            {
                "file": wide_path.name,
                "sha256": sha256_file(wide_path),
                "width": wide_meta["width"],
                "height": wide_meta["height"],
                "terminalGeometry": "140x24",
                "colorMode": "--color always",
                "role": "poster and wide native dashboard still",
            },
            {
                "file": compact_path.name,
                "sha256": sha256_file(compact_path),
                "width": compact_meta["width"],
                "height": compact_meta["height"],
                "terminalGeometry": "60x20",
                "colorMode": "--color never",
                "role": "compact native mobile still from the same fictional sources",
            },
            {
                "file": demo_path.name,
                **video,
                "terminalGeometry": "140x32",
                "colorMode": "--color always",
                "role": "20-second four-state demo",
            },
        ]
        receipt["status"] = "passed"

    receipt["capture"]["cleanup"] = {
        **cleanup_evidence,
        "temporaryDirectoryRemoved": not Path(temporary).exists(),
        "wideAndDemoPTYRestored": pty_evidence["terminalFlagsRestored"],
        "compactNeverPTYRestored": compact_pty_evidence["terminalFlagsRestored"],
        "publisherProcessExited": publisher.poll() is not None,
    }

    if args.provenance:
        entries = []
        for item in receipt["media"]:
            file_name = item["file"]
            geometry = item.get("terminalGeometry", "140x32 PTY states")
            entries.append(
                {
                    "file": file_name,
                    "source_repository": "https://github.com/byebyebryan/agent-observer",
                    "source_revision": OBSERVER_SOURCE_REVISION,
                    "source_path": "agent_observer/terminal/dashboard.py",
                    "treatment": (
                        "Released Agent Observer 0.7.0a14 dashboard rendering from fictional cached sources; "
                        "not a live fleet or physical terminal recording. One synthetic source is deliberately "
                        "partial to demonstrate visible source health."
                    ),
                    "sha256": item["sha256"],
                    "capture": {
                        "release_tag": OBSERVER_TAG,
                        "release_tag_revision": OBSERVER_TAG_REVISION,
                        "observer_wheel_sha256": OBSERVER_WHEEL_SHA256,
                        "mesh_version": MESH_VERSION,
                        "mesh_wheel_sha256": MESH_WHEEL_SHA256,
                        "textual_version": TEXTUAL_VERSION,
                        "vt_renderer": "pyte 0.8.2",
                        "requirements_file": dependency_evidence["file"],
                        "requirements_sha256": dependency_evidence["sha256"],
                        "pinned_dependencies": dependency_evidence["pinnedVersions"],
                        "capture_recipe": recipe_evidence,
                        "fixture": "fixtures/terminal-dashboard-scenario.json",
                        "fixture_sha256": fixture_sha,
                        "method": receipt["capture"]["method"],
                        "font": f"{font['family']} {font['style']} (sha256 {font['sha256']})",
                        "rasterizer": tools["svgRasterizer"],
                        "geometry": geometry,
                        "cell_size_pixels": {
                            "width": CELL_WIDTH,
                            "height": CELL_HEIGHT,
                            "fontSize": FONT_SIZE,
                        },
                        "terminal_environment": {
                            "TERM": "xterm-256color",
                            "COLORTERM": "truecolor",
                        },
                        "transforms": (
                            [
                                "VT screen cells rendered to SVG at the matching terminal grid without cropping or adding UI fields",
                                "SVG rasterized to lossless PNG with librsvg",
                            ]
                            if not file_name.endswith(".mp4")
                            else [
                                "Four actual PTY states rendered as matching-grid PNG frames without cropping or adding UI fields",
                                "Each SVG frame rasterized to PNG with librsvg",
                                "PNG frames encoded as 30 fps H.264 yuv420p MP4 with faststart",
                            ]
                        ),
                        **({"video_encoder": tools["videoEncoder"]} if file_name.endswith(".mp4") else {}),
                        "color_mode": item.get("colorMode"),
                        "working_set_window_hours": WINDOW_MS // 3_600_000,
                    },
                }
            )
        _update_provenance(args.provenance.resolve(), entries)

    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--python", type=Path, help="isolated Python containing the exact released dashboard stack")
    result.add_argument("--observer-wheel", type=Path)
    result.add_argument("--mesh-wheel", type=Path)
    result.add_argument("--scenario", type=Path, required=True)
    result.add_argument("--output-dir", type=Path)
    result.add_argument("--provenance", type=Path, help="update only the three terminal media entries")
    result.add_argument("--receipt", type=Path, help="write a private capture receipt outside public assets")
    result.add_argument("--serve-fixtures", type=Path, metavar="PRIVATE-DIR", help=argparse.SUPPRESS)
    return result


def main() -> int:
    args = parser().parse_args()
    if args.serve_fixtures is not None:
        asyncio.run(serve_fixture_publishers(args.serve_fixtures, args.scenario))
        return 0
    if not all((args.python, args.observer_wheel, args.mesh_wheel, args.output_dir)):
        parser().error("capture requires --python, --observer-wheel, --mesh-wheel, and --output-dir")
    try:
        receipt = capture(args)
    except (CaptureError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"capture failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
