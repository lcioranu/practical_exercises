"""
Tiny concurrency probe. Fires N requests at the service and reports throughput.

    python loadtest.py http://localhost:8001/ask 20

Watch p95 as you raise N on the naive app, then re-run against your fix.
"""

import sys
import time
import asyncio
import statistics
import httpx


async def one(client, url, i):
    t0 = time.perf_counter()
    r = await client.post(url, json={"text": f"q{i}: what is the refund policy?"})
    r.raise_for_status()
    return time.perf_counter() - t0


async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001/ask"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    async with httpx.AsyncClient(timeout=120) as client:
        await one(client, url, -1)  # warm up
        t0 = time.perf_counter()
        lat = await asyncio.gather(*[one(client, url, i) for i in range(n)])
        wall = time.perf_counter() - t0

    lat_sorted = sorted(lat)
    p50 = statistics.median(lat)
    p95 = lat_sorted[max(0, int(0.95 * n) - 1)]
    print(f"url={url}")
    print(f"concurrency={n}  wall={wall:.2f}s  throughput={n / wall:.1f} req/s")
    print(f"latency  p50={p50:.2f}s  p95={p95:.2f}s  max={max(lat):.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
