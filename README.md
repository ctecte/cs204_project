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

**Arguments:**

| Argument       | Required | Default    | Description                                      |
|----------------|----------|------------|--------------------------------------------------|
| `--baseline`   | No       |            | Run baseline test with no VPN                    |
| `--vpn`        | Yes*     |            | Name of the VPN being tested                     |
| `--location`   | No       | `nearest`  | Server location (e.g., `US-East`, `EU-West`)     |
| `--time`       | No       | `off-peak` | Time of day (`peak` or `off-peak`)               |
| `--iterations` | No       | `3`        | Number of speed test iterations per run           |

*Required unless using `--baseline`.

### Examples

```bash
# Baseline
python vpn_test.py --baseline

# Test ProtonVPN on nearest server during peak hours
python vpn_test.py --vpn "ProtonVPN" --location "nearest" --time "peak"

# Test Windscribe on a US-East server, 5 iterations
python vpn_test.py --vpn "Windscribe" --location "US-East" --time "off-peak" --iterations 5

# Test TunnelBear on a European server
python vpn_test.py --vpn "TunnelBear" --location "EU-West" --time "peak"
```

## What It Measures

Each run performs the following tests automatically:

| Test                  | What it does                                                        |
|-----------------------|---------------------------------------------------------------------|
| **IP leak check**     | Compares your current public IP to your baseline IP                 |
| **DNS leak check**    | Checks if DNS queries are going through the VPN tunnel              |
| **Speed test**        | Measures download speed, upload speed, and ping (Ookla)             |
| **Ping test**         | Sends 30 packets to measure latency, jitter, and packet loss        |
| **File download**     | Downloads a 100MB test file and times it                            |
| **Resource usage**    | Measures CPU and RAM usage of the VPN process                       |

## Output

All results are logged to `results.csv` with the following columns:

`timestamp, vpn_name, server_location, time_of_day, iteration, ping_ms, download_mbps, upload_mbps, jitter_ms, file_download_time_s, file_download_speed_mbps, avg_latency_ms, min_latency_ms, max_latency_ms, packet_loss_pct, dns_leak, ip_leak, public_ip, vpn_cpu_pct, vpn_ram_mb`

Baseline data is also saved to `baseline.json` for IP leak detection.

## Recommended Test Procedure

1. Run `--baseline` first
2. For each VPN:
   - Install the VPN app
   - Connect to the nearest server
   - Run the test script
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
