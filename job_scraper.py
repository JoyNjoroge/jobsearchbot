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
# Human-like Scraper
# =======================================================================
class HumanizedJobScraper:
    def __init__(self):
        self.jobs = []
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]

    def human_delay(self, min_sec=1.5, max_sec=5):
        time.sleep(random.uniform(min_sec, max_sec))

    def get_headers(self):
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Connection": "keep-alive",
        }

    def fetch_jobs(self, keywords, max_age_days):
        all_jobs = []
        for site, url_template in BASE_URLS.items():
            for keyword in keywords:
                url = url_template.format(keyword=keyword.replace(" ", "+"))
                print(f"Scraping {site} for keyword: {keyword}")
                try:
                    headers = self.get_headers()
                    response = requests.get(url, headers=headers, timeout=30)
                    self.human_delay(2, 4)
                    if response.status_code == 200:
                        jobs = parse_jobs(response.text, site, keyword)
                        all_jobs.extend(jobs)
                    else:
                        print(f"Non-200 for {site}: {response.status_code}")
                except Exception as e:
                    print(f"Error scraping {site}: {e}")
                self.human_delay(2, 5)
        self.jobs = all_jobs
        return all_jobs

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
def save_jobs_html(jobs, filename=OUTPUT_FILE, jobs_per_page=JOBS_PER_PAGE, keywords=None):
    total_jobs = len(jobs)
    total_pages = math.ceil(total_jobs / jobs_per_page)

    sources = {}
    companies = set()
    for job in jobs:
        companies.add(job["company"])
        sources[job["source"]] = sources.get(job["source"], 0) + 1

    now_str = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    keywords_str = ", ".join(keywords) if keywords else "Software"

    CSS = """
    <style>
        body { background: linear-gradient(120deg, #2a0845 0%, #6441A5 50%, #FF4E50 100%); color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-height: 100vh; margin: 0; padding: 0;}
        .container { max-width: 1400px; margin: 30px auto; background: rgba(30, 32, 61, 0.96); border-radius: 16px; padding: 32px; box-shadow: 0 10px 30px rgba(100,65,165,0.18);}
        .header { text-align: center; margin-bottom: 30px;}
        .header h1 { font-size: 2.7em; background: linear-gradient(90deg, #FF4E50 20%, #F9D423 50%, #7AF484 80%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
        .stats { display: flex; gap: 32px; justify-content: center; margin: 25px 0; flex-wrap: wrap;}
        .stat { background: linear-gradient(120deg, #7AF484, #6441A5); color: #2a0845; padding: 18px 28px; border-radius: 15px; text-align: center; min-width: 120px; box-shadow: 0 3px 12px rgba(122,244,132,0.12);}
        .stat h3 { font-size: 2em; margin-bottom: 5px;}
        .source-breakdown { background: #2a0845; border-radius: 15px; padding: 20px; margin: 18px 0;}
        .source-breakdown h3 { color: #fff; margin-bottom: 10px; text-align: center; letter-spacing: 1px;}
        .source-tags { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;}
        .source-tag { background: #FF4E50; color: #fff; padding: 8px 15px; border-radius: 20px; font-size: 0.95em; font-weight: 500;}
        .jobs-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(410px, 1fr)); gap: 22px; margin-top: 24px;}
        .job-card { background: #fff; color: #2a0845; border-radius: 18px; padding: 20px 24px 24px 24px; border-left: 6px solid #FF4E50; box-shadow: 0 3px 18px rgba(100,65,165,0.12); transition: all 0.3s; position: relative;}
        .job-card:hover { box-shadow: 0 10px 30px #FF4E50, 0 3px 18px #7AF484; transform: translateY(-7px) scale(1.01);}
        .job-title { font-size: 1.26em; font-weight: bold; margin-bottom: 8px; }
        .job-company { color: #6441A5; font-size: 1.07em; margin-bottom: 10px;}
        .job-source { display: inline-block; background: #6441A5; color: #fff; padding: 6px 15px; border-radius: 25px; font-size: 0.93em; margin-bottom: 15px; font-weight: 500;}
        .job-link { display: inline-block; background: linear-gradient(90deg, #7AF484, #6441A5); color: #fff; text-decoration: none; padding: 11px 22px; border-radius: 30px; font-weight: bold; transition: all 0.3s; font-size: 0.93em; text-transform: uppercase; letter-spacing: 1.1px; margin-top: 8px;}
        .job-link:hover { background: linear-gradient(90deg, #FF4E50, #6441A5); color: #fff; box-shadow: 0 6px 15px #FF4E50;}
        .footer { text-align: center; margin-top: 35px; padding-top: 20px; border-top: 2px solid #6441A5; color: #ddd;}
        .success-message { background: linear-gradient(90deg, #7AF484, #6441A5); color: #2a0845; padding: 16px; border-radius: 12px; text-align: center; margin-bottom: 18px; font-weight: bold; font-size: 1.1em;}
        .pagination { margin: 24px 0; text-align: center;}
        .pagination a, .pagination span { display: inline-block; margin: 0 7px; padding: 8px 15px; background: #2a0845; color: #fff; border-radius: 7px; text-decoration: none; font-size: 1.1em; border: 1.5px solid #6441A5; transition: all 0.2s;}
        .pagination a:hover, .pagination .current { background: #FF4E50; color: #fff; border: 1.5px solid #FF4E50;}
        @media (max-width: 768px) { .jobs-grid { grid-template-columns: 1fr; } .stats { flex-direction: column; align-items: center;} .header h1 { font-size: 2.0em; } }
    </style>
    """

    def get_page_html(page):
        start = (page-1)*jobs_per_page
        end = min(page*jobs_per_page, total_jobs)
        jobs_slice = jobs[start:end]
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{keywords_str} Software Jobs - Page {page}</title>
    {CSS}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{keywords_str} Software Jobs</h1>
            <p>Fresh Opportunities from All Over</p>
            <p>Generated on {now_str}</p>
        </div>
        <div class="success-message">
            ✅ Found {total_jobs} opportunities matching: <b>{keywords_str}</b>
        </div>
        <div class="stats">
            <div class="stat"><h3>{total_jobs}</h3><p>Total Jobs</p></div>
            <div class="stat"><h3>{len(sources)}</h3><p>Job Sources</p></div>
            <div class="stat"><h3>{len(companies)}</h3><p>Companies</p></div>
        </div>
        <div class="source-breakdown">
            <h3>Job Sources Covered</h3>
            <div class="source-tags">
        """
        for source, count in sources.items():
            html += f'<span class="source-tag">{source} ({count})</span>'
        html += """
            </div>
        </div>
        <div class="jobs-grid">
        """
        for job in jobs_slice:
            html += f"""
            <div class="job-card">
                <div class="job-title">{job['title']}</div>
                <div class="job-company">🏢 {job['company']}</div>
                <div class="job-source">{job['source']}</div>
                <a href="{job['url']}" target="_blank" class="job-link">Apply Now →</a>
            </div>
            """
        html += """
        </div>
        <div class="pagination">
        """
        # Pagination links
        for i in range(1, total_pages+1):
            if i == page:
                html += f'<span class="current">{i}</span>'
            else:
                html += f'<a href="jobs_page_{i}.html">{i}</a>'
        html += """
        </div>
        <div class="footer">
            <p>🤖 Generated by the Humanized Job Scraper</p>
            <p><small>Next update: Run again in a few hours for fresh listings!</small></p>
        </div>
    </div>
</body>
</html>
        """
        return html

    # Write N files for each page
    for i in range(1, total_pages+1):
        fname = filename if i == 1 else f"jobs_page_{i}.html"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(get_page_html(i))
    print(f"\nSaved {total_jobs} jobs to {filename} ({total_pages} pages).")

# In your menu's "run the bot" section, pass keywords to the function:
# Example replacement for the relevant menu logic:

elif choice == "5":
    scraper = HumanizedJobScraper()
    jobs = scraper.fetch_jobs(keywords, max_age_days)
    if jobs:
        save_jobs_html(jobs, keywords=keywords)
    else:
        print("No jobs found.")


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
