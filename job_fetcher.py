import os
import pandas as pd
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Job Pipeline Dashboard", page_icon="📊", layout="wide"
)

st.title("📊 Data & Analytics Job Aggregator")
st.write("Explore live filtered job postings fetched from your automated pipeline.")


# 2. Crash-Proof Data Loader with Caching
@st.cache_data
def load_data():
    filename = "cleaned_remote_jobs.csv"
    if not os.path.exists(filename):
        return None  # Return None if file is missing
    try:
        return pd.read_csv(filename)
    except Exception as e:
        st.error(f"Error reading data file: {e}")
        return None


df = load_data()

# 3. Handle Missing File Gracefully
if df is None or df.empty:
    st.warning(
        "⚠️ No job data found (`cleaned_remote_jobs.csv` is missing or empty).\n\n"
        "Please run your local pipeline script (`python main.py`) or wait for your "
        "GitHub Actions daily workflow to generate the data!"
    )
else:
    # 4. Sidebar Filters (Safe extraction of unique values)
    st.sidebar.header("Filter Jobs")

    sources = ["All"] + list(df["Source"].dropna().unique())
    selected_source = st.sidebar.selectbox("Source Platform", sources)

    search_query = st.sidebar.text_input("Search Title or Skills", "")

    # Apply Filters Safely
    filtered_df = df.copy()
    if selected_source != "All":
        filtered_df = filtered_df[filtered_df["Source"] == selected_source]

    if search_query:
        filtered_df = filtered_df[
            filtered_df["Title"].str.contains(search_query, case=False, na=False)
            | filtered_df["Skills Extracted"].str.contains(
                search_query, case=False, na=False
            )
        ]

    # 5. Main Metrics & Display
    col1, col2 = st.columns(2)
    col1.metric("Total Jobs Displayed", len(filtered_df))
    col2.metric("Unique Companies", filtered_df["Company"].nunique() if not filtered_df.empty else 0)

    st.markdown("---")

    # 6. Safe Rendering Loop
    if filtered_df.empty:
        st.info("ℹ️ No jobs match your current filter criteria.")
    else:
        for index, row in filtered_df.iterrows():
            with st.container():
                st.subheader(row.get("Title", "Untitled Role"))
                st.write(
                    f"**Company:** {row.get('Company', 'Unknown')} | "
                    f"**Location:** {row.get('Location', 'Remote')} | "
                    f"**Source:** {row.get('Source', 'Unknown')}"
                )
                st.write(f"🛠️ **Skills:** `{row.get('Skills Extracted', 'None')}`")
                
                apply_link = row.get("Apply Link")
                if apply_link and pd.notna(apply_link):
                    st.markdown(f"[Apply Here]({apply_link})", unsafe_allow_html=True)
                st.markdown("---")
