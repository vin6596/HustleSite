"""
SIGNAL scraper v2.

Jobs / Internships  -> strictly Nigeria, strictly electrical/electronics
                       engineering, oil & gas, industrial automation,
                       instrumentation.
Hackathons          -> general + Nigeria-based + Web3/bounties/grants.
Scholarships        -> fully-funded, abroad (new section).

Sources are a mix of RSS feeds (free, no key, no scraping-ToS grey area)
and a small curated list where no feed/API exists. RSS feed URLs below are
best-effort guesses at each site's standard WordPress feed path — this
sandbox can't reach these domains to verify them, so the first real test is
you running the workflow. If a source comes back empty, tell me and I'll
swap in a working feed URL.
"""
import json
from datetime import datetime, timezone

import feedparser
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (SignalRadar/1.0; personal opportunity tracker)"}

ENG_KEYWORDS = [
    "electrical", "electrical/electronic", "electronics", "instrumentation",
    "automation", "scada", "plc", "power system", "power systems",
    "power plant", "oil and gas", "oil & gas", "upstream", "downstream",
    "petroleum", "control system", "controls engineer", "process engineer",
    "renewable energy", "solar", "grid", "substation", "transmission",
    "mechatronics", "commissioning engineer", "hse engineer",
    "maintenance engineer", "energy engineer", "field engineer",
    "graduate trainee", "graduate engineer", "industrial engineer",
    "hvac", "utility engineer", "reliability engineer", "instrument engineer",
]

INTERN_HINTS = [
    "intern", "internship", "industrial training", "siwes", "nysc",
    "graduate trainee", "trainee", "youth corper",
]

WEB3_HINTS = ["web3", "blockchain", "crypto", "defi", "nft", "dao", "smart contract"]


def matches_eng(*parts):
    text = " ".join(p for p in parts if p).lower()
    return any(k in text for k in ENG_KEYWORDS)


def is_internship(*parts):
    text = " ".join(p for p in parts if p).lower()
    return any(k in text for k in INTERN_HINTS)


def is_web3(*parts):
    text = " ".join(p for p in parts if p).lower()
    return any(k in text for k in WEB3_HINTS)


# ---------------------------------------------------------------------------
# JOBS / INTERNSHIPS — Nigeria-only, engineering-only
# ---------------------------------------------------------------------------

NG_JOB_FEEDS = [
    ("MyJobMag", "https://www.myjobmag.com/rss/engineering-jobs-in-nigeria"),
    ("Hot Nigerian Jobs", "https://www.hotnigerianjobs.com/hotjobs/feed"),
    ("NGCareers", "https://ngcareers.com/feed"),
    ("Jobzilla NG", "https://jobzillang.com/feed"),
]


def fetch_ng_jobs_and_internships():
    jobs, interns = [], []
    for source, url in NG_JOB_FEEDS:
        try:
            feed = feedparser.parse(url, request_headers=HEADERS)
            if getattr(feed, "bozo", 0) and not feed.entries:
                print(f"{source}: feed unreachable or invalid — {url}")
                continue
            for entry in feed.entries[:80]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                if not matches_eng(title, summary):
                    continue
                item = {
                    "title": title,
                    "org": source,
                    "location": "Nigeria",
                    "type": "",
                    "url": entry.get("link"),
                    "tag": "Internship" if is_internship(title, summary) else "Job",
                    "source": source,
                }
                (interns if item["tag"] == "Internship" else jobs).append(item)
        except Exception as e:
            print(f"{source} failed:", e)
    return jobs, interns


def jobberman_search_link():
    """No public feed/API for Jobberman — one pre-filled search link as a fallback."""
    q = "electrical+engineer+OR+automation+OR+instrumentation+OR+oil+and+gas"
    return [{
        "title": "Search: Electrical / Automation / Oil & Gas roles in Nigeria",
        "org": "Jobberman Nigeria",
        "location": "Nigeria",
        "type": "Search link (not a live listing)",
        "url": f"https://www.jobberman.com/jobs?q={q}",
        "tag": "Job",
        "source": "Jobberman",
    }]


# ---------------------------------------------------------------------------
# HACKATHONS — general + Nigeria + Web3/bounties/grants
# ---------------------------------------------------------------------------

def fetch_devpost():
    out = []
    try:
        r = requests.get(
            "https://devpost.com/api/hackathons",
            params={"status[]": "open"}, headers=HEADERS, timeout=20,
        )
        r.raise_for_status()
        for h in r.json().get("hackathons", [])[:40]:
            loc = h.get("displayed_location", {}) or {}
            themes = h.get("themes") or []
            theme_names = " ".join(t.get("name", "") for t in themes)
            title = h.get("title", "")
            tag = "Bounty/Web3" if is_web3(title, theme_names) else "Hackathon"
            out.append({
                "title": title,
                "org": "Devpost",
                "location": loc.get("location", "Online"),
                "type": theme_names,
                "url": h.get("url"),
                "tag": tag,
                "source": "Devpost",
            })
    except Exception as e:
        print("Devpost failed:", e)
    return out


def curated_hackathons_extra():
    """
    Nigeria-based orgs, Web3 hackathon platforms, and bounty/grant platforms
    don't have free public APIs — direct links so nothing is missed while
    Phase 3 (real scraping of these) is still pending.
    """
    return [
        {"title": "Browse Nigeria & Africa hackathons", "org": "Techpoint Build",
         "location": "Nigeria", "type": "Live listing", "tag": "Hackathon",
         "url": "https://techpoint.africa/build/", "source": "Techpoint Build"},
        {"title": "Web3Bridge cohorts & hackathons", "org": "Web3Bridge",
         "location": "Nigeria", "type": "Web3", "tag": "Bounty/Web3",
         "url": "https://web3bridge.com/", "source": "Web3Bridge"},
        {"title": "Browse hackathons, bounties & grants", "org": "DoraHacks",
         "location": "Global", "type": "Web3", "tag": "Bounty/Web3",
         "url": "https://dorahacks.io/hackathon", "source": "DoraHacks"},
        {"title": "Browse open bounties", "org": "Gitcoin",
         "location": "Global", "type": "Web3", "tag": "Bounty/Web3",
         "url": "https://gitcoin.co/bounties", "source": "Gitcoin"},
        {"title": "Browse active quests & campaigns", "org": "Galxe",
         "location": "Global", "type": "Web3", "tag": "Bounty/Web3",
         "url": "https://www.galxe.com/discover", "source": "Galxe"},
        {"title": "Browse active quests", "org": "Layer3",
         "location": "Global", "type": "Web3", "tag": "Bounty/Web3",
         "url": "https://layer3.xyz/quests", "source": "Layer3"},
        {"title": "Browse hackathons (Africa-friendly)", "org": "Unstop",
         "location": "Global + Africa", "type": "Live listing", "tag": "Hackathon",
         "url": "https://unstop.com/hackathons", "source": "Unstop"},
    ]


# ---------------------------------------------------------------------------
# SCHOLARSHIPS — fully funded, abroad
# ---------------------------------------------------------------------------

SCHOLARSHIP_FEEDS = [
    ("Opportunity Desk", "https://opportunitydesk.org/feed/"),
    ("Opportunities For Africans", "https://www.opportunitiesforafricans.com/feed/"),
    ("Scholarship Region", "https://scholarship-positions.com/feed"),
]


def fetch_scholarships():
    out = []
    for source, url in SCHOLARSHIP_FEEDS:
        try:
            feed = feedparser.parse(url, request_headers=HEADERS)
            if getattr(feed, "bozo", 0) and not feed.entries:
                print(f"{source}: feed unreachable or invalid — {url}")
                continue
            for entry in feed.entries[:40]:
                title = entry.get("title", "")
                t = title.lower()
                if "scholarship" not in t and "fully funded" not in t and "fellowship" not in t:
                    continue
                out.append({
                    "title": title,
                    "org": source,
                    "location": "Abroad",
                    "type": "Fully-funded" if "fully funded" in t else "Scholarship",
                    "url": entry.get("link"),
                    "tag": "Scholarship",
                    "source": source,
                })
        except Exception as e:
            print(f"{source} failed:", e)
    return out


def curated_scholarship_links():
    """Backbone list of major fully-funded programs, always shown regardless of feed health."""
    return [
        {"title": "Chevening Scholarships (UK, fully funded)", "org": "Chevening",
         "location": "UK", "type": "Fully-funded", "tag": "Scholarship",
         "url": "https://www.chevening.org/scholarships/", "source": "Chevening"},
        {"title": "DAAD Scholarships (Germany, engineering-friendly)", "org": "DAAD",
         "location": "Germany", "type": "Fully-funded", "tag": "Scholarship",
         "url": "https://www.daad.de/en/study-and-research-in-germany/scholarships/", "source": "DAAD"},
        {"title": "Commonwealth Scholarships (UK)", "org": "Commonwealth Scholarship Commission",
         "location": "UK", "type": "Fully-funded", "tag": "Scholarship",
         "url": "https://cscuk.fcdo.gov.uk/scholarships/", "source": "Commonwealth"},
        {"title": "Mastercard Foundation Scholars Program", "org": "Mastercard Foundation",
         "location": "Multiple", "type": "Fully-funded", "tag": "Scholarship",
         "url": "https://mastercardfdn.org/all/scholars/", "source": "Mastercard Foundation"},
        {"title": "Fulbright Foreign Student Program (USA)", "org": "Fulbright",
         "location": "USA", "type": "Fully-funded", "tag": "Scholarship",
         "url": "https://foreign.fulbrightonline.org/", "source": "Fulbright"},
    ]


# ---------------------------------------------------------------------------

def main():
    jobs, interns = fetch_ng_jobs_and_internships()
    jobs += jobberman_search_link()

    hackathons = fetch_devpost() + curated_hackathons_extra()
    scholarships = fetch_scholarships() + curated_scholarship_links()

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hackathons": hackathons,
        "internships": interns,
        "jobs": jobs,
        "scholarships": scholarships,
    }

    with open("docs/data.json", "w") as f:
        json.dump(data, f, indent=2)

    print(
        f"hackathons={len(hackathons)} internships={len(interns)} "
        f"jobs={len(jobs)} scholarships={len(scholarships)} @ {data['generated_at']}"
    )


if __name__ == "__main__":
    main()
