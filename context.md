# CS204 VPN Project - Development Context

## What This Project Does

A simple VPN performance testing tool that runs 3 tests and compares results with and without a VPN:

1. **Download speed** — via speedtest-cli
2. **Upload speed** — via speedtest-cli
3. **YouTube video download** — real-world throughput via yt-dlp

## How It Works

- Run `python vpn_test.py --label "No VPN"` without VPN connected
- Run `python vpn_test.py --label "ProtonVPN"` with VPN connected
- All results accumulate in a single `results.json` with timestamps
- The `--label` flag is freeform — use whatever name you want
- Downloaded YouTube videos are automatically cleaned up after each test

## Dependencies

- `yt-dlp` — YouTube video downloader (pip)
- `speedtest-cli` — bandwidth test (pip)
- `deno` — JavaScript runtime required by yt-dlp to solve YouTube's JS challenges
- `cookies.txt` — Netscape-format YouTube cookies exported via "Get cookies.txt LOCALLY" Chrome extension (required because YouTube blocks VPN IPs as bots)

## Key Decisions & Issues Encountered

### Simplified from original version
The original script had ~540 lines with DNS leak checks, IP leak detection, ping tests, torrent downloads (aria2c), VPN process monitoring, CSV logging, and a baseline system. Stripped down to ~160 lines with just 3 meaningful tests.

### speedtest-cli vs Ookla speedtest
The system has `speedtest-cli` (Python pip package) not the Ookla binary. They use different JSON output formats — `speedtest-cli` returns bits/sec directly, Ookla returns bandwidth that needs `* 8 / 1_000_000` conversion.

### yt-dlp issues on Windows with VPN

1. **429 Too Many Requests** — YouTube flags shared VPN IPs as bots. Fixed by using `--cookies cookies.txt` with exported browser cookies.
2. **`--cookies-from-browser chrome` failed** — Chrome's DPAPI cookie encryption on Windows causes decryption failures. Switched to manual cookie file export instead.
3. **UTF-16 BOM encoding** — Windows Notepad saves cookies.txt as UTF-16 by default, causing `'utf-8' codec can't decode byte 0xff` error. Must save as UTF-8.
4. **JS challenge solver** — yt-dlp needs `deno` installed plus `--remote-components ejs:github` flag to solve YouTube's JavaScript challenges and get video formats (without it, only image thumbnails are returned).

### Windows venv activation
PowerShell doesn't show `(venv)` prefix when using `activate.bat`. Must use `.\venv\Scripts\Activate.ps1` instead. May require `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` first.

## Sample Results (No VPN baseline)

- Download: 865.94 Mbps
- Upload: 805.7 Mbps
- yt-dlp: 169.42 Mbps (708.96 MB video in 35.1s)
- Ping: 4.8 ms
