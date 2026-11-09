# 🚀 Remote Job Intelligence & Automated Data Pipeline

An end-to-end automated data engineering pipeline and interactive web application that aggregates, cleans, and analyzes remote data science and analytics job postings from multiple global APIs.

## 📊 Live App
Explore the live dashboard here: [Streamlit Cloud App URL] *(Replace with your link)*

---

## 🛠️ Tech Stack & Architecture
* **Backend & Pipeline:** Python (`pandas`, `requests`, `python-dotenv`)
* **APIs Integrated:** Adzuna, Remotive, Jobicy, Arbeitnow
* **Automation & CI/CD:** GitHub Actions (scheduled daily automated scraping and data commits)
* **Frontend Dashboard:** Streamlit Community Cloud
* **Version Control:** Git & GitHub

---

## 🔄 How It Works
1. **Automated Extraction:** A GitHub Action workflow triggers daily at 08:00 UTC, executing `job_fetcher.py`.
2. **Transformation & Skill Extraction:** The script fetches raw JSON/REST data, standardizes schemas, and uses RegEx pattern matching to extract in-demand technical skills (Python, SQL, PyTorch, Power BI, AWS, etc.).
3. **Persistence:** The cleaned data is saved locally and committed back to the repository as `cleaned_remote_jobs.csv`.
4. **Interactive Visualization:** Streamlit instantly detects the updated dataset and renders filtered job metrics, skill breakdowns, and direct application links.

---

## 📂 Project Structure
```text
remote-job-intelligence/
│
├── .github/workflows/
│   └── update_jobs.yml       # Daily automated pipeline workflow
├── app.py                    # Streamlit interactive dashboard
├── job_fetcher.py            # Multi-source API scraper & data processor
├── cleaned_remote_jobs.csv   # Automatically updated job dataset
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation