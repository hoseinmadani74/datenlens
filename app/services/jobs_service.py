import time
import re
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List
import httpx
from langdetect import detect
from jobspy import scrape_jobs
from app.config import JOBS_CACHE_TTL_SECONDS

jobs_cache: Dict[str, Dict[str, Any]] = {}

GERMAN_FLUENCY_REGEX = re.compile(
    r'\b(c1|c2|verhandlungssicher\w*|flie[ßs]end\w*)\b',
    re.IGNORECASE,
)


def is_english_friendly(text: str) -> bool:
  """Filter out listings with strict German fluency requirements (C1, C2, verhandlungssicher, fließend)."""
  if not text:
    return True
  if GERMAN_FLUENCY_REGEX.search(text):
    return False
  try:
    lang = detect(text[:400])
    if lang == "en":
      return True
  except Exception:
    pass
  return True


async def fetch_jobs_aggregated(
    query: str = "Data Analyst", hours: int = 24
) -> List[Dict[str, Any]]:
  """Fetch and filter English-friendly tech jobs in Germany from Arbeitnow and JobSpy."""
  now = time.time()
  cutoff = now - (hours * 3600)
  jobs: List[Dict[str, Any]] = []

  # 1. Arbeitnow Job Board API
  try:
    async with httpx.AsyncClient(timeout=8.0) as client:
      resp = await client.get("https://www.arbeitnow.com/api/job-board-api")
      if resp.status_code == 200:
        items = resp.json().get("data", [])
        terms = [t.lower() for t in query.split() if t.strip()]
        for item in items:
          created_at = item.get("created_at")
          if created_at and created_at < cutoff:
            continue

          title = item.get("title", "")
          desc = item.get("description", "")
          company = item.get("company_name", "")
          loc = item.get("location", "")
          # Filter out non-German regions
          if loc and re.search(
              r'\b(london|uk|united kingdom|wales|scotland|ireland|dublin|paris|france|spain|madrid|barcelona|usa|united states|canada|india)\b',
              loc,
              re.IGNORECASE,
          ):
            continue

          tags = " ".join(item.get("tags", []))
          full_text = f"{title} {company} {loc} {tags} {desc}"

          if not is_english_friendly(full_text):
            continue

          title_lower = title.lower()
          full_lower = full_text.lower()
          if terms:
            q_full = query.lower()
            if not (
                q_full in full_lower
                or all(t in full_lower for t in terms)
                or any(t in title_lower for t in terms)
            ):
              continue

          posted_str = "Recently"
          if created_at:
            dt = datetime.fromtimestamp(created_at, tz=timezone.utc)
            posted_str = dt.strftime("%Y-%m-%d %H:%M UTC")

          jobs.append({
              "title": title,
              "company": company,
              "location": loc or "Germany (Remote / Hybrid)",
              "job_url": item.get("url", ""),
              "posted_at": posted_str,
              "source": "Arbeitnow",
          })
  except Exception as e:
    print(f"Arbeitnow fetch error: {e}")

  # 2. JobSpy Aggregator (Indeed Germany) run asynchronously in thread pool
  def run_jobspy():
    try:
      df = scrape_jobs(
          site_name=["indeed"],
          search_term=query,
          location="Germany",
          results_wanted=15,
          hours_old=hours,
          country_indeed="germany",
      )
      return df
    except Exception as e:
      print(f"JobSpy scrape error: {e}")
      return None

  try:
    df = await asyncio.to_thread(run_jobspy)
    if df is not None and not df.empty:
      for _, row in df.iterrows():
        title = str(row.get("title") or "").strip()
        desc = str(row.get("description") or "")
        company = str(row.get("company") or "").strip()
        loc = str(row.get("location") or "").strip()
        job_url = str(
            row.get("job_url_direct") or row.get("job_url") or ""
        ).strip()
        date_posted = str(row.get("date_posted") or "Recently")

        if not title or not job_url:
          continue

        full_text = f"{title} {company} {loc} {desc}"
        if not is_english_friendly(full_text):
          continue

        if any(
            j["title"].lower() == title.lower()
            and j["company"].lower() == company.lower()
            for j in jobs
        ):
          continue

        jobs.append({
            "title": title,
            "company": company,
            "location": loc or "Germany",
            "job_url": job_url,
            "posted_at": date_posted,
            "source": "Indeed",
        })
  except Exception as e:
    print(f"JobSpy aggregator error: {e}")

  return jobs


async def get_jobs_cached(query: str = "Data Analyst", hours: int = 24) -> Dict[str, Any]:
  """Get aggregated jobs with in-memory TTL caching."""
  if hours not in [12, 24, 72]:
    hours = 24

  query_clean = query.strip()
  cache_key = f"{query_clean.lower()}_{hours}"
  now = time.time()

  if cache_key in jobs_cache:
    entry = jobs_cache[cache_key]
    if now - entry["timestamp"] < JOBS_CACHE_TTL_SECONDS:
      return {
          **entry["data"],
          "cached": True,
          "cache_age_seconds": int(now - entry["timestamp"]),
      }

  jobs = await fetch_jobs_aggregated(query=query_clean, hours=hours)
  result = {
      "success": True,
      "count": len(jobs),
      "jobs": jobs,
  }
  jobs_cache[cache_key] = {"timestamp": now, "data": result}
  return result
