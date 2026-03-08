# CS204 Project - Best Free VPN Testing Tool

An automated testing tool that measures VPN performance, reliability, and privacy indicators. Connect to a VPN manually, run the script, and it logs all metrics to a CSV for analysis.

## Setup

```bash
git clone https://github.com/ctecte/cs204_project.git
cd cs204_project
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### Torrent test (optional)

The torrent test requires `aria2c`, a lightweight command-line torrent client. Install it if you want to test P2P performance:

```bash
# Linux (Debian/Ubuntu)
sudo apt install aria2

# Linux (Fedora)
sudo dnf install aria2

# macOS
brew install aria2

# Windows
choco install aria2
# or download from https://aria2.github.io/
```

## Usage

### 1. Run a baseline (no VPN connected)

This records your real IP and network performance without a VPN. You need this first so the tool can detect IP leaks later.

```bash
python vpn_test.py --baseline
```

### 2. Test a VPN

Connect to your VPN manually through its app, then run:

```bash
python vpn_test.py --vpn "ProtonVPN" --location "nearest" --time "peak"
```

To include the torrent download test, add `--torrent`:

```bash
python vpn_test.py --vpn "ProtonVPN" --location "nearest" --time "peak" --torrent
```

**Arguments:**

| Argument       | Required | Default    | Description                                          |
|----------------|----------|------------|------------------------------------------------------|
| `--baseline`   | No       |            | Run baseline test with no VPN                        |
| `--vpn`        | Yes*     |            | Name of the VPN being tested                         |
| `--location`   | No       | `nearest`  | Server location (e.g., `US-East`, `EU-West`)         |
| `--time`       | No       | `off-peak` | Time of day (`peak` or `off-peak`)                   |
| `--iterations` | No       | `3`        | Number of speed test iterations per run               |
| `--torrent`    | No       |            | Include torrent download test (requires `aria2c`)    |

*Required unless using `--baseline`.

### Examples

```bash
# Baseline (run this first, no VPN connected)
python vpn_test.py --baseline

# Test ProtonVPN on nearest server during peak hours
python vpn_test.py --vpn "ProtonVPN" --location "nearest" --time "peak"

# Test Windscribe on a US-East server, 5 iterations
python vpn_test.py --vpn "Windscribe" --location "US-East" --time "off-peak" --iterations 5

# Test TunnelBear with torrent test included
python vpn_test.py --vpn "TunnelBear" --location "EU-West" --time "peak" --torrent

# Test with everything: 5 iterations + torrent
python vpn_test.py --vpn "ProtonVPN" --location "US-West" --time "off-peak" --iterations 5 --torrent
```

## What It Measures

Each run performs the following tests automatically:

| Test                  | What it does                                                              |
|-----------------------|---------------------------------------------------------------------------|
| **IP leak check**     | Compares your current public IP to your baseline IP                       |
| **DNS leak check**    | Checks if DNS queries are going through the VPN tunnel                    |
| **Speed test**        | Measures download speed, upload speed, and ping (Ookla)                   |
| **Ping test**         | Sends 30 packets to measure latency, jitter, and packet loss              |
| **File download**     | Downloads a 100MB test file and times it                                  |
| **Resource usage**    | Measures CPU and RAM usage of the VPN process                             |
| **Torrent test**      | Downloads a legal torrent (Ubuntu ISO) for 2 minutes, measures speed and peer count. Also detects if the VPN blocks P2P traffic. Only runs with `--torrent` flag. |

### Torrent test details

- Uses a **legal torrent** (Ubuntu 24.04 desktop ISO) — completely safe to download
- Downloads for **2 minutes** then stops automatically, no seeding
- Measures: download speed (Mbps), number of peers connected, and whether P2P is blocked
- If the VPN blocks torrenting, you'll see `torrent_blocked: yes` and 0 speed in the results
- Temporary files are cleaned up automatically after each test
- The test is only run on the **first iteration** to save time and data caps

## Output

All results are logged to `results.csv` with the following columns:

| Column                      | Description                                    |
|-----------------------------|------------------------------------------------|
| `timestamp`                 | When the test ran                              |
| `vpn_name`                  | Name of VPN (or BASELINE)                      |
| `server_location`           | VPN server location tested                     |
| `time_of_day`               | peak or off-peak                               |
| `iteration`                 | Which speed test iteration (1, 2, 3...)        |
| `ping_ms`                   | Ping from speed test (ms)                      |
| `download_mbps`             | Download speed (Mbps)                          |
| `upload_mbps`               | Upload speed (Mbps)                            |
| `jitter_ms`                 | Jitter from ping test (ms)                     |
| `file_download_time_s`      | Time to download 100MB test file (seconds)     |
| `file_download_speed_mbps`  | File download speed (Mbps)                     |
| `avg_latency_ms`            | Average ping latency (ms)                      |
| `min_latency_ms`            | Minimum ping latency (ms)                      |
| `max_latency_ms`            | Maximum ping latency (ms)                      |
| `packet_loss_pct`           | Packet loss percentage                         |
| `dns_leak`                  | DNS leak detected (yes/no/possible)            |
| `ip_leak`                   | IP leak detected (yes/no)                      |
| `public_ip`                 | Public IP during test                          |
| `vpn_cpu_pct`               | VPN process CPU usage (%)                      |
| `vpn_ram_mb`                | VPN process RAM usage (MB)                     |
| `torrent_download_speed_mbps` | Torrent download speed (Mbps)                |
| `torrent_peers`             | Max peers connected during torrent test        |
| `torrent_blocked`           | Whether VPN blocked P2P (yes/no/skipped)       |

Baseline data is also saved to `baseline.json` for IP leak detection.

## Recommended Test Procedure

1. Run `--baseline` first (make sure no VPN is connected)
2. For each VPN:
   - Install the VPN app
   - Connect to the nearest server
   - Run the test script (with `--torrent` on at least one run per VPN)
   - Disconnect
   - Connect to a far server (e.g., another continent)
   - Run the test script again
   - Uninstall or fully close the VPN before testing the next one
3. Repeat at different times of day (peak vs off-peak) for more data
4. Import `results.csv` into a spreadsheet or use Python/R to analyze

## VPN Process Detection

The tool monitors CPU/RAM usage of VPN processes by scanning for these keywords in process names:

`vpn, wireguard, openvpn, proton, windscribe, nordvpn, tunnelbear, mullvad, hideme, atlas, privado, surfshark, wg-quick, openconnect`

If your VPN's process name doesn't match any of these, the resource usage will show as 0. You can add more keywords by editing the `vpn_keywords` list in `vpn_test.py`.
