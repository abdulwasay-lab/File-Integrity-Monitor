# api/server.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

from config import WATCH_PATHS, API_HOST, API_PORT
from modules.scanner    import scan
from modules.baseline   import save_baseline, load_baseline, baseline_exists
from modules.comparator import compare

app = Flask(__name__)
CORS(app)

# ── In-memory store ───────────────────────────────────────
latest_findings  = []
last_scan_time   = None
dynamic_paths    = []          # paths added at runtime via the dashboard


def effective_paths():
    """Return the merged, deduplicated list of config + dynamic paths."""
    return list(dict.fromkeys(WATCH_PATHS + dynamic_paths))


# ── Routes ────────────────────────────────────────────────

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "baseline_exists": baseline_exists(),
        "watching":        len(effective_paths()),
        "paths":           effective_paths(),
        "last_scan":       last_scan_time,
    })


@app.route("/api/baseline", methods=["POST"])
def create_baseline():
    try:
        data = scan(effective_paths())
        save_baseline(data)
        return jsonify({
            "success":   True,
            "message":   "Baseline created successfully",
            "files":     len(data),
            "timestamp": datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/check", methods=["GET"])
def run_check():
    global latest_findings, last_scan_time

    try:
        if not baseline_exists():
            return jsonify({
                "success": False,
                "error":   "No baseline found. Create one first."
            }), 400

        baseline        = load_baseline()
        current         = scan(effective_paths())
        latest_findings = compare(baseline, current)
        last_scan_time  = datetime.now().isoformat()

        return jsonify({
            "success":   True,
            "timestamp": last_scan_time,
            "total":     len(latest_findings),
            "findings":  latest_findings,
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/findings", methods=["GET"])
def get_findings():
    return jsonify({
        "timestamp": last_scan_time,
        "total":     len(latest_findings),
        "findings":  latest_findings,
    })


@app.route("/api/summary", methods=["GET"])
def get_summary():
    summary = {
        "MODIFIED":     0,
        "DELETED":      0,
        "ADDED":        0,
        "PERM_CHANGE":  0,
        "OWNER_CHANGE": 0,
    }

    for f in latest_findings:
        if f["type"] in summary:
            summary[f["type"]] += 1

    return jsonify({
        "timestamp": last_scan_time,
        "summary":   summary,
        "total":     len(latest_findings),
    })


# ── Dynamic Path Management ───────────────────────────────

@app.route("/api/paths", methods=["GET"])
def get_paths():
    """Return all currently watched paths, flagged as config or dynamic."""
    paths = [
        {"path": p, "source": "config"}
        for p in WATCH_PATHS
    ] + [
        {"path": p, "source": "dynamic"}
        for p in dynamic_paths
    ]
    return jsonify({"paths": paths})


@app.route("/api/paths", methods=["POST"])
def add_path():
    """Add a new path to the dynamic watch list."""
    body = request.get_json(silent=True) or {}
    path = (body.get("path") or "").strip()

    if not path:
        return jsonify({"success": False, "error": "No path provided"}), 400

    if path in WATCH_PATHS or path in dynamic_paths:
        return jsonify({"success": False, "error": "Path is already being watched"}), 409

    dynamic_paths.append(path)
    return jsonify({
        "success": True,
        "message": f"Now watching: {path}",
        "paths":   effective_paths(),
    })


@app.route("/api/paths", methods=["DELETE"])
def remove_path():
    """Remove a path from the dynamic watch list (config paths cannot be removed)."""
    body = request.get_json(silent=True) or {}
    path = (body.get("path") or "").strip()

    if not path:
        return jsonify({"success": False, "error": "No path provided"}), 400

    if path in WATCH_PATHS:
        return jsonify({
            "success": False,
            "error":   "Config paths cannot be removed from the dashboard. Edit config.py to change them."
        }), 403

    if path not in dynamic_paths:
        return jsonify({"success": False, "error": "Path not found in watch list"}), 404

    dynamic_paths.remove(path)
    return jsonify({
        "success": True,
        "message": f"Removed: {path}",
        "paths":   effective_paths(),
    })


# ── Run Server ────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host=API_HOST, port=API_PORT, debug=True)
