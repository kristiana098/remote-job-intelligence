import re
import pandas as pd
import requests

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
        # Match whole words to avoid partial matching (e.g. matching "R" inside "Remote")
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            # Normalize variations like PowerBI to Power BI
            clean_skill = "Power BI" if skill.lower() == "powerbi" else skill
            if clean_skill not in found_skills:
                found_skills.append(clean_skill)

    return ", ".join(found_skills)


def fetch_remotive_jobs():
    print(" Fetching & processing Remotive API...")
    url = "https://remotive.com/api/remote-jobs?category=data"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            jobs = res.json().get("jobs", [])
            results = []
            for j in jobs:
                title = j.get("title", "")
                description = j.get("description", "")
                full_text = f"{title} {description}"

                results.append({
                    "Source": "Remotive",
                    "Title": title,
                    "Company": j.get("company_name", "Unknown"),
                    "Location": j.get(
                        "candidate_required_location", "Worldwide"
                    ),
                    "Skills Extracted": extract_skills(full_text),
                    "Published Date": str(j.get("publication_date", ""))[:10],
                    "Apply Link": j.get("url"),
                })
            return results
    except Exception as e:
        print(f"   Remotive error: {e}")
    return []


def fetch_jobicy_jobs():
    print(" Fetching & processing Jobicy API...")
    url = "https://jobicy.com/api/v1/jobs"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            jobs = res.json().get("jobs", [])
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
    except Exception as e:
        print(f"   Jobicy error: {e}")
    return []


def fetch_arbeitnow_jobs():
    print(" Fetching & processing Arbeitnow API (Europe/Remote)...")
    url = "https://www.arbeitnow.com/api/job-board-api"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            jobs = res.json().get("data", [])
            results = []
            for j in jobs:
                title = j.get("title", "")
                description = j.get("description", "")
                full_text = f"{title} {description}"

                loc = (
                    "Remote / Europe" if j.get("remote") else j.get("location")
                )

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
    except Exception as e:
        print(f"   Arbeitnow error: {e}")
    return []


def run_pipeline():
    all_jobs = []
    all_jobs.extend(fetch_remotive_jobs())
    all_jobs.extend(fetch_jobicy_jobs())
    all_jobs.extend(fetch_arbeitnow_jobs())

    if not all_jobs:
        print("No jobs fetched.")
        return

    df = pd.DataFrame(all_jobs)

    # Filter for data, analytics, python, SQL, operations, or BI roles
    pattern = "data|analyst|analytics|python|sql|bi|operations"
    filtered_df = df[
        df["Title"].str.contains(pattern, case=False, na=False)
    ].copy()

    # Drop duplicates
    filtered_df = filtered_df.drop_duplicates(subset=["Title", "Company"])

    # Clean missing skills
    filtered_df["Skills Extracted"] = filtered_df["Skills Extracted"].replace(
        "", "General Analytics / Unspecified"
    )

    # Save output
    filename = "cleaned_remote_jobs.csv"
    filtered_df.to_csv(filename, index=False)

    print("\n" + "=" * 60)
    print(" PIPELINE COMPLETE!")
    print(
        f" Total jobs analyzed: {len(df)} | Matching Data/Ops jobs: {len(filtered_df)}"
    )
    print(f" Saved enhanced dataset to '{filename}'")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
