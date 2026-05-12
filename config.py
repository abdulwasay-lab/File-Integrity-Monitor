# config.py  (Windows edition)

import os
import sys

# Enforce Windows
if sys.platform != "win32":
    raise EnvironmentError(
        "This config is for Windows only. "
        "Use the original config.py on Linux/macOS."
    )

# ─── Files & Folders to Monitor ───────────────────────────
#
#  Windows equivalents of the Linux critical-file list:
#
#   /etc/passwd        →  SAM + SYSTEM hive  (local account DB)
#   /etc/shadow        →  SECURITY hive      (credential store)
#   /etc/hosts         →  %SystemRoot%\System32\drivers\etc\hosts
#   /etc/sudoers       →  no direct equivalent; monitor sudoers-like
#                          GPO files or the SECURITY hive
#   /etc/ssh/sshd_config → OpenSSH for Windows config (if installed)
#   /etc/crontab       →  Scheduled-task XML files in Tasks\
#
WATCH_PATHS = [
    # Hosts file — common tampering target
    r"C:\Windows\System32\drivers\etc\hosts",

    # Registry hive backups (flat-file copies; the live hives are
    # locked by the kernel, so we watch the repair copies instead)
    r"C:\Windows\System32\config\RegBack\SAM",
    r"C:\Windows\System32\config\RegBack\SYSTEM",
    r"C:\Windows\System32\config\RegBack\SECURITY",
    r"C:\Windows\System32\config\RegBack\SOFTWARE",

    # OpenSSH server config (present only if the optional feature
    # "OpenSSH Server" is installed via Settings → Apps)
    r"C:\ProgramData\ssh\sshd_config",

    # Scheduled-tasks folder — equivalent of /etc/crontab
    r"C:\Windows\System32\Tasks",

    # Windows Defender exclusion config (attackers often modify this)
    r"C:\ProgramData\Microsoft\Windows Defender\Platform",
]

# ─── Baseline Settings ────────────────────────────────────
BASELINE_FILE = "baseline.json"

# ─── Monitor Settings ─────────────────────────────────────
CHECK_INTERVAL = 60          # seconds between checks in --monitor mode

# ─── Logging Settings ─────────────────────────────────────
#  Use os.path.join so the path is valid on Windows
LOG_FILE    = os.path.join("logs", "fim.log")
LOG_ENABLED = True

# ─── API Settings ─────────────────────────────────────────
API_HOST = "127.0.0.1"
API_PORT = 5000
