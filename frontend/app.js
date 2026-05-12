// frontend/app.js

const API = "http://127.0.0.1:5000/api";

// ── Severity Map ──────────────────────────────────────────
const SEVERITY = {
    MODIFIED:     { label: "HIGH",   badge: "high"   },
    DELETED:      { label: "HIGH",   badge: "high"   },
    OWNER_CHANGE: { label: "HIGH",   badge: "high"   },
    ADDED:        { label: "MEDIUM", badge: "medium" },
    PERM_CHANGE:  { label: "MEDIUM", badge: "medium" },
};

// ── DOM References ────────────────────────────────────────
const statWatched  = document.getElementById("stat-watched");
const statModified = document.getElementById("stat-modified");
const statDeleted  = document.getElementById("stat-deleted");
const statAdded    = document.getElementById("stat-added");
const statPerm     = document.getElementById("stat-perm");
const lastScan     = document.getElementById("last-scan");
const alertsBody   = document.getElementById("alerts-body");
const statusMsg    = document.getElementById("status-msg");
const btnBaseline  = document.getElementById("btn-baseline");
const btnCheck     = document.getElementById("btn-check");


// ── Helpers ───────────────────────────────────────────────

function showStatus(message, type = "success") {
    statusMsg.textContent = message;
    statusMsg.className   = type;
    setTimeout(() => { statusMsg.className = ""; }, 4000);
}

function formatTime(isoString) {
    if (!isoString) return "—";
    return new Date(isoString).toLocaleTimeString();
}

function renderTable(findings) {
    if (!findings || findings.length === 0) {
        alertsBody.innerHTML = `
            <tr>
                <td colspan="5" class="empty">
                    ✅ No changes detected. All files are intact.
                </td>
            </tr>`;
        return;
    }

    alertsBody.innerHTML = findings.map(f => {
        const sev = SEVERITY[f.type] || { label: "INFO", badge: "medium" };
        return `
            <tr>
                <td><span class="badge ${sev.badge}">${sev.label}</span></td>
                <td>${f.type.replace("_", " ")}</td>
                <td><span class="filepath">${f.file}</span></td>
                <td>${f.detail}</td>
                <td>${formatTime(f.timestamp)}</td>
            </tr>`;
    }).join("");
}


// ── Load Status on Page Load ──────────────────────────────

async function loadStatus() {
    try {
        const res  = await fetch(`${API}/status`);
        const data = await res.json();

        statWatched.textContent = data.watching ?? "—";
        lastScan.textContent    = data.last_scan
            ? `Last scan: ${formatTime(data.last_scan)}`
            : "Last scan: Never";

    } catch {
        showStatus("Cannot connect to FIM API. Is server.py running?", "error");
    }
}


// ── Load Summary ──────────────────────────────────────────

async function loadSummary() {
    try {
        const res  = await fetch(`${API}/summary`);
        const data = await res.json();
        const s    = data.summary;

        statModified.textContent = s.MODIFIED    ?? 0;
        statDeleted.textContent  = s.DELETED     ?? 0;
        statAdded.textContent    = s.ADDED       ?? 0;
        statPerm.textContent     = (s.PERM_CHANGE + s.OWNER_CHANGE) ?? 0;

    } catch {
        console.error("Failed to load summary");
    }
}


// ── Button — Create Baseline ──────────────────────────────

btnBaseline.addEventListener("click", async () => {
    btnBaseline.disabled    = true;
    btnBaseline.textContent = "Creating...";

    try {
        const res  = await fetch(`${API}/baseline`, { method: "POST" });
        const data = await res.json();

        if (data.success) {
            showStatus(`✅ Baseline created — ${data.files} files tracked`, "success");
        } else {
            showStatus(`❌ Error: ${data.error}`, "error");
        }

    } catch {
        showStatus("❌ Could not reach API", "error");
    }

    btnBaseline.disabled    = false;
    btnBaseline.textContent = "📸 Create Baseline";
});


// ── Button — Run Check ────────────────────────────────────

btnCheck.addEventListener("click", async () => {
    btnCheck.disabled    = true;
    btnCheck.textContent = "Scanning...";

    try {
        const res  = await fetch(`${API}/check`);
        const data = await res.json();

        if (data.success) {
            renderTable(data.findings);
            loadSummary();
            lastScan.textContent = `Last scan: ${formatTime(data.timestamp)}`;
            showStatus(
                data.total === 0
                    ? "✅ No changes detected"
                    : `⚠️ ${data.total} issue(s) found`,
                data.total === 0 ? "success" : "error"
            );
        } else {
            showStatus(`❌ ${data.error}`, "error");
        }

    } catch {
        showStatus("❌ Could not reach API", "error");
    }

    btnCheck.disabled    = false;
    btnCheck.textContent = "🔍 Run Check";
});


// ── Init ──────────────────────────────────────────────────
loadStatus();
loadSummary();
