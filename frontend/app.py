import streamlit as st
import requests


# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"


# --- UI Setup ---
st.set_page_config(page_title="AI Resume Screener", layout="wide", page_icon="📄")


# --- Custom CSS (with fix) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    body { font-family: 'Roboto', sans-serif; background-color: #f0f4f8; }
    .main-container { max-width: 1200px; margin: auto; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 2px solid #e0e0e0; }
    .stTabs [data-baseweb="tab"] { padding: 1rem; font-weight: 500; color: #555; }
    .stTabs [aria-selected="true"] { border-bottom: 2px solid #2563eb; color: #2563eb; }
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        background-color: #ffffff;
        color: #4A5568 !important; /* <-- FIX: Ensures all text inside is readable */
    }
    .stButton>button {
        width: 100%; border-radius: 8px; border: none; background-color: #2563eb;
        color: white; padding: 12px 0; font-weight: 500; transition: background-color 0.3s;
    }
    .stButton>button:hover { background-color: #1d4ed8; }
    .score-bar-container { margin-bottom: 1rem; }
    .score-bar-text {
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;
    }
    .score-bar-text span { font-weight: 500; color: #4A5568; } /* Darker text for category */
    .score-bar-text strong { font-size: 1.1em; } /* Smaller score text */
    .progress-bar-background { background-color: #e0e7ff; border-radius: 5px; height: 8px; width: 100%; }
    .progress-bar-fill { height: 100%; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)


def get_score_color(percentage):
    if percentage >= 80: return "#28a745"
    elif percentage >= 50: return "#ffc107"
    else: return "#dc3545"


def display_score_bar(category, percentage):
    score_out_of_10 = round(percentage / 10.0, 1)
    color = get_score_color(percentage)
    bar_html = f"""
    <div class="score-bar-container">
        <div class="score-bar-text">
            <span>{category}</span>
            <strong style='color:{color}'>{score_out_of_10}/10</strong>
        </div>
        <div class="progress-bar-background">
            <div class="progress-bar-fill" style="width: {percentage}%; background-color: {color};"></div>
        </div>
    </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)


# --- Reusable Display Function ---
def display_results(results):
    st.subheader("Screening Results")
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    for i, result in enumerate(results):
        rank = i + 1
        name = result.get('name', "Candidate")
        score = result.get('score', 0)
        source_file = result.get('source_file', 'N/A')
        
        expander_label = f"**{rank}. {name}** - *Source: {source_file}*"

        with st.expander(expander_label):
            score_color = get_score_color(score)
            st.markdown(f"### Overall Match Score: <span style='color: {score_color};'>{score}%</span>", unsafe_allow_html=True)
            st.markdown("---")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("AI Summary")
                summary = result.get('summary', {})
                st.markdown("**Strengths:**")
                for strength in summary.get('strengths', ['N/A']):
                    st.markdown(f"✅ {strength}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown("**Weaknesses:**")
                for weakness in summary.get('weaknesses', ['N/A']):
                    st.markdown(f"❌ {weakness}")

            with col2:
                st.subheader("Breakdown")
                partials = result.get('partial_scores', {})
                for key, value in partials.items():
                    display_score_bar(key.replace("_", " ").title(), value)


# --- Main App ---
st.markdown("<div class='main-container'>", unsafe_allow_html=True)

# --- THIS IS THE ONLY CHANGE ---
st.markdown("<h1 style='text-align: center;'>📄 AI-Powered Resume Screener</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Streamline your hiring process by intelligently screening and ranking candidates.</p>", unsafe_allow_html=True)
# --- END OF CHANGE ---

tab1, tab2 = st.tabs(["Screen & Add Resumes", "Search Talent Pool"])

with tab1:
    st.header("Analyze New Resumes")
    jd_part1 = st.text_area("Paste the Job Description here:", height=200, key="jd_part1_tab")
    uploaded_files = st.file_uploader("Upload Resumes (PDF)...", type=["pdf"], accept_multiple_files=True, key="resumes_tab")

    if st.button("Analyze Resumes", use_container_width=True):
        if uploaded_files and jd_part1:
            with st.spinner(f"Analyzing {len(uploaded_files)} resumes..."):
                results = []
                for file in uploaded_files:
                    files = {'resume_file': (file.name, file.getvalue(), file.type)}
                    data = {'job_description': jd_part1}
                    try:
                        response = requests.post(f"{BACKEND_URL}/screen/", files=files, data=data, timeout=90)
                        if response.status_code == 200:
                            result = response.json()
                            result['source_file'] = file.name
                            results.append(result)
                        else:
                            st.error(f"Error processing {file.name}: {response.json().get('detail', response.text)}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Failed to connect to the backend: {e}")
                        break
                st.session_state.results_part1 = results
        else:
            st.warning("Please provide a job description and upload at least one resume.")

    if 'results_part1' in st.session_state and st.session_state.results_part1:
        display_results(st.session_state.results_part1)

with tab2:
    st.header("Search Your Existing Talent Pool")
    jd_part2 = st.text_area("Paste a new Job Description to search:", height=200, key="jd_part2_tab")

    col1, col2 = st.columns(2)
    with col1:
        threshold = st.slider("Minimum Score Threshold (%)", 0, 100, 70, key="threshold_tab")
    with col2:
        num_candidates = st.number_input("Number of candidates to find", 1, 50, 5, key="num_candidates_tab")

    if st.button("Search Talent Pool", use_container_width=True):
        if jd_part2:
            with st.spinner("Searching talent pool and re-scoring..."):
                try:
                    response = requests.get(f"{BACKEND_URL}/resumes/", timeout=30)
                    talent_pool = response.json()
                    if not talent_pool:
                        st.warning("Talent pool is empty.")
                        st.stop()
                    
                    all_results = []
                    progress_bar = st.progress(0.0, "Re-scoring resumes...")
                    
                    for i, resume in enumerate(talent_pool):
                        files = {'resume_file': (resume['filename'], resume['text'], 'text/plain')}
                        data = {'job_description': jd_part2}
                        
                        rescreen_response = requests.post(f"{BACKEND_URL}/screen/", files=files, data=data, timeout=90)
                        if rescreen_response.status_code == 200:
                            result = rescreen_response.json()
                            result['source_file'] = resume['filename']
                            all_results.append(result)
                        
                        progress_bar.progress((i + 1) / len(talent_pool), f"Re-scoring... ({i+1}/{len(talent_pool)})")
                    
                    filtered_results = [res for res in all_results if res.get('score', 0) >= threshold]
                    filtered_results.sort(key=lambda x: x.get('score', 0), reverse=True)
                    final_results = filtered_results[:num_candidates]
                    st.session_state.results_part2 = final_results
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to connect to the backend: {e}")
        else:
            st.warning("Please provide a job description.")

    if 'results_part2' in st.session_state:
        if not st.session_state.results_part2:
            st.info(f"No candidates found with a score of {threshold}% or higher.")
        else:
            display_results(st.session_state.results_part2)

st.markdown("</div>", unsafe_allow_html=True)

