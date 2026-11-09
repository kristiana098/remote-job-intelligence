import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Job Pipeline Dashboard", page_icon="📊", layout="wide"
)

st.title("📊 Data & Analytics Job Aggregator")
st.write(
    "Explore live filtered job postings fetched from your automated pipeline."
)


@st.cache_data
def load_data():
  filename = "cleaned_remote_jobs.csv"
  if not os.path.exists(filename):
    return None
  try:
    # on_bad_lines='skip' ignores any broken rows instead of crashing the app
    return pd.read_csv(filename, on_bad_lines="skip")
  except Exception as e:
    st.error(f"Error reading data file: {e}")
    return None


df = load_data()

if df is None or df.empty:
  st.warning(
      "⚠️ No job data found (`cleaned_remote_jobs.csv` is missing or empty)."
      " Run `python job_fetcher.py` first!"
  )
else:
  st.sidebar.header("Filter Jobs")
  sources = ["All"] + list(df["Source"].dropna().unique())
  selected_source = st.sidebar.selectbox("Source Platform", sources)
  search_query = st.sidebar.text_input("Search Title or Skills", "")

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

  col1, col2 = st.columns(2)
  col1.metric("Total Jobs Displayed", len(filtered_df))
  col2.metric(
      "Unique Companies",
      filtered_df["Company"].nunique() if not filtered_df.empty else 0,
  )

  st.markdown("---")

  if filtered_df.empty:
    st.info("ℹ️ No jobs match your current filter criteria.")
  else:
    for index, row in filtered_df.iterrows():
      with st.container():
        st.subheader(row.get("Title", "Untitled Role"))
        st.write(
            f"**Company:** {row.get('Company', 'Unknown')} | **Location:**"
            f" {row.get('Location', 'Remote')} | **Source:**"
            f" {row.get('Source', 'Unknown')}"
        )
        st.write(f"🛠️ **Skills:** `{row.get('Skills Extracted', 'None')}`")
        apply_link = row.get("Apply Link")
        if apply_link and pd.notna(apply_link):
          st.markdown(f"[Apply Here]({apply_link})", unsafe_allow_html=True)
        st.markdown("---")