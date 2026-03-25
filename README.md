# CS204 Project - VPN Performance Test

A simple tool that measures VPN impact on your connection by running 3 tests:

1. **Download speed** — via speedtest-cli
2. **Upload speed** — via speedtest-cli
3. **YouTube video download** — real-world throughput via yt-dlp

Run it once without a VPN, once with — compare the numbers.

## Setup

### Linux / Mac

```bash
git clone https://github.com/ctecte/cs204_project.git
cd cs204_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install speedtest-cli
```

### Windows (PowerShell)

```powershell
git clone https://github.com/ctecte/cs204_project.git
cd cs204_project
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install speedtest-cli
```

> If you get an execution policy error on Windows, run this first:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

## Usage

### 1. Test without VPN

Make sure your VPN is **disconnected**, then run:

```bash
python vpn_test.py --label "No VPN"
```

### 2. Test with VPN

Connect to your VPN, then run:

```bash
python vpn_test.py --label "ProtonVPN"
```

### 3. Compare

All runs accumulate in a single `results.json` file with timestamps, so you can see every test side by side.

## What It Measures

| Test | What it does |
|---|---|
| **Download Speed** | Measures raw download bandwidth (Mbps) via speedtest-cli |
| **Upload Speed** | Measures raw upload bandwidth (Mbps) via speedtest-cli |
| **yt-dlp Download** | Downloads a YouTube video and measures real-world throughput (Mbps) |

The speedtest gives synthetic bandwidth numbers. The yt-dlp download shows real-world performance since YouTube traffic is what most people actually use. VPN overhead should be clearly visible in the difference between runs.
