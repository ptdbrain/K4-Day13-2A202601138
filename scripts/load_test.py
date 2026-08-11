import argparse
import concurrent.futures
import json
import sys
import time
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.challenge import load_challenge, ordered_queries
from app.cli import configure_utf8_stdio

BASE_URL = "http://127.0.0.1:8000"
QUERIES = Path("data/sample_queries.jsonl")


def send_request(client: httpx.Client, payload: dict) -> None:
    try:
        start = time.perf_counter()
        r = client.post(f"{BASE_URL}/chat", json=payload)
        latency = (time.perf_counter() - start) * 1000
        cid = r.headers.get("x-request-id") or r.json().get("correlation_id", "None")
        print(f"[{r.status_code}] {cid} | {payload['feature']} | {latency:.1f}ms")
    except Exception as e:
        print(f"Error: {e}")



def main() -> None:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=1, help="Number of concurrent requests")
    parser.add_argument(
        "--challenge",
        action="store_true",
        help="Dùng input chính thức trong config/challenge.json sau khi được release.",
    )
    args = parser.parse_args()

    if args.challenge:
        challenge = load_challenge()
        payloads = ordered_queries(challenge)
        print(f"Challenge: {challenge.challenge_id} | Cohort: {challenge.cohort}")
    else:
        payloads = [
            json.loads(line)
            for line in QUERIES.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    
    with httpx.Client(timeout=30.0) as client:
        if args.concurrency > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                futures = [executor.submit(send_request, client, payload) for payload in payloads]
                concurrent.futures.wait(futures)
        else:
            for payload in payloads:
                send_request(client, payload)


if __name__ == "__main__":
    main()
