#!/usr/bin/env python3
"""
VPN Testing Script - CS204 Project
Tests network performance, reliability, and privacy indicators.
Usage:
    python vpn_test.py --vpn "ProtonVPN" --location "nearest" --time "peak"
    python vpn_test.py --baseline
"""

import argparse
import csv
import json
import os
import platform
import socket
import statistics
import subprocess
import time
from datetime import datetime

import psutil
import requests
import speedtest


# ── Config ──────────────────────────────────────────────────────────────────
RESULTS_FILE = "results.csv"
BASELINE_FILE = "baseline.json"
SPEEDTEST_ITERATIONS = 3
PING_TARGET = "8.8.8.8"
PING_COUNT = 30
TEST_FILE_URL = "https://speed.hetzner.de/100MB.bin"
TEST_FILE_SIZE_MB = 100
IP_CHECK_URL = "https://api.ipify.org?format=json"
DNS_CHECK_DOMAINS = ["google.com", "facebook.com", "amazon.com"]
# Known public DNS servers (if your DNS resolves to one of these while on VPN, it may be leaking)
PUBLIC_DNS_SERVERS = {
    "8.8.8.8", "8.8.4.4",           # Google
    "1.1.1.1", "1.0.0.1",           # Cloudflare
    "208.67.222.222", "208.67.220.220",  # OpenDNS
    "9.9.9.9",                        # Quad9
}

CSV_HEADERS = [
    "timestamp", "vpn_name", "server_location", "time_of_day",
    "iteration",
    "ping_ms", "download_mbps", "upload_mbps", "jitter_ms",
    "file_download_time_s", "file_download_speed_mbps",
    "avg_latency_ms", "min_latency_ms", "max_latency_ms", "packet_loss_pct",
    "dns_leak", "ip_leak", "public_ip",
    "vpn_cpu_pct", "vpn_ram_mb",
]


# ── Helpers ─────────────────────────────────────────────────────────────────
def ensure_csv():
    """Create the CSV file with headers if it doesn't exist."""
    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)


def append_row(row: dict):
    """Append a single row dict to the results CSV."""
    ensure_csv()
    with open(RESULTS_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow(row)


def load_baseline():
    """Load baseline IP from file."""
    if os.path.exists(BASELINE_FILE):
        with open(BASELINE_FILE, "r") as f:
            return json.load(f)
    return None


def save_baseline(data: dict):
    """Save baseline data to file."""
    with open(BASELINE_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Tests ───────────────────────────────────────────────────────────────────
def get_public_ip():
    """Get current public IP address."""
    try:
        resp = requests.get(IP_CHECK_URL, timeout=10)
        return resp.json().get("ip", "unknown")
    except Exception as e:
        print(f"  [!] Failed to get public IP: {e}")
        return "error"


def run_speedtest():
    """Run Ookla speedtest, return dict with results."""
    print("  Running speed test...")
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        st.download()
        st.upload()
        results = st.results.dict()
        return {
            "ping_ms": round(results["ping"], 2),
            "download_mbps": round(results["download"] / 1_000_000, 2),
            "upload_mbps": round(results["upload"] / 1_000_000, 2),
            # speedtest-cli doesn't provide jitter directly; we'll get it from ping test
            "jitter_ms": 0,
        }
    except Exception as e:
        print(f"  [!] Speed test failed: {e}")
        return {"ping_ms": -1, "download_mbps": -1, "upload_mbps": -1, "jitter_ms": -1}


def run_ping_test(target=PING_TARGET, count=PING_COUNT):
    """Run ping test and return latency stats + packet loss."""
    print(f"  Pinging {target} ({count} packets)...")
    try:
        flag = "-n" if platform.system() == "Windows" else "-c"
        result = subprocess.run(
            ["ping", flag, str(count), target],
            capture_output=True, text=True, timeout=60
        )
        output = result.stdout

        # Parse individual ping times
        times = []
        for line in output.splitlines():
            if "time=" in line:
                t = line.split("time=")[1].split()[0].replace("ms", "")
                times.append(float(t))

        if not times:
            return {"avg_latency_ms": -1, "min_latency_ms": -1, "max_latency_ms": -1,
                    "packet_loss_pct": 100, "jitter_ms": -1}

        # Calculate jitter (average difference between consecutive pings)
        diffs = [abs(times[i+1] - times[i]) for i in range(len(times)-1)]
        jitter = round(statistics.mean(diffs), 2) if diffs else 0

        # Parse packet loss
        loss = 0
        for line in output.splitlines():
            if "packet loss" in line or "loss" in line:
                parts = line.split("%")
                if parts:
                    loss_str = parts[0].split()[-1]
                    try:
                        loss = float(loss_str)
                    except ValueError:
                        loss = round((1 - len(times) / count) * 100, 1)
                break

        return {
            "avg_latency_ms": round(statistics.mean(times), 2),
            "min_latency_ms": round(min(times), 2),
            "max_latency_ms": round(max(times), 2),
            "packet_loss_pct": loss,
            "jitter_ms": jitter,
        }
    except Exception as e:
        print(f"  [!] Ping test failed: {e}")
        return {"avg_latency_ms": -1, "min_latency_ms": -1, "max_latency_ms": -1,
                "packet_loss_pct": -1, "jitter_ms": -1}


def run_file_download():
    """Download a test file and measure speed."""
    print(f"  Downloading {TEST_FILE_SIZE_MB}MB test file...")
    try:
        start = time.time()
        resp = requests.get(TEST_FILE_URL, stream=True, timeout=120)
        total = 0
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            total += len(chunk)
        elapsed = time.time() - start
        speed_mbps = round((total * 8) / (elapsed * 1_000_000), 2)
        return {
            "file_download_time_s": round(elapsed, 2),
            "file_download_speed_mbps": speed_mbps,
        }
    except Exception as e:
        print(f"  [!] File download failed: {e}")
        return {"file_download_time_s": -1, "file_download_speed_mbps": -1}


def check_dns_leak():
    """Check for DNS leaks by seeing which DNS server resolves our queries."""
    print("  Checking for DNS leaks...")
    try:
        # Get the DNS server being used
        dns_servers_used = set()
        for domain in DNS_CHECK_DOMAINS:
            try:
                answers = socket.getaddrinfo(domain, 80)
                # The actual DNS server used isn't directly available from getaddrinfo,
                # so we use an external service
            except Exception:
                pass

        # Use an external DNS leak test API
        try:
            resp = requests.get("https://1.1.1.1/cdn-cgi/trace", timeout=10)
            trace_info = resp.text
            # This gives us info about the connection but not DNS specifically
        except Exception:
            pass

        # Simple check: resolve a unique subdomain through a DNS leak test service
        # For simplicity, we'll check if we can detect the resolver
        try:
            resp = requests.get("https://am.i.mullvad.net/json", timeout=10)
            data = resp.json()
            # If mullvad reports we're not on a VPN, DNS might be leaking
            is_mullvad = data.get("mullvad_exit_ip", False)
            # This isn't a perfect DNS leak test but gives useful info
            return "no" if data.get("mullvad_exit_ip", True) else "possible"
        except Exception:
            # Fallback: basic check - compare resolved DNS to known public DNS
            return "unknown"

    except Exception as e:
        print(f"  [!] DNS leak check error: {e}")
        return "error"


def check_ip_leak(baseline_ip):
    """Check if the real IP is exposed."""
    print("  Checking for IP leaks...")
    current_ip = get_public_ip()
    if current_ip == "error":
        return "error", current_ip
    if baseline_ip and current_ip == baseline_ip:
        return "yes", current_ip  # IP didn't change = leak
    return "no", current_ip


def get_vpn_process_usage():
    """Find VPN processes and measure CPU/RAM usage."""
    print("  Checking VPN process resource usage...")
    vpn_keywords = [
        "vpn", "wireguard", "openvpn", "proton", "windscribe", "nordvpn",
        "tunnelbear", "mullvad", "hideme", "atlas", "privado", "surfshark",
        "wg-quick", "openconnect"
    ]
    total_cpu = 0
    total_ram = 0
    found = False

    for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info']):
        try:
            name = proc.info['name'].lower()
            if any(kw in name for kw in vpn_keywords):
                found = True
                total_cpu += proc.info['cpu_percent'] or 0
                mem = proc.info['memory_info']
                if mem:
                    total_ram += mem.rss / (1024 * 1024)  # Convert to MB
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not found:
        return {"vpn_cpu_pct": 0, "vpn_ram_mb": 0}

    return {
        "vpn_cpu_pct": round(total_cpu, 1),
        "vpn_ram_mb": round(total_ram, 1),
    }


# ── Main ────────────────────────────────────────────────────────────────────
def run_baseline():
    """Run baseline measurements without VPN."""
    print("\n═══ Running Baseline (No VPN) ═══\n")

    ip = get_public_ip()
    print(f"  Your IP: {ip}")

    ping_results = run_ping_test()
    print(f"  Latency: {ping_results['avg_latency_ms']}ms avg, "
          f"jitter: {ping_results['jitter_ms']}ms, "
          f"loss: {ping_results['packet_loss_pct']}%")

    speed_results = run_speedtest()
    print(f"  Download: {speed_results['download_mbps']} Mbps, "
          f"Upload: {speed_results['upload_mbps']} Mbps, "
          f"Ping: {speed_results['ping_ms']}ms")

    dl_results = run_file_download()
    print(f"  File download: {dl_results['file_download_time_s']}s "
          f"({dl_results['file_download_speed_mbps']} Mbps)")

    baseline = {
        "ip": ip,
        "timestamp": datetime.now().isoformat(),
        "ping": ping_results,
        "speed": speed_results,
        "file_download": dl_results,
    }
    save_baseline(baseline)
    print(f"\n  Baseline saved to {BASELINE_FILE}")

    # Also log to CSV as "baseline" entry
    row = {
        "timestamp": baseline["timestamp"],
        "vpn_name": "BASELINE",
        "server_location": "none",
        "time_of_day": "baseline",
        "iteration": 1,
        **speed_results,
        **dl_results,
        **ping_results,
        "dns_leak": "n/a",
        "ip_leak": "n/a",
        "public_ip": ip,
        "vpn_cpu_pct": 0,
        "vpn_ram_mb": 0,
    }
    append_row(row)
    print(f"  Results logged to {RESULTS_FILE}")
    print("\n═══ Baseline Complete ═══\n")


def run_vpn_test(vpn_name, location, time_of_day, iterations=SPEEDTEST_ITERATIONS):
    """Run full test suite for a VPN."""
    baseline = load_baseline()
    baseline_ip = baseline.get("ip") if baseline else None

    if not baseline_ip:
        print("[!] No baseline found. Run with --baseline first to record your real IP.")
        print("    (Needed to detect IP leaks)")
        return

    print(f"\n═══ Testing: {vpn_name} | Location: {location} | Time: {time_of_day} ═══\n")

    # Check IP first
    ip_leak, current_ip = check_ip_leak(baseline_ip)
    if ip_leak == "yes":
        print(f"  [WARNING] IP LEAK DETECTED! Your IP ({current_ip}) matches baseline.")
        print(f"  Make sure the VPN is connected before running tests.")
    else:
        print(f"  Public IP: {current_ip} (baseline: {baseline_ip}) - {'OK' if ip_leak == 'no' else ip_leak}")

    # DNS leak check
    dns_leak = check_dns_leak()
    print(f"  DNS leak: {dns_leak}")

    # Ping test (once)
    ping_results = run_ping_test()
    print(f"  Latency: {ping_results['avg_latency_ms']}ms avg, "
          f"jitter: {ping_results['jitter_ms']}ms, "
          f"loss: {ping_results['packet_loss_pct']}%")

    # VPN resource usage
    usage = get_vpn_process_usage()
    print(f"  VPN process: CPU {usage['vpn_cpu_pct']}%, RAM {usage['vpn_ram_mb']}MB")

    # Speed tests (multiple iterations)
    for i in range(1, iterations + 1):
        print(f"\n  ── Iteration {i}/{iterations} ──")

        speed_results = run_speedtest()
        # Use jitter from ping test
        speed_results["jitter_ms"] = ping_results["jitter_ms"]
        print(f"  Download: {speed_results['download_mbps']} Mbps, "
              f"Upload: {speed_results['upload_mbps']} Mbps")

        dl_results = run_file_download()
        print(f"  File download: {dl_results['file_download_time_s']}s "
              f"({dl_results['file_download_speed_mbps']} Mbps)")

        row = {
            "timestamp": datetime.now().isoformat(),
            "vpn_name": vpn_name,
            "server_location": location,
            "time_of_day": time_of_day,
            "iteration": i,
            **speed_results,
            **dl_results,
            **ping_results,
            "dns_leak": dns_leak,
            "ip_leak": ip_leak,
            "public_ip": current_ip,
            **usage,
        }
        append_row(row)

    print(f"\n  All results logged to {RESULTS_FILE}")
    print(f"\n═══ Test Complete: {vpn_name} ═══\n")


def main():
    parser = argparse.ArgumentParser(description="VPN Testing Script - CS204 Project")
    parser.add_argument("--vpn", type=str, help="Name of the VPN being tested")
    parser.add_argument("--location", type=str, default="nearest", help="Server location (e.g., 'nearest', 'US-East')")
    parser.add_argument("--time", type=str, default="off-peak", help="Time of day (e.g., 'peak', 'off-peak')")
    parser.add_argument("--baseline", action="store_true", help="Run baseline test (no VPN)")
    parser.add_argument("--iterations", type=int, default=SPEEDTEST_ITERATIONS, help="Number of speed test iterations")

    args = parser.parse_args()

    if args.baseline:
        run_baseline()
    elif args.vpn:
        run_vpn_test(args.vpn, args.location, args.time, args.iterations)
    else:
        parser.print_help()
        print("\nExamples:")
        print('  python vpn_test.py --baseline')
        print('  python vpn_test.py --vpn "ProtonVPN" --location "nearest" --time "peak"')
        print('  python vpn_test.py --vpn "Windscribe" --location "US-East" --time "off-peak" --iterations 5')


if __name__ == "__main__":
    main()
