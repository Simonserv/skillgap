import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path

from skillgap.services.jobs.job_aggregator_service import JobAggregatorService
from skillgap.services.jobs.job_skill_extraction_service import JobSkillExtractionService

OUTPUT_DIR = Path("data/jobs")
OUTPUT_FILE = OUTPUT_DIR / "jobs.json"


def main():
    parser = argparse.ArgumentParser(description="Fetch and enrich market job data.")
    parser.add_argument("--keyword", type=str, default="software", help="Search keyword for jobs (default: software)")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of jobs to fetch and enrich (default: all)")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay in seconds between AI enrichment calls (default: 1.5)")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    aggregator = JobAggregatorService()

    print(f"Fetching jobs for keyword: '{args.keyword}'...")
    jobs = aggregator.fetch_jobs(args.keyword)

    print(f"Fetched {len(jobs)} total jobs (deduplicated)")

    if args.limit is not None:
        jobs = jobs[:args.limit]
        print(f"Limiting to first {args.limit} jobs for enrichment.")

    enriched = []
    total = len(jobs)

    for i, job in enumerate(jobs, start=1):
        print(f"[{i}/{total}] Enriched: '{job.title}' at '{job.company}'")

        try:
            job = JobSkillExtractionService.enrich(job)
            enriched.append(asdict(job))
        except Exception as e:
            print(f"  Failed to enrich job: {e}")

        # Introduce a delay to prevent Groq API rate limit issues
        if i < total and args.delay > 0:
            time.sleep(args.delay)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=4, ensure_ascii=False)

    print()
    print("=" * 60)
    print(f"Saved {len(enriched)} enriched jobs to dataset.")
    print(f"Dataset path: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()