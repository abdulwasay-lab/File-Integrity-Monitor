Here is the complete version with all commands:

---

**Step 1 — Open CMD as Administrator**
Right-click Command Prompt → Run as administrator

**Step 2 — Install dependencies**
```
py -m pip install flask flask-cors
```

**Step 3 — Create your test file**
```
mkdir C:\fim_test
echo This file is monitored by FIM > C:\fim_test\monitored.txt
```

**Step 4 — Navigate to project folder**
```
cd C:\Users\YourName\fim
```

**Step 5 — Check watched files**
```
python fim.py --status
```

**Step 6 — Create baseline**
```
python fim.py --baseline
```

**Step 7 — Run a single check**
```
python fim.py --check
```

**Step 8 — Start continuous monitoring**
```
python fim.py --monitor
```
This checks every 60 seconds automatically. Press Ctrl+C to stop.

**Step 9 — Tamper with the test file (to test alerts)**
```
echo tampered >> C:\fim_test\monitored.txt
```
Then run `--check` or wait for `--monitor` to catch it.

**Step 10 — Start the API server (open a second CMD as Admin)**
```
cd C:\Users\YourName\fim
python -m api.server
```

**Step 11 — Open the dashboard**
Double-click `frontend\index.html` in File Explorer

---

**Quick reference for daily use:**

| What you want | Command |
|---|---|
| See watched files | `python fim.py --status` |
| Create baseline | `python fim.py --baseline` |
| One-off check | `python fim.py --check` |
| Continuous monitor | `python fim.py --monitor` |
| Start dashboard API | `python -m api.server` |
