#!/usr/bin/env python3
"""Drive one demo server through one or more scripted sessions.

Talks to baselines/demo/server.py over HTTP:
  1. wait for /api/health pipeline_loaded
  2. POST /api/start (image + prompt)
  3. queue all actions via /api/action/{sid}
  4. drain /api/events/{sid} until the last segment event arrives
  5. POST /api/stop, then copy the combined mp4 out of demo/sessions/{sid}
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
import uuid
from pathlib import Path
import urllib.request
import urllib.error


def log(msg: str) -> None:
    print(f"[driver {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def api_get(base: str, path: str, timeout: float = 60.0):
    with urllib.request.urlopen(base + path, timeout=timeout) as r:
        return json.loads(r.read().decode())


def api_post_json(base: str, path: str, payload: dict, timeout: float = 60.0):
    req = urllib.request.Request(
        base + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def api_start(base: str, image_path: Path, prompt: str, timeout: float = 120.0):
    boundary = uuid.uuid4().hex
    img_bytes = image_path.read_bytes()
    parts = []
    parts.append(
        (
            f'--{boundary}\r\nContent-Disposition: form-data; name="image"; '
            f'filename="{image_path.name}"\r\nContent-Type: image/png\r\n\r\n'
        ).encode()
        + img_bytes
        + b"\r\n"
    )
    parts.append(
        (
            f'--{boundary}\r\nContent-Disposition: form-data; name="prompt"\r\n\r\n{prompt}\r\n'
        ).encode()
    )
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    req = urllib.request.Request(
        base + "/api/start",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def wait_ready(base: str, timeout_s: float) -> None:
    t0 = time.time()
    last_report = 0.0
    while True:
        try:
            h = api_get(base, "/api/health", timeout=15)
        except (urllib.error.URLError, OSError, TimeoutError):
            h = None
        if h is not None:
            if h.get("error"):
                raise RuntimeError(f"adapter load failed: {h['error']}")
            if h.get("pipeline_loaded"):
                log(f"adapter '{h.get('adapter')}' ready after {time.time() - t0:.0f}s")
                return
        if time.time() - t0 > timeout_s:
            raise TimeoutError(f"server not ready after {timeout_s}s (health={h})")
        if time.time() - last_report > 60:
            log(f"waiting for adapter to load ... ({time.time() - t0:.0f}s, health={h})")
            last_report = time.time()
        time.sleep(5)


def find_combined(session_dir: Path) -> Path | None:
    candidates = [p for p in session_dir.glob("*.mp4") if "current_iteration" not in p.name and not p.name.startswith(".")]
    if not candidates:
        return None
    named = [p for p in candidates if p.name != "combined.mp4"]
    pool = named or candidates
    return max(pool, key=lambda p: p.stat().st_mtime)


def run_one_session(base: str, spec: dict, args) -> bool:
    name = spec["name"]
    actions = spec["actions"]
    n_seg = int(spec.get("expected_segments", len(actions)))
    out_path = Path(args.out_dir) / f"{name}.mp4"
    session_timeout = float(spec.get("timeout", args.session_timeout))

    log(f"=== session {name}: {len(actions)} action(s), expecting {n_seg} segment(s)")
    prompt = Path(args.prompt_file).read_text().strip()
    sid = api_start(base, Path(args.image), prompt)["session_id"]
    log(f"session id {sid}")

    for a in actions:
        api_post_json(base, f"/api/action/{sid}", a)
    log(f"queued {len(actions)} action(s)")

    t0 = time.time()
    seen_last = False
    error_msg = None
    max_seen = -1
    while time.time() - t0 < session_timeout:
        try:
            ev = api_get(base, f"/api/events/{sid}?timeout=30", timeout=60)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                log("events endpoint 404 (session gone)")
                break
            raise
        except (urllib.error.URLError, OSError, TimeoutError):
            time.sleep(2)
            continue
        et = ev.get("type")
        if et == "heartbeat":
            continue
        if et == "segment":
            max_seen = max(max_seen, int(ev.get("index", -1)))
            log(f"segment {ev.get('index')} done ({time.time() - t0:.0f}s elapsed)")
            if max_seen >= n_seg - 1:
                seen_last = True
                break
        elif et == "error":
            error_msg = ev.get("msg")
            log(f"ERROR event: {error_msg}")
            break
        elif et == "done":
            log("done event")
            break
        elif et in {"status", "generating"}:
            log(f"{et}: {ev.get('msg') or ev.get('action') or ''}")

    try:
        api_post_json(base, "/api/stop", {})
    except Exception as exc:  # noqa: BLE001
        log(f"stop failed (ignored): {exc!r}")
    time.sleep(5)

    session_dir = Path(args.sessions_dir) / sid
    combined = find_combined(session_dir)
    if combined is None:
        log(f"FAIL {name}: no combined video in {session_dir}")
        return False
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(combined, out_path)
    log(f"saved {out_path} (from {combined.name}, {out_path.stat().st_size / 1e6:.1f} MB)")
    if error_msg:
        log(f"NOTE {name}: finished with error event: {error_msg}")
        return False
    if not seen_last:
        log(f"NOTE {name}: only saw segments up to {max_seen} (wanted {n_seg - 1}); saved what exists")
        return max_seen >= 0
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--image", required=True)
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--sessions", required=True, help="path to JSON list of session specs")
    ap.add_argument("--sessions-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--load-timeout", type=float, default=5400)
    ap.add_argument("--session-timeout", type=float, default=21600)
    args = ap.parse_args()

    specs = json.loads(Path(args.sessions).read_text())
    wait_ready(args.base, args.load_timeout)

    ok = True
    for spec in specs:
        try:
            ok = run_one_session(args.base, spec, args) and ok
        except Exception as exc:  # noqa: BLE001
            log(f"FAIL {spec['name']}: {exc!r}")
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
