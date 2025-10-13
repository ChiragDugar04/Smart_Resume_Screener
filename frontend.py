import streamlit as st
import httpx
import asyncio
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Resume Screener", page_icon="🔍", layout="wide")

# --- Custom CSS ---
CSS = """
body { background-color: #f0f2f6; }
.stButton>button { width: 100%; border-radius: 20px; border: 1px solid #4B8BBE; background-color: #4B8BBE; color: white; transition: all 0.2s; }
.stButton>button:hover { transform: scale(1.02); border-color: #3A6A94; background-color: #3A6A94; }
.st-emotion-cache-1r6slb0 { border: 1px solid #e6e6e6; }
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# --- Backend API URLs ---
ANALYZE_API_URL = "http://127.0.0.1:8000/screen/"
SEARCH_API_URL = "http://127.0.0.1:8000/search-talent-pool/"

# --- Helper Functions ---
def display_breakdown_score(category, percentage):
    score_out_of_10 = round(percentage / 10.0, 1)
    color = "#28a745" if score_out_of_10 >= 8.0 else "#ffc107" if score_out_of_10 >= 5.0 else "#dc3545"
    st.markdown(f"**{category}**")
    st.markdown(f"<h3 style='color: {color};'>{score_out_of_10} / 10</h3>", unsafe_allow_html=True)

async def call_analyze_api(client, file, job_description):
    try:
        files = {'resume_file': (file.name, file.getvalue(), 'application/pdf')}
        data = {'job_description': job_description}
        response = await client.post(ANALYZE_API_URL, files=files, data=data, timeout=90.0)
        if response.status_code == 200:
            return {"status": "success", "filename": file.name, "data": response.json()}
        else:
            try:
                error_detail = response.json().get("detail", response.text)
            except:
                error_detail = response.text or "Unknown server error."
            return {"status": "error", "filename": file.name, "message": error_detail}
    except Exception as e:
        return {"status": "error", "filename": file.name, "message": str(e)}

# --- Main App UI ---
st.markdown("<h1 style='text-align: center;'>🔍 Resume Screener</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- UI Tabs for different actions ---
tab1, tab2 = st.tabs(["Analyze New Resumes", "Search Talent Pool"])

with tab1:
    st.header("Analyze and Add to Talent Pool")
    with st.container(border=True):
        jd_analyze = st.text_area("Paste Job Description to Analyze", height=200, key="jd_analyze")
        uploaded_files = st.file_uploader("Upload Candidate Resumes (PDFs)", type="pdf", accept_multiple_files=True)

    if st.button("Analyze Resumes", type="primary", use_container_width=True, key="analyze_button"):
        if uploaded_files and jd_analyze:
            # --- THIS IS THE RESTORED LOGIC ---
            with st.spinner(f'Analyzing {len(uploaded_files)} resumes...'):
                async def run_analysis():
                    successful_results, failed_results = [], []
                    async with httpx.AsyncClient() as client:
                        tasks = [call_analyze_api(client, file, jd_analyze) for file in uploaded_files]
                        api_responses = await asyncio.gather(*tasks)
                    for res in api_responses:
                        (successful_results if res["status"] == "success" else failed_results).append(res)
                    return successful_results, failed_results

                successful_results, failed_results = asyncio.run(run_analysis())

            st.success("Analysis Complete!")

            if successful_results:
                st.subheader("✅ Candidate Rankings")
                sorted_results = sorted(successful_results, key=lambda x: x['data']['match_data']['match_score'], reverse=True)

                for index, result in enumerate(sorted_results):
                    match_data = result['data']['match_data']
                    score_out_of_10 = round(match_data['match_score'] / 10.0)
                    with st.expander(f"**#{index + 1} {result['filename']}** - Score: **{score_out_of_10}/10**"):
                        st.info(f"**Summary:** {match_data['summary']}")
                        st.divider()
                        st.markdown("##### Match Breakdown")
                        breakdown_items = match_data.get('breakdown', [])
                        row1 = st.columns(4)
                        for i, item in enumerate(breakdown_items[:4]):
                            with row1[i]:
                                display_breakdown_score(item.get('category'), item.get('match_percentage'))
                        st.divider()
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("##### 💪 Strengths")
                            for strength in match_data['strengths']: st.markdown(f"- {strength}")
                        with col2:
                            st.markdown("##### 🚩 Weaknesses / Gaps")
                            for weakness in match_data['weaknesses']: st.markdown(f"- {weakness}")
            
            if failed_results:
                st.subheader("❌ Failed Analyses")
                for res in failed_results:
                    st.error(f"**File:** {res['filename']} \n\n **Reason:** {res['message']}")
        else:
            st.warning("Please upload at least one resume and provide a job description.")

with tab2:
    st.header("Query Your Existing Talent Database")
    with st.container(border=True):
        jd_search = st.text_area("Paste NEW Job Description to Search With", height=200, key="jd_search")
        score_threshold = st.slider("Minimum Match Score (0-100)", 0, 100, 70)

    if st.button("Search Talent Pool", type="primary", use_container_width=True, key="search_button"):
        if jd_search:
            with st.spinner("Searching and re-scoring candidates in the database..."):
                try:
                    data = {'job_description': jd_search, 'score_threshold': score_threshold}
                    response = httpx.post(SEARCH_API_URL, data=data, timeout=300.0)
                    
                    if response.status_code == 200:
                        search_results = response.json()
                        st.success(f"Found {len(search_results)} matching candidates above the {score_threshold}% threshold.")
                        
                        if search_results:
                            df = pd.DataFrame(search_results)
                            df = df.rename(columns={"full_name": "Name", "email": "Email", "new_match_score": "Match Score", "summary": "AI Summary"})
                            st.dataframe(df, use_container_width=True, height=400,
                                column_config={
                                    "Match Score": st.column_config.ProgressColumn("Match Score", format="%d", min_value=0, max_value=100)
                                }
                            )
                    else:
                        st.error(f"Error searching talent pool: {response.text}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please provide a job description to search the talent pool.")