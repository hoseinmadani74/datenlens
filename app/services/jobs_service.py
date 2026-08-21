import time
import re
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import httpx
from langdetect import detect
from jobspy import scrape_jobs
from app.config import JOBS_CACHE_TTL_SECONDS

jobs_cache: Dict[str, Dict[str, Any]] = {}

# ==============================================================================
# 1. ULTRA-STRICT GERMAN LANGUAGE REQUIREMENT REGEXES
# ==============================================================================
NO_GERMAN_PATTERNS = re.compile(
    r'\b('
    r'no\s+german\s+(is\s+)?(required|needed)|'
    r'german\s+(is\s+)?(not\s+required|optional|not\s+mandatory)|'
    r'without\s+german|'
    r'keine\s+deutschkenntnisse\s+erforderlich|'
    r'100%\s+english\s+working\s+environment|'
    r'working\s+language\s+is\s+english'
    r')\b',
    re.IGNORECASE,
)

STRICT_GERMAN_REQ_REGEX = re.compile(
    r'('
    # English phrases indicating German is required or expected
    r'\b(fluent|good|proficient|powerful|strong|excellent|native|business|solid|advanced|working|intermediate)\s+(in\s+)?german\b|'
    r'\bgerman\s+(is\s+)?(required|a\s+must|mandatory|necessary|essential|needed|preferred|advantageous|beneficial)\b|'
    r'\b(speak|speaking|command\s+of|knowledge\s+of|skills?\s+in|level\s+in)\s+german\b|'
    r'\bgerman\s+(c1|c2|b2\+?|fluen\w+|language\s+skills?|proficiency)\b|'
    r'\bgerman\s+and\s+english\s+fluency\b|'
    r'\bfluency\s+in\s+both\s+german\b|'
    r'\bmust\s+speak\s+german\b|'
    r'\brequire\s+german\b|'
    # German phrases indicating German requirement
    r'\b(c1|c2|verhandlungssicher\w*|flie[ßs]end\w*|muttersprachler\w*|muttersprache\w*)\b|'
    r'\b(sehr\s+gute\s+deutsch\w*|gute\s+deutsch\w*|deutschkenntnisse\s+(in\s+wort\s+und\s+schrift|erforderlich|zwingend|mindestens|vorausgesetzt|notwendig))\b|'
    r'\b(deutsch\s+auf\s+(c1|c2|b2)|deutsch\s+(min\w*|mind\w*)\.?\s*(b2|c1|c2))\b|'
    r'\b(hervorragende\s+deutsch\w*|flie[ßs]ende\s+deutsch\w*)\b|'
    r'\bvoraussetzung:\s*deutsch\b'
    r')',
    re.IGNORECASE,
)


def is_strictly_english_friendly(text: str) -> bool:
  """Enforces 100% English-friendly environment by rejecting any explicit German requirements."""
  if not text:
    return True

  # If text explicitly states German is NOT required, remove that clause and inspect remainder
  if NO_GERMAN_PATTERNS.search(text):
    cleaned = NO_GERMAN_PATTERNS.sub('', text)
    if STRICT_GERMAN_REQ_REGEX.search(cleaned):
      return False
  elif STRICT_GERMAN_REQ_REGEX.search(text):
    return False

  try:
    lang = detect(text[:400])
    if lang == "de":
      # If language is detected as pure German, ensure no hidden requirements
      if re.search(r'\b(deutschkenntnisse|deutsch)\b', text, re.IGNORECASE):
        return False
  except Exception:
    pass

  return True


# ==============================================================================
# 2. STRICT JUNIOR / ENTRY-LEVEL (<= 3 YEARS) EXPERIENCE REGEXES
# ==============================================================================
SENIOR_LEAD_TITLES_REGEX = re.compile(
    r'\b('
    r'senior|sr\.?|lead|principal|head\s+of|director|vp|vice\s+president|'
    r'staff\s+(engineer|developer|analyst)|chief|architect|executive|manager\b'
    r')',
    re.IGNORECASE,
)

SENIOR_YEARS_EXP_REGEX = re.compile(
    r'('
    r'\b(several|many|numerous|extensive|solid|long-standing)\s+years\s+(of\s+)?experience\b|'
    r'\b([3-9]|\d{2,})\+?\s*(-|\s*to\s*)\s*\d+\s+years\s+(of\s+)?experience\b|'
    r'\b([4-9]|\d{2,})\+?\s*years\s+(of\s+)?experience\b|'
    r'\b3\+\s*years\s+(of\s+)?experience\b|'
    r'\b(min\w*|mind\w*|at\s+least)\s*([3-9]|\d{2,})\s*years\b|'
    r'\b(langjährige|mehrjährige)\s+(berufs)?erfahrung\b|'
    r'\b(mindestens|mind\.)\s*([3-9]|\d{2,})\s*jahre\b'
    r')',
    re.IGNORECASE,
)


def is_junior_or_entry_level(title: str, description: str) -> bool:
  """Filter for junior, graduate, entry-level, or <= 3 years experience only."""
  full_text = f"{title} {description}"

  # 1. Reject senior/lead/head-of in titles
  if SENIOR_LEAD_TITLES_REGEX.search(title):
    return False

  # 2. Reject multi-year / senior experience phrases in text
  if SENIOR_YEARS_EXP_REGEX.search(full_text):
    return False

  return True


# ==============================================================================
# 3. STRICT GERMANY GEOGRAPHIC & WORKPLACE FILTER
# ==============================================================================
GERMAN_GEO_CITIES = [
    "germany", "deutschland", "berlin", "munich", "münchen", "frankfurt", "hamburg",
    "nuremberg", "nürnberg", "erlangen", "cologne", "köln", "stuttgart", "düsseldorf",
    "leipzig", "dresden", "karlsruhe", "bonn", "dortmund", "essen", "mannheim",
    "hanover", "hannover", "bremen", "augsburg", "wiesbaden", "mainz", "freiburg",
    "münster", "aachen", "braunschweig", "kiel", "chemnitz", "magdeburg", "rostock",
    "heidelberg", "regensburg", "ingolstadt", "ulm", "darmstadt", "würzburg", "bayern",
    "bavaria", "hessen", "baden-württemberg", "nordrhein-westfalen", "nrw", "sachsen",
]

NON_GERMAN_GEO_REGEX = re.compile(
    r'\b('
    r'uk|united\s+kingdom|london|scotland|edinburgh|glasgow|wales|cardiff|'
    r'ireland|dublin|paris|france|spain|madrid|barcelona|italy|milan|rome|'
    r'usa|united\s+states|new\s+york|california|san\s+francisco|austin|texas|'
    r'canada|toronto|vancouver|india|bangalore|delhi|mumbai|poland|warsaw|krakow|'
    r'netherlands|amsterdam|rotterdam|sweden|stockholm|switzerland|zurich|geneva|'
    r'austria|vienna'
    r')\b',
    re.IGNORECASE,
)


def is_strictly_germany_location(location: str) -> bool:
  """Ensures job is strictly located within Germany and discards foreign regions."""
  if not location:
    return True
  loc_clean = location.lower()

  # Check if non-German country is mentioned without German city
  if NON_GERMAN_GEO_REGEX.search(loc_clean):
    if not any(
        city in loc_clean
        for city in [
            "germany", "deutschland", "berlin", "munich", "münchen",
            "frankfurt", "hamburg", "nuremberg", "erlangen",
        ]
    ):
      return False

  return any(c in loc_clean for c in GERMAN_GEO_CITIES) or "germany" in loc_clean


# ==============================================================================
# 4. GER 40 / DAX 40 & TECH BLUE CHIPS CLASSIFIER
# ==============================================================================
DAX40_COMPANIES = {
    "sap": "SAP SE",
    "siemens": "Siemens AG",
    "siemens healthineers": "Siemens Healthineers",
    "siemens energy": "Siemens Energy",
    "bmw": "BMW Group",
    "bmw group": "BMW Group",
    "mercedes-benz": "Mercedes-Benz Group",
    "mercedes": "Mercedes-Benz Group",
    "daimler": "Mercedes-Benz / Daimler Truck",
    "porsche": "Porsche AG",
    "bosch": "Robert Bosch GmbH",
    "deutsche telekom": "Deutsche Telekom",
    "telekom": "Deutsche Telekom",
    "allianz": "Allianz SE",
    "basf": "BASF SE",
    "bayer": "Bayer AG",
    "infineon": "Infineon Technologies",
    "continental": "Continental AG",
    "airbus": "Airbus Group",
    "deutsche bank": "Deutsche Bank",
    "munich re": "Munich Re",
    "münchener rück": "Munich Re",
    "henkel": "Henkel",
    "beiersdorf": "Beiersdorf AG",
    "merck": "Merck KGaA",
    "carl zeiss": "Carl Zeiss AG",
    "zeiss": "Carl Zeiss AG",
    "delivery hero": "Delivery Hero",
    "zalando": "Zalando SE",
    "rwe": "RWE AG",
    "e.on": "E.ON SE",
    "vonovia": "Vonovia SE",
    "brenntag": "Brenntag SE",
    "heidelberg materials": "Heidelberg Materials",
    "fresenius": "Fresenius SE",
    "symrise": "Symrise AG",
    "sartorius": "Sartorius AG",
    "mtu aero engines": "MTU Aero Engines",
    "qiagen": "Qiagen N.V.",
    "commerzbank": "Commerzbank AG",
    "hannover rück": "Hannover Re",
    "rheinmetall": "Rheinmetall AG",
    "volkswagen": "Volkswagen AG",
    "audi": "Audi AG (VW Group)",
}

TECH_SCALEUPS = {
    "celonis": "Celonis",
    "personio": "Personio",
    "n26": "N26",
    "trade republic": "Trade Republic",
    "deepl": "DeepL",
    "flix": "Flix",
    "flixbus": "Flix",
    "lilium": "Lilium",
    "helsing": "Helsing AI",
    "wefox": "Wefox",
    "forto": "Forto",
    "tier": "Tier Mobility",
}


def classify_company(company_name: str) -> Dict[str, Any]:
  """Classify company as DAX40 Blue Chip, Scale-Up, or Standard."""
  comp_lower = company_name.lower().strip()

  for key, official_name in DAX40_COMPANIES.items():
    if key in comp_lower:
      return {
          "is_dax40": True,
          "category": "DAX 40 Blue Chip",
          "badge": "⭐ DAX 40 Enterprise",
          "official_name": official_name,
      }

  for key, official_name in TECH_SCALEUPS.items():
    if key in comp_lower:
      return {
          "is_dax40": False,
          "is_scaleup": True,
          "category": "German Tech Scale-Up",
          "badge": "🚀 Tech Scale-Up",
          "official_name": official_name,
      }

  return {
      "is_dax40": False,
      "is_scaleup": False,
      "category": "Standard Tech",
      "badge": None,
      "official_name": company_name,
  }


# ==============================================================================
# 5. 3 DISTINCT CAREER TRACK DEFINITIONS
# ==============================================================================
TRACK_DEFINITIONS = {
    "track1": {
        "id": "track1",
        "title": "Data Analyst & Data Scientist (incl. Computational Bio)",
        "description": "Data Analytics, Machine Learning, BI, and Computational Biomedical / Bioinformatics positions without strict biology lab or MD degree requirements.",
        "search_queries": [
            "Data Analyst Junior",
            "Junior Data Scientist",
            "Biomedical Data Analyst",
            "Bioinformatics Data Scientist",
            "BI Analyst",
        ],
        "default_query": "Junior Data Analyst",
        "bio_medical_filter": True,
    },
    "track2": {
        "id": "track2",
        "title": "Data Engineering",
        "description": "ETL pipelines, PySpark, Big Data, SQL, Databricks, and cloud data platform engineering.",
        "search_queries": [
            "Junior Data Engineer",
            "Data Engineer",
            "Big Data Engineer",
            "ETL Developer",
            "PySpark Data Engineer",
        ],
        "default_query": "Junior Data Engineer",
        "bio_medical_filter": False,
    },
    "track3": {
        "id": "track3",
        "title": "Data Warehouse, Cloud Data, Systems & DevOps / MLOps",
        "description": "DWH architecture, Snowflake, BigQuery, Database Infrastructure, Cloud Data Ops, and MLOps / Systems Engineering.",
        "search_queries": [
            "Data Warehouse Engineer",
            "DWH Developer",
            "Database Engineer",
            "DevOps Engineer Data",
            "MLOps Engineer",
            "Cloud Data Engineer",
        ],
        "default_query": "Data Warehouse Engineer",
        "bio_medical_filter": False,
    },
}

# Biology degree / Wet lab hurdle regex for Track 1
BIO_BARRIER_REGEX = re.compile(
    r'\b('
    r'wet\s+lab\s+experience|'
    r'phd\s+in\s+molecular\s+biology|'
    r'medical\s+doctor|approbation|facharzt|'
    r'degree\s+in\s+medicine\s+required|'
    r'laboratory\s+pipetting|cell\s+culture\s+hands-on'
    r')\b',
    re.IGNORECASE,
)


# ==============================================================================
# 6. DIRECT SEARCH DEEP-LINKS GENERATOR (ALL MAJOR JOB BOARDS & DAX 40 PORTALS)
# ==============================================================================
def generate_direct_jobboard_links(query: str) -> List[Dict[str, str]]:
  """Generates direct pre-filtered deep search links for all requested job boards."""
  q_enc = query.replace(" ", "+")
  q_step = query.lower().replace(" ", "-")

  return [
      {
          "name": "LinkedIn Germany",
          "badge": "Entry Level (0-3y)",
          "icon": "linkedin",
          "url": f"https://www.linkedin.com/jobs/search/?keywords={q_enc}&location=Germany&f_E=2%2C1&f_TPR=r604800",
          "description": "Search on LinkedIn with Junior / Associate filter applied",
      },
      {
          "name": "Indeed Germany",
          "badge": "Entry Level (DE)",
          "icon": "indeed",
          "url": f"https://de.indeed.com/jobs?q={q_enc}&l=Deutschland&explvl=entry_level",
          "description": "Search on Indeed Germany with Entry-Level experience filter",
      },
      {
          "name": "StepStone Germany",
          "badge": "Graduate / Junior",
          "icon": "stepstone",
          "url": f"https://www.stepstone.de/jobs/{q_step}/in-deutschland?experienceLevel=GRADUATE%2CENTRY_LEVEL",
          "description": "Direct search on StepStone for Graduate and Junior tech roles",
      },
      {
          "name": "XING Germany",
          "badge": "German Network",
          "icon": "xing",
          "url": f"https://www.xing.com/jobs/search?keywords={q_enc}&location=Deutschland",
          "description": "Search on XING across German tech & enterprise listings",
      },
      {
          "name": "Bundesagentur für Arbeit",
          "badge": "Official Federal Portal",
          "icon": "arbeitsagentur",
          "url": f"https://www.arbeitsagentur.de/jobsuche/suche?angebotsart=1&was={q_enc}&wo=Deutschland",
          "description": "Official German Federal Employment Agency Jobsuche",
      },
      {
          "name": "Arbeitnow",
          "badge": "English-Friendly (DE)",
          "icon": "arbeitnow",
          "url": f"https://www.arbeitnow.com/jobs?query={q_enc}",
          "description": "Curated English-speaking German startup & tech opportunities",
      },
  ]


def generate_dax40_career_links(query: str) -> List[Dict[str, str]]:
  """Generates direct search links to official DAX 40 corporate career sites."""
  q_enc = query.replace(" ", "+")

  return [
      {
          "company": "SAP SE",
          "badge": "DAX 40",
          "url": f"https://jobs.sap.com/search/?q={q_enc}&locationsearch=Germany",
          "focus": "Enterprise ERP & Cloud Data",
      },
      {
          "company": "Siemens AG",
          "badge": "DAX 40",
          "url": f"https://jobs.siemens.com/careers?query={q_enc}&location=Germany",
          "focus": "Industrial IoT, AI & Automation",
      },
      {
          "company": "BMW Group",
          "badge": "DAX 40",
          "url": f"https://www.bmwgroup.jobs/de/en/jobfinder.html#location=DE&keyword={q_enc}",
          "focus": "Automotive Data & Connected Drive",
      },
      {
          "company": "Robert Bosch GmbH",
          "badge": "Enterprise Blue Chip",
          "url": f"https://www.bosch.de/karriere/job-angebote/?search={q_enc}",
          "focus": "IoT, Sensor Analytics & Mobility",
      },
      {
          "company": "Mercedes-Benz Group",
          "badge": "DAX 40",
          "url": f"https://group.mercedes-benz.com/karriere/jobsuche/?keywords={q_enc}",
          "focus": "Vehicle Software & AI Intelligence",
      },
      {
          "company": "Porsche AG",
          "badge": "DAX 40",
          "url": f"https://jobs.porsche.com/index.php?ac=search_result&search_criterion_keyword%5B%5D={q_enc}",
          "focus": "High-Performance Automotive Engineering",
      },
      {
          "company": "Allianz SE",
          "badge": "DAX 40",
          "url": f"https://careers.allianz.com/en_EN/jobs.html?keyword={q_enc}&country=Germany",
          "focus": "Fintech, Insurance Analytics & Risk Models",
      },
      {
          "company": "Deutsche Telekom",
          "badge": "DAX 40",
          "url": f"https://www.telekom.com/en/careers/job-search?keyword={q_enc}",
          "focus": "Telecom Infrastructure, Cloud & Data Science",
      },
      {
          "company": "Infineon Technologies",
          "badge": "DAX 40",
          "url": f"https://www.infineon.com/cms/en/careers/jobsearch/jobsearch/?term={q_enc}",
          "focus": "Semiconductor Data & Smart Sensors",
      },
      {
          "company": "Zalando SE",
          "badge": "DAX 40",
          "url": f"https://jobs.zalando.com/en/jobs/?query={q_enc}&locations=Germany",
          "focus": "E-Commerce, Recommendation ML & DWH",
      },
  ]


# ==============================================================================
# 7. MULTI-SOURCE INGESTION & AGGREGATOR ENGINE
# ==============================================================================
async def fetch_jobs_aggregated(
    query: str = "Data Analyst",
    hours: int = 72,
    track: Optional[str] = "track1",
    workplace_preference: str = "all",  # "all" | "onsite_hybrid" | "remote_germany"
    dax40_only: bool = False,
) -> List[Dict[str, Any]]:
  """Fetch and filter English-friendly tech jobs in Germany from multiple sources."""
  now = time.time()
  cutoff = now - (hours * 3600)
  jobs: List[Dict[str, Any]] = []

  # Clean query
  query_clean = query.strip()
  if not query_clean:
    query_clean = "Data Analyst"

  is_track1 = track == "track1"

  # 1. Ingest from Arbeitnow API
  try:
    async with httpx.AsyncClient(timeout=8.0) as client:
      resp = await client.get("https://www.arbeitnow.com/api/job-board-api")
      if resp.status_code == 200:
        items = resp.json().get("data", [])
        terms = [t.lower() for t in query_clean.split() if t.strip()]
        for item in items:
          created_at = item.get("created_at")
          if created_at and created_at < cutoff:
            continue

          title = item.get("title", "")
          desc = item.get("description", "")
          company = item.get("company_name", "")
          loc = item.get("location", "")
          is_remote = bool(item.get("remote", False))

          full_text = f"{title} {company} {loc} {desc}"

          # Workplace preference filtering
          if workplace_preference == "onsite_hybrid" and is_remote:
            # If user prefers On-site/Hybrid in Germany, skip pure remote
            continue
          if workplace_preference == "remote_germany" and not is_remote:
            continue

          # Strict Geographic filter (Germany only)
          if not is_strictly_germany_location(loc):
            continue

          # Ultra-strict German filter
          if not is_strictly_english_friendly(full_text):
            continue

          # Strict Junior / <= 3 years filter
          if not is_junior_or_entry_level(title, desc):
            continue

          # Track 1 bio barrier check
          if is_track1 and BIO_BARRIER_REGEX.search(full_text):
            continue

          # Company Classification
          comp_info = classify_company(company)
          if dax40_only and not comp_info["is_dax40"]:
            continue

          # Keyword relevance matching
          title_lower = title.lower()
          full_lower = full_text.lower()
          q_lower = query_clean.lower()
          if not (
              q_lower in full_lower
              or all(t in full_lower for t in terms)
              or any(t in title_lower for t in terms)
          ):
            continue

          posted_str = "Recently"
          if created_at:
            dt = datetime.fromtimestamp(created_at, tz=timezone.utc)
            posted_str = dt.strftime("%Y-%m-%d %H:%M UTC")

          work_type_label = (
              "Remote (Germany)"
              if is_remote
              else "On-site / Hybrid (Germany)"
          )

          jobs.append({
              "title": title,
              "company": company,
              "location": loc or "Germany",
              "workplace_type": work_type_label,
              "job_url": item.get("url", ""),
              "posted_at": posted_str,
              "source": "Arbeitnow",
              "is_dax40": comp_info["is_dax40"],
              "badge": comp_info["badge"],
              "experience_tier": "Junior (0-3 Years)",
          })
  except Exception as e:
    print(f"Arbeitnow fetch error: {e}")

  # 2. Ingest from JobSpy (Indeed Germany + LinkedIn Germany) in parallel thread
  def run_jobspy():
    try:
      df = scrape_jobs(
          site_name=["indeed", "linkedin"],
          search_term=query_clean,
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
        site_source = str(row.get("site") or "Indeed").title()
        is_remote_job = bool(row.get("is_remote", False))

        if not title or not job_url:
          continue

        full_text = f"{title} {company} {loc} {desc}"

        # Workplace preference filtering
        if workplace_preference == "onsite_hybrid" and is_remote_job:
          continue
        if workplace_preference == "remote_germany" and not is_remote_job:
          continue

        # Strict Germany location check
        if not is_strictly_germany_location(loc):
          continue

        # Ultra-strict German filter
        if not is_strictly_english_friendly(full_text):
          continue

        # Strict Junior / <= 3 years filter
        if not is_junior_or_entry_level(title, desc):
          continue

        # Track 1 bio barrier check
        if is_track1 and BIO_BARRIER_REGEX.search(full_text):
          continue

        # Company classification
        comp_info = classify_company(company)
        if dax40_only and not comp_info["is_dax40"]:
          continue

        # Deduplicate
        if any(
            j["title"].lower() == title.lower()
            and j["company"].lower() == company.lower()
            for j in jobs
        ):
          continue

        work_type_label = (
            "Remote (Germany)"
            if is_remote_job
            else "On-site / Hybrid (Germany)"
        )

        jobs.append({
            "title": title,
            "company": company,
            "location": loc or "Germany",
            "workplace_type": work_type_label,
            "job_url": job_url,
            "posted_at": date_posted,
            "source": site_source,
            "is_dax40": comp_info["is_dax40"],
            "badge": comp_info["badge"],
            "experience_tier": "Junior (0-3 Years)",
        })
  except Exception as e:
    print(f"JobSpy aggregator error: {e}")

  return jobs


async def get_jobs_cached(
    query: str = "Junior Data Analyst",
    hours: int = 72,
    track: Optional[str] = "track1",
    workplace_preference: str = "all",
    dax40_only: bool = False,
) -> Dict[str, Any]:
  """Get aggregated jobs with in-memory TTL caching and deep links."""
  if hours not in [12, 24, 72, 168]:
    hours = 72

  query_clean = query.strip()
  cache_key = f"{query_clean.lower()}_{hours}_{track}_{workplace_preference}_{dax40_only}"
  now = time.time()

  # Deep links for all requested job boards
  direct_jobboards = generate_direct_jobboard_links(query_clean)
  dax40_portals = generate_dax40_career_links(query_clean)

  if cache_key in jobs_cache:
    entry = jobs_cache[cache_key]
    if now - entry["timestamp"] < JOBS_CACHE_TTL_SECONDS:
      return {
          **entry["data"],
          "cached": True,
          "cache_age_seconds": int(now - entry["timestamp"]),
          "direct_jobboard_links": direct_jobboards,
          "dax40_portals": dax40_portals,
          "track_info": TRACK_DEFINITIONS.get(
              track or "track1", TRACK_DEFINITIONS["track1"]
          ),
      }

  jobs = await fetch_jobs_aggregated(
      query=query_clean,
      hours=hours,
      track=track,
      workplace_preference=workplace_preference,
      dax40_only=dax40_only,
  )

  result = {
      "success": True,
      "count": len(jobs),
      "jobs": jobs,
      "direct_jobboard_links": direct_jobboards,
      "dax40_portals": dax40_portals,
      "track_info": TRACK_DEFINITIONS.get(
          track or "track1", TRACK_DEFINITIONS["track1"]
      ),
      "filters_applied": {
          "max_experience": "Junior / Entry Level (<= 3 Years)",
          "language": "Strictly English-Friendly (No German fluency barriers)",
          "country": "Germany Only (Excluding UK, Scotland, France, USA, etc.)",
          "workplace_preference": workplace_preference,
          "dax40_only": dax40_only,
      },
  }

  jobs_cache[cache_key] = {"timestamp": now, "data": result}
  return result
