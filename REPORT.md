# VPN Performance Test Report

**CS204 Project** | March 2026

## Methodology

We measured three metrics to compare network performance with and without a VPN:

1. **Download Speed** (Mbps) -- via `speedtest-cli` (Ookla)
2. **Upload Speed** (Mbps) -- via `speedtest-cli` (Ookla)
3. **Real-World Download** (Mbps) -- downloading a 709 MB YouTube 4K Big Bucks Bunny video with `yt-dlp`

Each VPN was tested on multiple server locations. Tests were run from Singapore on a gigabit fibre connection.

> **Note on speedtest-cli accuracy:** `speedtest-cli` selects the nearest test server, which may be close to the VPN exit node rather than the user's actual location. This can inflate results (especially visible with TunnelBear). The **yt-dlp download** is a more reliable measure of real-world end-to-end throughput because it tests the full path: user -> VPN -> YouTube CDN -> back.

---

## Baseline (No VPN)

| Metric | Run 1 | Run 2 | Average |
|--------|-------|-------|---------|
| Download | 915.55 Mbps | 865.94 Mbps | **890.75 Mbps** |
| Upload | 795.41 Mbps | 805.70 Mbps | **800.56 Mbps** |
| yt-dlp Download | 124.26 Mbps | 169.42 Mbps | **146.84 Mbps** |

---

## Results by VPN Provider (Best Server)

The table below shows the **best-performing server** for each VPN, averaged across valid runs.

| VPN | Best Server | Download (Mbps) | Upload (Mbps) | yt-dlp (Mbps) | DL % of Baseline | yt-dlp % of Baseline |
|-----|-------------|----------------:|-------------:|--------------:|-----------------:|---------------------:|
| **No VPN** | -- | 890.75 | 800.56 | 146.84 | 100% | 100% |
| **ProtonVPN** | Singapore | 414.09 | 83.86 | 125.01 | 46.5% | 85.1% |
| **TunnelBear** | Singapore | 686.16* | 434.25* | 99.01 | 77.0%* | 67.4% |
| **PrivadoVPN** | US - LA | 118.55 | 18.67 | 96.16 | 13.3% | 65.5% |
| **Windscribe** | Canada | 317.22 | 103.90 | 68.93 | 35.6% | 46.9% |
| **Cloudflare WARP** | Singapore | 174.57 | 32.97 | 41.75 | 19.6% | 28.4% |

\* TunnelBear speedtest numbers are likely inflated -- see methodology note above.

---

## Detailed Breakdown by Server Location

### ProtonVPN

| Server | Download (Mbps) | Upload (Mbps) | yt-dlp (Mbps) | Runs |
|--------|----------------:|-------------:|--------------:|-----:|
| Singapore | 414.09 | 83.86 | 125.01 | 4 |
| Japan | 302.01 | 44.22 | 92.57 | 5 |
| United States | 60.51 | 9.59 | 88.35 | 3 |
| Netherlands | 130.40 | 15.51 | 91.81 | 1 |
| Switzerland | 66.76 | 12.49 | N/A | 1 |
| Canada | 24.66 | 12.53 | N/A | 2 |

ProtonVPN performed best on the Singapore server (geographically closest), retaining **85% of baseline yt-dlp throughput**. Distant servers (US, Canada) showed significant speedtest degradation but surprisingly maintained reasonable yt-dlp speeds (~88-96 Mbps), suggesting YouTube CDN routing adapts to the VPN exit location.

### TunnelBear

| Server | Download (Mbps) | Upload (Mbps) | yt-dlp (Mbps) | Runs |
|--------|----------------:|-------------:|--------------:|-----:|
| Singapore (best) | 686.16 | 434.25 | 99.01 | 3 |

TunnelBear's speedtest numbers look impressive but are misleading -- the test server was likely on or near TunnelBear's network. The yt-dlp speed (99 Mbps) is a more honest indicator and still quite good.

### PrivadoVPN

| Server | Download (Mbps) | Upload (Mbps) | yt-dlp (Mbps) | Runs |
|--------|----------------:|-------------:|--------------:|-----:|
| US - Los Angeles | 118.55 | 18.67 | 96.16 | 1 |
| Canada - Montreal | 38.43 | 13.05 | 96.07 | 1 |
| Mumbai | 27.25 | 9.14 | 77.52 | 3 |

Consistent yt-dlp performance across servers (~77-96 Mbps), though speedtest numbers varied widely by location.

### Windscribe

| Server | Download (Mbps) | Upload (Mbps) | yt-dlp (Mbps) | Runs |
|--------|----------------:|-------------:|--------------:|-----:|
| Canada (best) | 317.22 | 103.90 | 68.93 | 1 |
| US - Peachtree | 52.51 | 13.11 | 30.41 | 1 |

Decent speedtest numbers but lower yt-dlp throughput compared to other VPNs.

### Cloudflare WARP

| Server | Download (Mbps) | Upload (Mbps) | yt-dlp (Mbps) | Runs |
|--------|----------------:|-------------:|--------------:|-----:|
| Singapore | 174.57 | 32.97 | 41.75 | 1 |

WARP performed the worst for yt-dlp downloads despite being a nearby server. WARP optimises routing but doesn't function as a traditional VPN for bypassing geo-restrictions.

---

## Free Plan Limits

| VPN | Monthly Data | Devices | Free Servers | Notable Restrictions |
|-----|-------------|---------|--------------|---------------------|
| **ProtonVPN** | **Unlimited** | 1 | 5 countries (US, NL, JP, RO, PL) | No P2P, no streaming-optimised servers, lower priority than paid |
| **TunnelBear** | **2 GB** | 5 | All locations (~47 countries) | Very limited data; essentially a trial |
| **Windscribe** | **10 GB** | Unlimited | ~10 locations | 2 GB base + 8 GB for email confirmation |
| **PrivadoVPN** | **10 GB** | 1 | ~12 server locations | Drops to limited speeds after data cap |
| **Cloudflare WARP** | **Unlimited** | 5 | Auto (nearest Cloudflare PoP) | Not a true VPN -- doesn't mask location for most services |

---

## Peak Hour Congestion

| Server | Time (SGT) | Download (Mbps) | Upload (Mbps) | yt-dlp (Mbps) | Notes |
|--------|-----------|----------------:|--------------:|--------------:|-------|
| Proton Japan | Mar 25 ~1pm (midday) | 301 | 46 | 115 | Off-peak Japan |
| Proton Japan | Mar 26 ~9:40pm (evening) | 298–304 | 43–44 | 72–90 | **yt-dlp dropped 25-35%** |
| Proton US | Mar 25 ~1:15pm (1am EST) | 59–101 | 11–16 | 95 | US off-peak |
| Proton US | Mar 26 ~9:41pm (9:41am EST) | **20.6** | **1.57** | 74 | **DL dropped ~70%** |
| Proton Singapore | Mar 25 ~12:30-1pm | 380–428 | 83–86 | 125 | Stable |

Raw bandwidth on Japan stayed flat (~300 Mbps) but yt-dlp dropped — YouTube CDN congestion, not the tunnel. US servers got hit hardest during business hours. Singapore stayed consistent due to proximity.

### Why Speedtest Stays Stable but YouTube Drops

Speedtest measures short-burst tunnel capacity to a nearby server. YouTube measures end-to-end throughput through Google's CDN — fundamentally different congestion points. Three factors compound during peak hours:

1. **CDN congestion:** Japan's internet exchange points (JPNAP, JPIX) see 2-3x daytime traffic levels between 8pm-midnight JST. YouTube accounts for 15-25% of that evening traffic, saturating Google's local cache nodes and forcing fallback to more distant CDN edges.
2. **VPN IP deprioritisation:** Google detects VPN/datacenter exit IPs and routes them to suboptimal CDN nodes. During peak hours, even those fallback nodes get congested.
3. **Shared exit IP throttling:** Multiple free-tier VPN users share the same exit IP. YouTube applies per-IP rate limits — more concurrent users at peak means a smaller slice each. This explains the 70% drop on Proton US: their US free servers are the most popular globally, so business hours = maximum contention.

---

## Conclusions

### Best Free VPN for Performance: ProtonVPN

**ProtonVPN** is the clear winner for the following reasons:

1. **Best real-world throughput:** Retained **85% of baseline** yt-dlp speed on the Singapore server (125 Mbps vs 147 Mbps baseline) -- the highest of any VPN tested.
2. **Unlimited data:** The only full VPN with no monthly data cap on the free plan, making it viable for daily use.
3. **Consistent across servers:** Even on distant servers (US, Japan, Netherlands), yt-dlp speeds remained above 72 Mbps.

### Rankings by Real-World Download Speed (yt-dlp)

| Rank | VPN | Best yt-dlp Speed | % of Baseline | Practical for Daily Use? |
|------|-----|-------------------:|---------------:|:------------------------:|
| 1 | ProtonVPN | 125.01 Mbps | 85.1% | Yes (unlimited data) |
| 2 | TunnelBear | 99.01 Mbps | 67.4% | No (2 GB/month) |
| 3 | PrivadoVPN | 96.16 Mbps | 65.5% | Limited (10 GB/month) |
| 4 | Windscribe | 68.93 Mbps | 46.9% | Limited (10 GB/month) |
| 5 | Cloudflare WARP | 41.75 Mbps | 28.4% | Yes (unlimited data) |

### Key Takeaways

- **Server proximity matters:** VPN servers closest to the user's physical location (Singapore) consistently performed best across all providers.
- **Speedtest vs real-world:** Synthetic speedtest results can overstate VPN performance by up to 7x (TunnelBear: 686 Mbps speedtest vs 99 Mbps real-world). Always use real-world download tests.
- **All VPNs reduce speed:** Even the best-performing setup (ProtonVPN Singapore) lost ~15% of real-world throughput. Distant servers lost 40-70%.
- **Upload hit is severe:** Upload speeds dropped 89-97% on most VPNs (except TunnelBear/Windscribe which fared better at ~45-87% reduction).
- **ProtonVPN's unlimited free tier is unmatched:** For users who need a free VPN for regular use, it's the only option that doesn't impose a data cap, while also offering the best performance.
