# =======================================================================
# Step 1: import requirements
# =======================================================================
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import os
from termcolor import colored
import pyfiglet
import json

# =======================================================================
# Step 2: set variable
# =======================================================================
CONFIG_FILE = "job_config.json"

DEFAULT_KEYWORDS = [
    "remote", "visa-sponsorship", "internship", "entry-level",
    "actuarial science", "actuary", "underwriting",
    "data science", "data scientist", "data analysis", "data analyst",
    "Quantitative developer", "software developer", "junior software developer",
    "react", "js"
]

DEFAULT_MAX_AGE_DAYS = 7
BASE_URLS = {
    "linkedin": "https://www.linkedin.com/jobs/search?keywords={keyword}&location=Worldwide&f_TPR=r604800",
    "glassdoor": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keyword}",
    "indeed": "https://www.indeed.com/jobs?q={keyword}&sort=date"
}
OUTPUT_FILE = "jobs.txt"

# =======================================================================
# Config handling
# =======================================================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        keywords = data.get("KEYWORDS", DEFAULT_KEYWORDS)
        max_age_days = data.get("MAX_AGE_DAYS", DEFAULT_MAX_AGE_DAYS)
    else:
        keywords = DEFAULT_KEYWORDS
        max_age_days = DEFAULT_MAX_AGE_DAYS
    return {"KEYWORDS": keywords, "MAX_AGE_DAYS": max_age_days}

def save_config(keywords, max_age_days):
    data = {
        "KEYWORDS": keywords,
        "MAX_AGE_DAYS": max_age_days
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# =======================================================================
# Step 3: fetch jobs from APIS
# =======================================================================
def show_banner():
    text = "JOB BOT by JOY NJOROGE"
    ascii_banner = pyfiglet.figlet_format(text)
    colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']
    for i, line in enumerate(ascii_banner.split("\n")):
        print(colored(line, colors[i % len(colors)]))

def fetch_jobs(keywords, max_age_days):
    all_jobs = []
    for site, url_template in BASE_URLS.items():
        for keyword in keywords:
            url = url_template.format(keyword=keyword.replace(" ", "+"))
            print(f"Scraping {site} for keyword: {keyword}")
            try:
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if response.status_code == 200:
                    jobs = parse_jobs(response.text, site, keyword)
                    # Filtering jobs by date is not implemented in parse_jobs.
                    all_jobs.extend(jobs)
            except Exception as e:
                print(f"Error scraping {site}: {e}")
    # Filtering by max_age_days could be implemented if each job had a 'date' field.
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
# Step 6: Menu Functions
# =======================================================================
def view_keywords(keywords):
    print("\nCurrent keywords:")
    for i, kw in enumerate(keywords, 1):
        print(f"{i}. {kw}")

def edit_keywords(keywords):
    while True:
        view_keywords(keywords)
        print("\nOptions: [a]dd, [d]elete, [e]dit, [b]ack")
        choice = input("Choose: ").strip().lower()
        if choice == "a":
            new_kw = input("Enter new keyword: ").strip()
            if new_kw and new_kw not in keywords:
                keywords.append(new_kw)
                print("Added!\n")
        elif choice == "d":
            idx = input("Enter keyword number to delete: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(keywords):
                del keywords[int(idx)-1]
                print("Deleted!\n")
        elif choice == "e":
            idx = input("Enter keyword number to edit: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(keywords):
                new_val = input("Enter new value: ").strip()
                if new_val:
                    keywords[int(idx)-1] = new_val
                    print("Edited!\n")
        elif choice == "b":
            break
        else:
            print("Invalid option.")
    return keywords

def view_filters(max_age_days):
    print(f"\nCurrent filter - Max age days: {max_age_days}")

def edit_filters(max_age_days):
    view_filters(max_age_days)
    new_val = input("Enter new max age days: ").strip()
    if new_val.isdigit() and int(new_val) > 0:
        max_age_days = int(new_val)
        print("Updated!\n")
    else:
        print("Value not changed or invalid.")
    return max_age_days

def view_last_jobs():
    if os.path.exists(OUTPUT_FILE):
        print(f"\n--- Last Scraped Jobs ({OUTPUT_FILE}) ---")
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f.readlines()[:20]:
                print(line.strip())
        print("--- End of Preview ---\n")
    else:
        print("No jobs file found. Run the bot first.\n")

def reset_to_default():
    save_config(DEFAULT_KEYWORDS, DEFAULT_MAX_AGE_DAYS)
    print("Settings reset to default.\n")

# =======================================================================
# Step 7: Main Menu
# =======================================================================
def menu():
    show_banner()
    config = load_config()
    keywords = config["KEYWORDS"]
    max_age_days = config["MAX_AGE_DAYS"]

    while True:
        print("\n====== JOB BOT MENU ======")
        print("1. View keywords")
        print("2. Edit keywords")
        print("3. View filters (max age days)")
        print("4. Edit filters (max age days)")
        print("5. Run the bot (scrape jobs)")
        print("6. View last scraped jobs")
        print("7. Reset all settings to default")
        print("8. Save and exit")
        print("9. Exit without saving")
        choice = input("Select option: ").strip()

        if choice == "1":
            view_keywords(keywords)
        elif choice == "2":
            keywords = edit_keywords(keywords)
        elif choice == "3":
            view_filters(max_age_days)
        elif choice == "4":
            max_age_days = edit_filters(max_age_days)
        elif choice == "5":
            jobs = fetch_jobs(keywords, max_age_days)
            if jobs:
                save_jobs(jobs)
                print(f"\nJoy I have saved {len(jobs)} jobs to {OUTPUT_FILE}")
            else:
                print("No jobs found.")
        elif choice == "6":
            view_last_jobs()
        elif choice == "7":
            reset_to_default()
            config = load_config()
            keywords = config["KEYWORDS"]
            max_age_days = config["MAX_AGE_DAYS"]
        elif choice == "8":
            save_config(keywords, max_age_days)
            print("Settings saved. Goodbye!")
            break
        elif choice == "9":
            print("Exiting without saving.")
            break
        else:
            print("Invalid option. Try again.")

# =======================================================================
# Step 8: Start app
# =======================================================================
if __name__ == "__main__":
    menu()

# =========================================================================
# Now lets scrape my jobs, wish me luck in my applications!!!
