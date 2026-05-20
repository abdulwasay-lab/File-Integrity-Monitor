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

const pathInput    = document.getElementById("path-input");
const btnAddPath   = document.getElementById("btn-add-path");

const pathList     = document.getElementById("path-list");
const pathCount    = document.getElementById("path-count");

// ── Helpers ───────────────────────────────────────────────

function showStatus(message, type = "success") {

    statusMsg.textContent = message;
    statusMsg.className   = type;

    setTimeout(() => {
        statusMsg.className = "";
    }, 4000);
}

function formatTime(isoString) {

    if (!isoString) return "—";

    return new Date(isoString).toLocaleTimeString();
}

function escapeAttr(str) {

    return str
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

// ── Render Alerts Table ──────────────────────────────────

function renderTable(findings) {

    if (!findings || findings.length === 0) {

        alertsBody.innerHTML = `
            <tr>
                <td colspan="5" class="empty">
                    ✅ No changes detected. All files are intact.
                </td>
            </tr>
        `;

        return;
    }

    alertsBody.innerHTML = findings.map(f => {

        const sev = SEVERITY[f.type] || {
            label: "INFO",
            badge: "medium"
        };

        return `
            <tr>
                <td>
                    <span class="badge ${sev.badge}">
                        ${sev.label}
                    </span>
                </td>

                <td>${f.type.replace(/_/g, " ")}</td>

                <td>
                    <span class="filepath">
                        ${f.file}
                    </span>
                </td>

                <td>${f.detail}</td>

                <td>${formatTime(f.timestamp)}</td>
            </tr>
        `;

    }).join("");
}

// ── Watch Paths ───────────────────────────────────────────

async function loadPaths() {

    try {

        const res  = await fetch(`${API}/paths`);
        const data = await res.json();

        renderPaths(data.paths);

    } catch {

        pathList.innerHTML = `
            <li class="path-list-empty">
                ⚠️ Could not load paths
            </li>
        `;
    }
}

function renderPaths(paths) {

    if (!paths || paths.length === 0) {

        pathList.innerHTML = `
            <li class="path-list-empty">
                No paths configured yet.
            </li>
        `;

        pathCount.textContent = "0 paths";
        statWatched.textContent = "0";

        return;
    }

    pathCount.textContent =
        `${paths.length} path${paths.length !== 1 ? "s" : ""}`;

    statWatched.textContent = paths.length;

    pathList.innerHTML = paths.map(p => `

        <li class="path-item ${p.source === 'config'
            ? 'path-config'
            : 'path-dynamic'}">

            <span class="path-source-badge">
                ${p.source === 'config'
                    ? 'config'
                    : 'custom'}
            </span>

            <span class="path-text">
                ${p.path}
            </span>

            ${p.source === 'dynamic'

                ? `
                    <button
                        class="btn-remove-path"
                        data-path="${escapeAttr(p.path)}"
                        title="Remove path">
                        ✕
                    </button>
                `

                : `
                    <span
                        class="path-locked"
                        title="Defined in config.py — edit the file to change">
                        🔒
                    </span>
                `
            }

        </li>

    `).join("");

    // Attach remove listeners
    pathList
        .querySelectorAll(".btn-remove-path")
        .forEach(btn => {

            btn.addEventListener("click", () => {
                removePath(btn.dataset.path);
            });

        });
}

// ── Add Path ─────────────────────────────────────────────

async function addPath() {

    const path = pathInput.value.trim();

    if (!path) {

        showStatus(
            "⚠️ Please enter a path first",
            "error"
        );

        pathInput.focus();

        return;
    }

    btnAddPath.disabled = true;
    btnAddPath.textContent = "Adding...";

    try {

        const res = await fetch(`${API}/paths`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({ path })

        });

        const data = await res.json();

        if (data.success) {

            pathInput.value = "";

            showStatus(
                `✅ ${data.message}`,
                "success"
            );

            await loadPaths();

        } else {

            showStatus(
                `❌ ${data.error}`,
                "error"
            );
        }

    } catch {

        showStatus(
            "❌ Could not reach API",
            "error"
        );
    }

    btnAddPath.disabled = false;
    btnAddPath.textContent = "＋ Add Path";
}

// ── Remove Path ──────────────────────────────────────────

async function removePath(path) {

    try {

        const res = await fetch(`${API}/paths`, {

            method: "DELETE",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({ path })

        });

        const data = await res.json();

        if (data.success) {

            showStatus(
                `🗑️ ${data.message}`,
                "success"
            );

            await loadPaths();

        } else {

            showStatus(
                `❌ ${data.error}`,
                "error"
            );
        }

    } catch {

        showStatus(
            "❌ Could not reach API",
            "error"
        );
    }
}

// ── Enter Key Add Path ───────────────────────────────────

pathInput.addEventListener("keydown", e => {

    if (e.key === "Enter") {
        addPath();
    }

});

btnAddPath.addEventListener("click", addPath);

// ── Load Status ──────────────────────────────────────────

async function loadStatus() {

    try {

        const res  = await fetch(`${API}/status`);
        const data = await res.json();

        lastScan.textContent = data.last_scan

            ? `Last scan: ${formatTime(data.last_scan)}`

            : "Last scan: Never";

    } catch {

        showStatus(
            "Cannot connect to AgeisFIM API. Is server.py running?",
            "error"
        );
    }
}

// ── Load Summary ─────────────────────────────────────────

async function loadSummary() {

    try {

        const res  = await fetch(`${API}/summary`);
        const data = await res.json();

        const s = data.summary || {};

        statModified.textContent = s.MODIFIED ?? 0;
        statDeleted.textContent  = s.DELETED ?? 0;
        statAdded.textContent    = s.ADDED ?? 0;

        statPerm.textContent =
            ((s.PERM_CHANGE ?? 0) + (s.OWNER_CHANGE ?? 0));

    } catch {

        console.error("Failed to load summary");
    }
}

// ── Create Baseline ──────────────────────────────────────

btnBaseline.addEventListener("click", async () => {

    btnBaseline.disabled = true;
    btnBaseline.textContent = "Creating...";

    try {

        const res = await fetch(`${API}/baseline`, {
            method: "POST"
        });

        const data = await res.json();

        if (data.success) {

            showStatus(
                `✅ Baseline created — ${data.files} files tracked`,
                "success"
            );

        } else {

            showStatus(
                `❌ Error: ${data.error}`,
                "error"
            );
        }

    } catch {

        showStatus(
            "❌ Could not reach API",
            "error"
        );
    }

    btnBaseline.disabled = false;
    btnBaseline.textContent = "📸 Create Baseline";
});

// ── Run Integrity Check ──────────────────────────────────

btnCheck.addEventListener("click", async () => {

    btnCheck.disabled = true;
    btnCheck.textContent = "Scanning...";

    try {

        const res  = await fetch(`${API}/check`);
        const data = await res.json();

        if (data.success) {

            renderTable(data.findings);

            loadSummary();

            lastScan.textContent =
                `Last scan: ${formatTime(data.timestamp)}`;

            showStatus(

                data.total === 0

                    ? "✅ No changes detected"

                    : `⚠️ ${data.total} issue(s) found`,

                data.total === 0
                    ? "success"
                    : "error"
            );

        } else {

            showStatus(
                `❌ ${data.error}`,
                "error"
            );
        }

    } catch {

        showStatus(
            "❌ Could not reach API",
            "error"
        );
    }

    btnCheck.disabled = false;
    btnCheck.textContent = "🔍 Run Check";
});

// ── Init ─────────────────────────────────────────────────

// ── Matrix Background (canvas) ───────────────────────────
function initMatrix() {
    const canvas = document.getElementById('bg-matrix');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let w = canvas.width = window.innerWidth;
    let h = canvas.height = window.innerHeight;
    // performance-conscious settings
    const fontSize = Math.max(14, Math.floor(window.innerWidth / 160));
    let columns = Math.max(40, Math.floor(w / fontSize));

    // drops tracked in pixels for smoother motion
    let drops = new Array(columns).fill(0).map(() => ({
        y: Math.random() * h,
        speed: (0.01 + Math.random() * 0.04) // px per ms
    }));

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
        columns = Math.max(40, Math.floor(w / fontSize));
        drops = new Array(columns).fill(0).map(() => ({ y: Math.random() * h, speed: (0.01 + Math.random() * 0.04) }));
    }

    window.addEventListener('resize', resize);

    // throttle FPS to reduce CPU: target ~30 FPS
    const targetFPS = 30;
    const frameInterval = 1000 / targetFPS;
    let lastFrameTime = performance.now();
    let running = true;

    // pause when tab is hidden
    document.addEventListener('visibilitychange', () => {
        running = !document.hidden;
        if (running) {
            lastFrameTime = performance.now();
            requestAnimationFrame(draw);
        }
    });

    function draw(now) {
        if (!running) return;

        const elapsed = now - lastFrameTime;
        if (elapsed < frameInterval) {
            return requestAnimationFrame(draw);
        }
        lastFrameTime = now;

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            ctx.clearRect(0, 0, w, h);
            return requestAnimationFrame(draw);
        }

        // translucent black fill for trails: small alpha for long trails but not too heavy
        ctx.fillStyle = 'rgba(0,0,0,0.03)';
        ctx.fillRect(0, 0, w, h);

        ctx.font = fontSize + 'px monospace';
        ctx.textBaseline = 'top';

        // normal blending (no page glow)
        ctx.globalCompositeOperation = 'source-over';

        for (let i = 0; i < columns; i++) {
            const colX = i * fontSize;
            const drop = drops[i];

            // leading character green (no glow)
            ctx.shadowBlur = 0;
            ctx.fillStyle = 'rgba(0,255,80,1)';
            ctx.fillText(Math.random() > 0.5 ? '1' : '0', colX, drop.y);

            // one faint trailing char
            ctx.fillStyle = 'rgba(0,200,60,0.2)';
            drop.y += drop.speed * (elapsed);

            if (drop.y > h + fontSize * (3 + Math.random() * 6)) {
                drop.y = -Math.random() * h * 0.4;
                drop.speed = 0.01 + Math.random() * 0.05;
            }
        }

        ctx.globalCompositeOperation = 'source-over';

        requestAnimationFrame(draw);
    }

    requestAnimationFrame(draw);
}

loadStatus();
loadSummary();
loadPaths();

// start matrix background (non-blocking)
initMatrix();