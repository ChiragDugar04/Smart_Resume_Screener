import streamlit as st
import httpx
import asyncio

# --- Page Configuration ---
st.set_page_config(
    page_title="Resume Screener",  # Changed page title
    page_icon="🔍",               # Changed icon from rocket to magnifying glass
    layout="wide"
)

# --- Custom CSS for a Polished Look ---
CSS = """
body { background-color: #f0f2f6; }
.stButton>button { width: 100%; border-radius: 20px; border: 1px solid #4B8BBE; background-color: #4B8BBE; color: white; transition: all 0.2s; }
.stButton>button:hover { transform: scale(1.02); border-color: #3A6A94; background-color: #3A6A94; }
.st-emotion-cache-1r6slb0 { border: 1px solid #e6e6e6; }
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# --- Backend API URL ---
API_URL = "http://127.0.0.1:8000/screen/"

# --- Function to display colored breakdown scores ---
def display_breakdown_score(category, percentage):
    """Converts a percentage to a score out of 10 and displays it with color."""
    score_out_of_10 = round(percentage / 10.0, 1)
    
    if score_out_of_10 >= 8.0:
        color = "#28a745"  # Green
    elif score_out_of_10 >= 5.0:
        color = "#ffc107"  # Yellow
    else:
        color = "#dc3545"  # Red

    st.markdown(f"**{category}**")
    st.markdown(f"<h3 style='color: {color};'>{score_out_of_10} / 10</h3>", unsafe_allow_html=True)

# --- Asynchronous API Call Function ---
async def call_api_for_resume(client, file, job_description):
    """Calls the API and robustly handles all possible success and error cases."""
    try:
        files = {'resume_file': (file.name, file.getvalue(), 'application/pdf')}
        data = {'job_description': job_description}
        response = await client.post(API_URL, files=files, data=data, timeout=90.0)
        
        if response.status_code == 200:
            return {"status": "success", "filename": file.name, "data": response.json()}
        else:
            try:
                error_detail = response.json().get("detail", response.text)
            except:
                error_detail = response.text or "Unknown server error."
            return {"status": "error", "filename": file.name, "message": error_detail}
    except httpx.ConnectError as e:
        return {"status": "error", "filename": file.name, "message": "Connection Error: Cannot reach the backend server."}
    except Exception as e:
        return {"status": "error", "filename": file.name, "message": str(e)}

# --- Main App UI ---
# --- NEW: Centered Title ---
st.markdown("<h1 style='text-align: center;'>🔍 Resume Screener</h1>", unsafe_allow_html=True)

with st.container(border=True):
    job_description = st.text_area("**Paste the Job Description Here**", height=250)
    uploaded_files = st.file_uploader("**Upload Candidate Resumes (PDFs)**", type="pdf", accept_multiple_files=True)

if st.button("Analyze All Resumes", type="primary", use_container_width=True):
    if uploaded_files and job_description:
        with st.spinner(f'Analyzing {len(uploaded_files)} resumes...'):
            async def main():
                successful_results, failed_results = [], []
                async with httpx.AsyncClient() as client:
                    tasks = [call_api_for_resume(client, file, job_description) for file in uploaded_files]
                    api_responses = await asyncio.gather(*tasks)
                for res in api_responses:
                    (successful_results if res["status"] == "success" else failed_results).append(res)
                return successful_results, failed_results

            successful_results, failed_results = asyncio.run(main())

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