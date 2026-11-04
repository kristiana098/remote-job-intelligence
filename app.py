from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

# Set page layout
st.set_page_config(
    page_title="Remote Data Job Intelligence Dashboard",
    page_icon="💼",
    layout="wide",
)

st.title("💼 Remote Data Science & Analytics Job Intelligence")
st.markdown(
    "Explore real-time remote Data Science, ML, and Analytics opportunities aggregated across free global APIs."
)


@st.cache_data
def load_data():
    """Loads the cleaned job dataset and parses dates."""
    try:
        df = pd.read_csv("cleaned_remote_jobs.csv")
        # Convert Published Date to datetime for filtering
        df["Parsed Date"] = pd.to_datetime(
            df["Published Date"], errors="coerce"
        )
        return df
    except FileNotFoundError:
        return pd.DataFrame()


df = load_data()

if df.empty:
    st.error(
        "No data file found! Make sure to run `uv run job_fetcher.py` first to generate 'cleaned_remote_jobs.csv'."
    )
else:
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("🔍 Filter Options")

    # Keyword Search
    search_query = st.sidebar.text_input(
        "Search by Title or Company", ""
    ).strip()

    # Time Filter Option
    time_filter = st.sidebar.selectbox(
        "Filter by Date Posted",
        [
            "All Time",
            "Past 24 Hours",
            "Past Week (7 Days)",
            "Past Month (30 Days)",
        ],
    )

    # Source Filter
    sources = ["All"] + sorted(df["Source"].dropna().unique().tolist())
    selected_source = st.sidebar.selectbox("API Source", sources)

    # Tech Skill Filter
    all_skills = set()
    for skills in df["Skills Extracted"].dropna():
        if skills != "General Analytics / Unspecified":
            for s in skills.split(", "):
                all_skills.add(s)

    selected_skills = st.sidebar.multiselect(
        "Filter by Required Tech Skill", sorted(list(all_skills))
    )

    # --- APPLY FILTERS ---
    filtered_df = df.copy()

    # 1. Search Query Filter
    if search_query:
        mask = filtered_df["Title"].str.contains(
            search_query, case=False, na=False
        ) | filtered_df["Company"].str.contains(
            search_query, case=False, na=False
        )
        filtered_df = filtered_df[mask]

    # 2. Time Filter Logic
    now = pd.Timestamp.now()
    if time_filter == "Past 24 Hours":
        filtered_df = filtered_df[
            filtered_df["Parsed Date"] >= (now - timedelta(days=1))
        ]
    elif time_filter == "Past Week (7 Days)":
        filtered_df = filtered_df[
            filtered_df["Parsed Date"] >= (now - timedelta(days=7))
        ]
    elif time_filter == "Past Month (30 Days)":
        filtered_df = filtered_df[
            filtered_df["Parsed Date"] >= (now - timedelta(days=30))
        ]

    # 3. Source Filter
    if selected_source != "All":
        filtered_df = filtered_df[filtered_df["Source"] == selected_source]

    # 4. Tech Skill Filter
    if selected_skills:
        for skill in selected_skills:
            filtered_df = filtered_df[
                filtered_df["Skills Extracted"].str.contains(
                    skill, case=False, na=False
                )
            ]

    # --- KEY METRICS CARDS ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Jobs Found", len(filtered_df))
    col2.metric(
        "Unique Companies",
        filtered_df["Company"].nunique() if not filtered_df.empty else 0,
    )
    col3.metric("Time Window", time_filter)

    st.markdown("---")

    # --- DATA TABLE & LINKS ---
    st.subheader("📋 Active Remote Job Openings")

    if filtered_df.empty:
        st.warning(
            "No jobs match your current filter criteria or time window."
        )
    else:
        for _, row in filtered_df.iterrows():
            with st.container():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"### [{row['Title']}]({row['Apply Link']})")
                    st.markdown(
                        f"**Company:** {row['Company']} | **Location:** {row['Location']} | **Posted:** {row['Published Date']}"
                    )
                    st.markdown(
                        f"**Tech Stack:** `{row['Skills Extracted']}`"
                    )
                with c2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.link_button("👉 Apply Now", row['Apply Link'])
                st.markdown("---")