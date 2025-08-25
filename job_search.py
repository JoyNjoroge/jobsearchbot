# =======================================================================
# Step 1: import requirements
# =======================================================================
# 1. requests for sending http requests to APIs(post, get, put, delete),
import requests
# 2. bs4 for extracting data, web scraping
from bs4 import BeautifulSoup
# 3. datetime for parsing recent posts
from datetime import datetime, timedelta
import time
import os

# =======================================================================
# Step 2: set variable
# =======================================================================
KEYWORDS = [
    "remote", "visa-sponsorship", "internship", "entry-level",
    "actuarial science", "actuary", "underwriting",
    "data science", "data scientist", "data analysis", "data analyst",
    "Quantitative developer", "software developer", "junior software developer",
    "react", "js"
    ]

MAX_AGE_DAYS = 7 # MAKE IT BRING JOBS NOT OLDER THAN 7 DAYS OR 1 WEEK
BASE_URLS = {
    "linkedin": "https://www.linkedin.com/jobs/search?keywords={keyword}&location=Worldwide&f_TPR=r604800",
    "glassdoor": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keyword}",
    "indeed": "https://www.indeed.com/jobs?q={keyword}&sort=date"
    }
OUTPUT_FILE = "jobs.txt"


# =======================================================================
# Step 3: fetch jobs from APIS
# =======================================================================
# Lemme beautify it first
# =======================
from termcolor import colored
import pyfiglet

text = "JOB BOT by JOY NJOROGE"
ascii_banner = pyfiglet.figlet_format(text)

colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']
for i, line in enumerate(ascii_banner.split("\n")):
    print(colored(line, colors[i % len(colors)]))
# =========================================================================
def fetch_jobs():
    all_jobs = []
    for site, url_template in BASE_URLS.items():
        for keyword in KEYWORDS:
            url = url_template.format(keyword=keyword.replace(" ", "+"))
            print(f"Scraping {site} for keyword: {keyword}")
            try:
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if response.status_code == 200:
                    jobs = parse_jobs(response.text, site, keyword)
                    all_jobs.extend(jobs)
            except Exception as e:
                print(f"Error scraping {site}: {e}")
    return all_jobs
# =======================================================================
# Step 4: Interprete data and convert using parse method
# =======================================================================
def parse_jobs(html, site, keyword):
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    if site == "linkedin":
        for card in soup.select(".base-card"):
            title = card.select_one(".base-search-card__title")
            company = card.select_one(".base-search-card__subtitle")
            link = card.select_one("a.base-card__full-link")
            if title and company and link:
                jobs.append({
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True),
                    "url": link["href"],
                    "site": site
                })

    elif site == "glassdoor":
        for card in soup.select(".react-job-listing"):
            title = card.select_one(".jobLink")
            company = card.select_one(".jobEmpolyerName") or card.select_one(".jobEmployerName")
            if title and company:
                jobs.append({
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True),
                    "url": "https://glassdoor.com" + title["href"],
                    "site": site
                })

    elif site == "indeed":
        for card in soup.select("a.tapItem"):
            title = card.select_one("h2 span")
            company = card.select_one(".companyName")
            if title and company:
                jobs.append({
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True),
                    "url": "https://indeed.com" + card["href"],
                    "site": site
                })
    return jobs
# =======================================================================
# Step 5: Save jobs as a file
# =======================================================================
def save_jobs(jobs):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for job in jobs:
            f.write(f"{job['title']} | {job['company']} | {job['url']} | {job['site']}\n")
# =======================================================================
# Step 7: Finish and publish app
# =======================================================================
if __name__ == "__main__":
    jobs = fetch_jobs()
    if jobs:
        save_jobs(jobs)
        print(f"Joy I have saved {len(jobs)} jobs to {OUTPUT_FILE}")

# =========================================================================
# Now lets scrape my jobs, wish me luck in my applications!!!
