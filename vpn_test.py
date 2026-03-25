#!/usr/bin/env python3
"""
VPN Performance Test - CS204 Project
Runs 3 tests to compare connection speed with and without a VPN:
  1. Download speed (Ookla speedtest)
  2. Upload speed (Ookla speedtest)
  3. yt-dlp video download (real-world throughput)

Usage:
    python vpn_test.py                  # run all 3 tests
    python vpn_test.py --label "No VPN" # tag the run with a label
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime


# YouTube video for real-world download test
YT_VIDEO_URL = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
YT_OUTPUT_DIR = "yt_test_tmp"


def run_speedtest():
    """Run speedtest-cli and return download/upload in Mbps."""
    print("\n── Speed Test (speedtest-cli) ──")
    try:
        result = subprocess.run(
            ["speedtest-cli", "--json"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            print(f"  [!] speedtest failed: {result.stderr.strip()}")
            return None, None

        data = json.loads(result.stdout)
        # speedtest-cli returns bits per second
        download = round(data["download"] / 1_000_000, 2)
        upload = round(data["upload"] / 1_000_000, 2)
        ping = round(data["ping"], 1)

        print(f"  Download: {download} Mbps")
        print(f"  Upload:   {upload} Mbps")
        print(f"  Ping:     {ping} ms")
        return download, upload

    except FileNotFoundError:
        print("  [!] 'speedtest-cli' not found.")
        print("      Install: pip install speedtest-cli")
        return None, None
    except Exception as e:
        print(f"  [!] Speed test error: {e}")
        return None, None


def run_ytdlp_download():
    """Download a YouTube video with yt-dlp and measure throughput."""
    print("\n── yt-dlp Video Download ──")
    print(f"  Video: {YT_VIDEO_URL}")

    os.makedirs(YT_OUTPUT_DIR, exist_ok=True)
    output_template = os.path.join(YT_OUTPUT_DIR, "%(title)s.%(ext)s")

    try:
        start = time.time()
        result = subprocess.run(
            [
                "yt-dlp",
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "-o", output_template,
                "--no-playlist",
                "--newline",
                "--cookies-from-browser", "chrome",
                YT_VIDEO_URL,
            ],
            capture_output=True, text=True, timeout=300,
        )
        elapsed = time.time() - start

        if result.returncode != 0:
            print(f"  [!] yt-dlp failed (exit code {result.returncode}):")
            if result.stderr:
                print(f"  STDERR: {result.stderr.strip()}")
            if result.stdout:
                # Print last few lines of stdout for context
                last_lines = result.stdout.strip().splitlines()[-10:]
                print(f"  STDOUT (last lines):")
                for line in last_lines:
                    print(f"    {line}")
            return None, None

        # Calculate total file size downloaded
        total_bytes = 0
        for root, _, files in os.walk(YT_OUTPUT_DIR):
            for f in files:
                total_bytes += os.path.getsize(os.path.join(root, f))

        size_mb = round(total_bytes / (1024 * 1024), 2)
        speed_mbps = round((total_bytes * 8) / (elapsed * 1_000_000), 2)

        print(f"  Downloaded: {size_mb} MB in {round(elapsed, 1)}s")
        print(f"  Throughput: {speed_mbps} Mbps")
        return size_mb, speed_mbps

    except FileNotFoundError:
        print("  [!] 'yt-dlp' not found.")
        print("      Install: pip install yt-dlp")
        return None, None
    except Exception as e:
        print(f"  [!] yt-dlp error: {e}")
        return None, None
    finally:
        # Clean up downloaded files
        import shutil
        shutil.rmtree(YT_OUTPUT_DIR, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="VPN Performance Test - CS204")
    parser.add_argument("--label", type=str, default="", help="Label for this run (e.g. 'No VPN', 'ProtonVPN')")
    args = parser.parse_args()

    label = args.label or "Test Run"
    print(f"\n{'═' * 50}")
    print(f"  VPN Performance Test — {label}")
    print(f"{'═' * 50}")

    # 1 & 2: Speed test (download + upload)
    download_mbps, upload_mbps = run_speedtest()

    # 3: yt-dlp real-world download
    yt_size_mb, yt_speed_mbps = run_ytdlp_download()

    # Summary
    print(f"\n{'═' * 50}")
    print(f"  Results — {label}")
    print(f"{'═' * 50}")
    print(f"  1. Download Speed:    {download_mbps or 'N/A'} Mbps")
    print(f"  2. Upload Speed:      {upload_mbps or 'N/A'} Mbps")
    print(f"  3. yt-dlp Download:   {yt_speed_mbps or 'N/A'} Mbps ({yt_size_mb or '?'} MB)")
    print()

    # Append results to a single JSON file
    result = {
        "label": label,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "download_mbps": download_mbps,
        "upload_mbps": upload_mbps,
        "ytdlp_speed_mbps": yt_speed_mbps,
        "ytdlp_size_mb": yt_size_mb,
    }

    results_file = "results.json"
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            all_results = json.load(f)
    else:
        all_results = []

    all_results.append(result)

    with open(results_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"  Appended to {results_file} ({len(all_results)} total runs)")
    print()


if __name__ == "__main__":
    main()
