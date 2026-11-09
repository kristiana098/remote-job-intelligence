import os
import re
from dotenv import load_dotenv
import pandas as pd
import requests

# 1. Load secret variables from the hidden .env file once
load_dotenv()

app_id = os.getenv("ADZUNA_APP_ID")
app_key = os.getenv("ADZUNA_APP_KEY")

# Define key tech skills we want to extract from job titles & descriptions
TECH_SKILLS = [
    "Python",
    "SQL",
    "Pandas",
    "NumPy",
    "R",
    "Power BI",
    "PowerBI",
    "Tableau",
    "Docker",
    "AWS",
    "Azure",
    "GCP",
    "Spark",
    "Airflow",
    "Git",
    "Excel",
    "Machine Learning",
    "NLP",
    "MLOps",
    "ETL",
    "Scikit-Learn",
    "PyTorch",
    "TensorFlow",
    "FastAPI",
    "Streamlit",
    "Dash",
]


def extract_skills(text):
    """Scans text and returns a comma-separated string of matched tech skills."""
    if not isinstance(text, str):
        return ""

    found_skills = []
    for skill in TECH_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            clean_skill = "Power BI" if skill.lower() == "powerbi" else skill
            if clean_skill not in found_skills:
                found_skills.append(clean_skill)

    return ", ".join(found_skills)


def fetch_adzuna_jobs():
    print("Fetching & processing Adzuna API...")
    if not app_id or not app_key:
        print("⚠️ Adzuna skipped: Missing APP_ID or APP_KEY in your .env file.")
        return []

    url = "https://api.adzuna.com/v1/api/jobs/gb/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": "data science",
        "results_per_page": 20,
        "content-type": "application/json",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get("results", [])
            results = []
            for j in jobs:
                title = j.get("title", "")
                description = j.get("description", "")
                full_text = f"{title} {description}"

                results.append({
                    "Source": "Adzuna",
                    "Title": title,
                    "Company": j.get("company", {}).get("display_name", "Unknown"),
                    "Location": j.get("location", {}).get("display_name", "UK"),
                    "Skills Extracted": extract_skills(full_text),
                    "Published Date": str(j.get("created", ""))[:10],
                    "Apply Link": j.get("redirect_url"),
                })
            return results
        else:
            print(f"⚠️ Adzuna API returned non-200 status: {response.status_code}")
    except requests.exceptions.Timeout:
        print("⚠️ Adzuna error: Request timed out.")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Adzuna network error: {e}")
    except Exception as e:
        print(f"⚠️ Adzuna unexpected error: {e}")
    return []


def fetch_remotive_jobs():
    print("Fetching & processing Remotive API...")
    url = "https://remotive.com/api/remote-jobs?category=data"
    
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            jobs = data.get("jobs", [])
            results = []
            for j in jobs:
                title = j.get("title", "")
                description = j.get("description", "")
                full_text = f"{title} {description}"

                results.append({
                    "Source": "Remotive",
                    "Title": title,
                    "Company": j.get("company_name", "Unknown"),
                    "Location": j.get("candidate_required_location", "Worldwide"),
                    "Skills Extracted": extract_skills(full_text),
                    "Published Date": str(j.get("publication_date", ""))[:10],
                    "Apply Link": j.get("url"),
                })
            return results
        else:
            print(f"⚠️ Remotive API returned non-200 status: {res.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Remotive network error: {e}")
    except Exception as e:
        print(f"⚠️ Remotive unexpected error: {e}")
    return []


def fetch_jobicy_jobs():
    print("Fetching & processing Jobicy API...")
    url = "https://jobicy.com/api/v2/remote-jobs"
    
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200 and "application/json" in res.headers.get("Content-Type", ""):
            data = res.json()
            jobs = data.get("jobs", [])
            results = []
            for j in jobs:
                title = j.get("jobTitle", "")
                description = j.get("jobDescription", "")
                full_text = f"{title} {description}"

                results.append({
                    "Source": "Jobicy",
                    "Title": title,
                    "Company": j.get("companyName", "Unknown"),
                    "Location": j.get("jobGeo", "Remote"),
                    "Skills Extracted": extract_skills(full_text),
                    "Published Date": str(j.get("pubDate", ""))[:10],
                    "Apply Link": j.get("url"),
                })
            return results
        else:
            print(f" Jobicy error: Received non-JSON response or status {res.status_code}")
    except requests.exceptions.RequestException as e:
        print(f" Jobicy network error: {e}")
    except Exception as e:
        print(f" Jobicy unexpected error: {e}")
    return []


def fetch_arbeitnow_jobs():
    print("Fetching & processing Arbeitnow API (Europe/Remote)...")
    url = "https://www.arbeitnow.com/api/job-board-api"
    
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            jobs = data.get("data", [])
            results = []
            for j in jobs:
                title = j.get("title", "")
                description = j.get("description", "")
                full_text = f"{title} {description}"

                loc = "Remote / Europe" if j.get("remote") else j.get("location")

                results.append({
                    "Source": "Arbeitnow",
                    "Title": title,
                    "Company": j.get("company_name", "Unknown"),
                    "Location": loc,
                    "Skills Extracted": extract_skills(full_text),
                    "Published Date": "",
                    "Apply Link": j.get("url"),
                })
            return results
        else:
            print(f" Arbeitnow API returned non-200 status: {res.status_code}")
    except requests.exceptions.RequestException as e:
        print(f" Arbeitnow network error: {e}")
    except Exception as e:
        print(f" Arbeitnow unexpected error: {e}")
    return []


def run_pipeline():
    all_jobs = []
    
    # Each function safely catches its own errors and returns [] if it fails
    all_jobs.extend(fetch_adzuna_jobs())
    all_jobs.extend(fetch_remotive_jobs())
    all_jobs.extend(fetch_jobicy_jobs())
    all_jobs.extend(fetch_arbeitnow_jobs())

    if not all_jobs:
        print(" No jobs fetched from any source.")
        return

    df = pd.DataFrame(all_jobs)

    # Filter for data, analytics, python, SQL, operations, or BI roles
    pattern = (
        "data scientist|machine learning|ml engineer|ai engineer|nlp|"
        "llm|mlops|quantitative|data science|data analyst|bi analyst|"
        "business intelligence|analytics engineer"
    )
    filtered_df = df[
        df["Title"].str.contains(pattern, case=False, na=False)
    ].copy()

    # Ensure Published Date is formatted cleanly (YYYY-MM-DD)
    filtered_df["Published Date"] = pd.to_datetime(
        filtered_df["Published Date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    filtered_df["Published Date"] = filtered_df["Published Date"].fillna(
        "Recent"
    )

    # Drop duplicates
    filtered_df = filtered_df.drop_duplicates(subset=["Title", "Company"])

    # Clean missing skills
    filtered_df["Skills Extracted"] = filtered_df["Skills Extracted"].replace(
        "", "General Analytics / Unspecified"
    )

   # Save output with proper quoting to prevent CSV tokenizing errors
    filename = "cleaned_remote_jobs.csv"
    filtered_df.to_csv(filename, index=False, quoting=1)
    
    print("\n" + "=" * 60)
    print(" PIPELINE COMPLETE!")
    print(
        f"Total jobs analyzed: {len(df)} | Matching Data/Ops jobs: {len(filtered_df)}"
    )
    print(f"Saved enhanced dataset to '{filename}'")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
