# api/server.py
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime

from config import WATCH_PATHS, API_HOST, API_PORT
from modules.scanner    import scan
from modules.baseline   import save_baseline, load_baseline, baseline_exists
from modules.comparator import compare

app = Flask(__name__)
CORS(app)

# ── In-memory store for latest findings ──────────────────
latest_findings = []
last_scan_time  = None


# ── Routes ───────────────────────────────────────────────

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "baseline_exists": baseline_exists(),
        "watching":        len(WATCH_PATHS),
        "paths":           WATCH_PATHS,
        "last_scan":       last_scan_time,
    })


@app.route("/api/baseline", methods=["POST"])
def create_baseline():
    try:
        data = scan()
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
        current         = scan()
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


# ── Run Server ───────────────────────────────────────────
if __name__ == "__main__":
    app.run(host=API_HOST, port=API_PORT, debug=True)
