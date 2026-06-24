#!/usr/bin/env python3
"""
Collect Hacker News stories/comments into data/raw/<query>_<kind>.csv.
Usage:
  python scripts/collect_hn.py --kind comments --limit 1000 --query ai
No API key is required.
"""
import argparse
import csv
import os
from datetime import datetime

import requests


API_URL = "https://hn.algolia.com/api/v1/search_by_date"


def build_text(hit, kind):
    if kind == "comments":
        return (hit.get("comment_text") or "").replace("\n", " ").strip()
    title = (hit.get("title") or "").strip()
    story_text = (hit.get("story_text") or "").replace("\n", " ").strip()
    return " ".join(part for part in [title, story_text] if part)


def fetch_page(kind, query, page, hits_per_page):
    tag = "comment" if kind == "comments" else "story"
    params = {
        "tags": tag,
        "query": query,
        "page": page,
        "hitsPerPage": hits_per_page,
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["comments", "stories"], default="comments")
    parser.add_argument("--query", default="")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--page-size", type=int, default=100)
    args = parser.parse_args()

    outdir = os.path.join("data", "raw")
    os.makedirs(outdir, exist_ok=True)

    safe_query = args.query.strip().replace(" ", "_") or "all"
    outpath = os.path.join(outdir, f"hn_{safe_query}_{args.kind}.csv")

    collected = 0
    seen_ids = set()

    with open(outpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "text", "score", "created_utc", "author", "url", "kind"],
        )
        writer.writeheader()

        total_pages = None
        page = 0
        while collected < args.limit:
            payload = fetch_page(args.kind, args.query, page, min(args.page_size, args.limit - collected))
            if total_pages is None:
                total_pages = payload.get("nbPages", 0)

            hits = payload.get("hits", [])
            if not hits:
                break

            for hit in hits:
                object_id = hit.get("objectID")
                text = build_text(hit, args.kind)
                if not object_id or not text or object_id in seen_ids:
                    continue

                created_at = hit.get("created_at")
                created_utc = ""
                if created_at:
                    try:
                        created_utc = datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp()
                    except ValueError:
                        created_utc = created_at

                writer.writerow(
                    {
                        "id": object_id,
                        "text": text,
                        "score": hit.get("points", ""),
                        "created_utc": created_utc,
                        "author": hit.get("author", ""),
                        "url": hit.get("url", hit.get("story_url", "")),
                        "kind": args.kind,
                    }
                )
                seen_ids.add(object_id)
                collected += 1
                if collected >= args.limit:
                    break

            page += 1
            if total_pages is not None and page >= total_pages:
                break

    print("Saved", outpath, f"({collected} rows)")


if __name__ == "__main__":
    main()