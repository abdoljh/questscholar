import streamlit as st
import asyncio
import os
import json
from pathlib import Path
from datetime import datetime
import importlib

# Page configuration
st.set_page_config(
    page_title="QuestScholar - Research Analysis",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #667eea;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff6b35;
        text-align: center;
        font-style: italic;
        margin-bottom: 2rem;
    }
    .stProgress > div > div > div > div {
        background-color: #667eea;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'workflow_running' not in st.session_state:
    st.session_state.workflow_running = False
if 'execution_logs' not in st.session_state:
    st.session_state.execution_logs = []
if 'results' not in st.session_state:
    st.session_state.results = None
if 'statistics' not in st.session_state:
    st.session_state.statistics = None

def check_environment():
    """Check if required environment variables and files exist"""
    issues = []
    
    # Check for .env file
    #if not os.path.exists('env'):
        #issues.append("⚠️ 'env' file not found. Please create it with GOOGLE_API_KEY and ENTREZ_MAIL")
    
    # Check for tools file
    if not os.path.exists('my_tools.py'):
        issues.append("⚠️ 'my_tools.py' not found")
    
    # Check for requirements
    try:
        import google.adk
        import semanticscholar
        import arxiv
        from Bio import Entrez
        from reportlab.lib.pagesizes import A4
    except ImportError as e:
        issues.append(f"⚠️ Missing dependency: {str(e)}")
    
    return issues

def load_environment():
    """Load environment variables"""
    try:
        # Try Streamlit secrets first (for cloud deployment)
        if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
            os.environ['GOOGLE_API_KEY'] = st.secrets['GOOGLE_API_KEY']
            os.environ['ENTREZ_MAIL'] = st.secrets.get('ENTREZ_MAIL', 'default@example.com')
            return True
    except Exception:
        pass
    
    # Fall back to local .env file
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.getcwd(), 'env')
        if os.path.exists(env_path):
            load_dotenv(dotenv_path=env_path, override=True)
            return True
    except Exception:
        pass
    
    return False

def initialize_tools():
    """Initialize all research tools"""
    import my_tools
    importlib.reload(my_tools)
    
    from my_tools import (
        SemanticScholarTool, PubMedTool, ArXivTool, OpenAlexTool,
        CriticTool, PDFReportTool, HTMLReportTool
    )
    from google.adk.tools import FunctionTool
    
    # Instantiate tools
    tools = {
        'semantic': SemanticScholarTool(),
        'pubmed': PubMedTool(),
        'arxiv': ArXivTool(),
        'openalex': OpenAlexTool(),
        'critic': CriticTool(),
        'pdf': PDFReportTool(),
        'html': HTMLReportTool()
    }
    
    # Wrap with FunctionTool
    wrapped_tools = {
        'semantic_tool': FunctionTool(tools['semantic'].search),
        'pubmed_tool': FunctionTool(tools['pubmed'].search),
        'arxiv_tool': FunctionTool(tools['arxiv'].search),
        'openalex_tool': FunctionTool(tools['openalex'].search),
        'critic_eval_tool': FunctionTool(tools['critic'].evaluate_papers),
        'critic_get_tool': FunctionTool(tools['critic'].get_papers_for_evaluation),
        'dedupe_tool': FunctionTool(tools['critic'].deduplicate_collection),
        'pdf_tool': FunctionTool(tools['pdf'].generate_report),
        'html_tool': FunctionTool(tools['html'].generate_html_report)
    }
    
    return tools, wrapped_tools

def create_agents(wrapped_tools, retry_config):
    """Create all agent instances"""
    from google.adk.agents import Agent, SequentialAgent, ParallelAgent
    from google.adk.models.google_llm import Gemini
    
    # Search agents (optimized with concise instructions)
    semantic_researcher = Agent(
        name="SemanticResearcher",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),  # Faster model
        instruction="Search Semantic Scholar. Use search tool. Report: 'Semantic Scholar: Added N papers.'",
        tools=[wrapped_tools['semantic_tool']],
        output_key="semantic_research"
    )
    
    pubmed_researcher = Agent(
        name="PubMedResearcher",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="Search PubMed. Use search tool. Report: 'PubMed: Added N papers.'",
        tools=[wrapped_tools['pubmed_tool']],
        output_key="pubmed_research"
    )
    
    arxiv_researcher = Agent(
        name="ArxivResearcher",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="Search arXiv. Use search tool. Report: 'arXiv: Added N papers.'",
        tools=[wrapped_tools['arxiv_tool']],
        output_key="arxiv_research"
    )
    
    openalex_researcher = Agent(
        name="OpenAlexResearcher",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="Search OpenAlex. Use search tool. Report: 'OpenAlex: Added N papers.'",
        tools=[wrapped_tools['openalex_tool']],
        output_key="openalex_research"
    )
    
    # Aggregator Phase 1 (optimized)
    aggregator_phase1 = Agent(
        name="AggregatorPhase1",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="Call deduplicate_collection tool. Report deduplication results.",
        tools=[wrapped_tools['dedupe_tool']],
        output_key="aggregation_phase1"
    )
    
    # Critic workflow
    critic_fetcher = Agent(
        name="CriticFetcher",
        model=Gemini(model="gemini-pro-latest", retry_options=retry_config),
        instruction="Call get_papers_for_evaluation() and return the complete JSON response.",
        tools=[wrapped_tools['critic_get_tool']],
        output_key="papers_json"
    )
    
    critic_evaluator = Agent(
        name="CriticEvaluator",
        model=Gemini(model="gemini-pro-latest", retry_options=retry_config, generation_config={"temperature": 0.1}),
        instruction="""You received papers in JSON. Evaluate ALL of them.

SCORING GUIDE:
Relevance (0-5): 5=Core research, 4=Directly relevant, 3=Mentions topic, 2=Tangential, 1=Generic
Methodology (0-5): 5=RCT/large cohort/systematic review, 4=Well-designed, 3=Adequate, 2=Weak, 1=Poor
Impact (0-5): 5=100+ citations, 4=50-99, 3=10-49, 2=1-9, 1=No citations

FLAGS: review, meta_analysis, clinical_trial, case_report, guideline, preprint, genomics, targeted_therapy

For EACH paper create:
{
  "paper_title": "exact title",
  "relevance_score": NUMBER,
  "methodological_soundness": NUMBER,
  "impact_score": NUMBER,
  "redundancy_flag": false,
  "flags": ["tag1"],
  "recommended_action": "include" or "exclude",
  "rationale": "Brief explanation"
}

Call evaluate_papers([...all evaluations...]) NOW. Do not write text. ONLY call the tool.""",
        tools=[wrapped_tools['critic_eval_tool']],
        output_key="evaluations"
    )
    
    critic_workflow = SequentialAgent(
        name="CriticWorkflow",
        sub_agents=[critic_fetcher, critic_evaluator]
    )
    
    # Report generation
    pdf_reporter = Agent(
        name="PDFReporter",
        model=Gemini(model="gemini-pro-latest", retry_options=retry_config),
        instruction="Generate PDF report. Synthesize 250-word Executive Summary covering: key themes, methodological trends, high-impact contributions, quality metrics. Call 'generate_report'.",
        tools=[wrapped_tools['pdf_tool']],
        output_key="pdf_report_status"
    )
    
    html_reporter = Agent(
        name="HTMLReporter",
        model=Gemini(model="gemini-pro-latest", retry_options=retry_config),
        instruction="Generate interactive HTML report. Use SAME executive summary as PDF. Call 'generate_html_report'.",
        tools=[wrapped_tools['html_tool']],
        output_key="html_report_status"
    )
    
    report_generation = ParallelAgent(
        name="ReportGeneration",
        sub_agents=[pdf_reporter, html_reporter]
    )
    
    # Assemble workflow
    parallel_research = ParallelAgent(
        name="ParallelResearchTeam",
        sub_agents=[semantic_researcher, pubmed_researcher, arxiv_researcher, openalex_researcher]
    )
    
    root_agent = SequentialAgent(
        name="ResearchSystem",
        sub_agents=[parallel_research, aggregator_phase1, critic_workflow, report_generation]
    )
    
    return root_agent

async def run_workflow(subject, start_year, end_year, source_limits, progress_bar, status_text, log_container):
    """Execute the research workflow"""
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    import my_tools
    import sys
    from io import StringIO
    
    # Clear previous data
    importlib.reload(my_tools)
    my_tools.clear_papers()
    
    # Load environment
    status_text.text("🔑 Loading credentials...")
    if not load_environment():
        return {
            'response': None,
            'error': "Failed to load environment variables. Check your 'env' file.",
            'statistics': {},
            'logs': []
        }
    
    # Verify API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return {
            'response': None,
            'error': "GOOGLE_API_KEY not found in environment",
            'statistics': {},
            'logs': []
        }
    
    # Retry configuration
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504]
    )
    
    # Initialize tools and agents
    status_text.text("🔧 Initializing tools and agents...")
    progress_bar.progress(5)
    
    tools, wrapped_tools = initialize_tools()
    root_agent = create_agents(wrapped_tools, retry_config)
    
    # Construct prompt
    prompt = (
        f"Conduct a comprehensive research analysis on '{subject}' for years {start_year}-{end_year}.\n\n"
        f"PHASE 1 - PARALLEL SEARCH:\n"
        f"  • SemanticResearcher: Find {source_limits['semantic_scholar']} papers\n"
        f"  • PubMedResearcher: Find {source_limits['pubmed']} papers\n"
        f"  • ArxivResearcher: Find {source_limits['arxiv']} papers\n"
        f"  • OpenAlexResearcher: Find {source_limits['openalex']} papers\n\n"
        f"PHASE 2 - AGGREGATION: Deduplicate and normalize\n"
        f"PHASE 3 - CRITIC: Evaluate quality\n"
        f"PHASE 4 - REPORTS: Generate PDF and HTML\n\n"
        f"Begin now."
    )
    
    # Execute workflow
    status_text.text("🚀 Phase 1: Searching databases...")
    progress_bar.progress(10)
    
    runner = InMemoryRunner(agent=root_agent)
    response = None
    error = None
    captured_logs = []
    
    try:
        # Capture output
        log_capture = StringIO()
        
        # Track progress through phases
        phase_updates = {
            10: "Phase 1: Searching 4 databases...",
            30: "Phase 2: Deduplicating results...",
            50: "Phase 3: Critic evaluation...",
            70: "Phase 4: Generating reports..."
        }
        
        async def run_with_progress():
            nonlocal response
            response = await runner.run_debug(prompt, verbose=True)
        
        # Run workflow
        await run_with_progress()
        
        # Update progress incrementally
        for prog, msg in phase_updates.items():
            if prog <= 70:
                status_text.text(f"✓ {msg}")
                progress_bar.progress(prog)
        
        progress_bar.progress(90)
        
    except ExceptionGroup as eg:
        error = f"Multiple errors occurred:\n"
        for i, e in enumerate(eg.exceptions, 1):
            error += f"\n{i}. {type(e).__name__}: {str(e)}"
    except Exception as e:
        error = f"{type(e).__name__}: {str(e)}"
    
    # Get statistics
    status_text.text("📊 Calculating statistics...")
    progress_bar.progress(95)
    
    stats = {
        'total_collected': len(my_tools.COLLECTED_PAPERS),
        'total_evaluated': len(my_tools.CRITIC_EVALUATIONS),
        'high_rated': 0,
        'excluded': 0,
        'avg_relevance': 0,
        'avg_methodology': 0,
        'avg_impact': 0
    }
    
    if stats['total_evaluated'] > 0:
        evals = my_tools.CRITIC_EVALUATIONS.values()
        stats['high_rated'] = sum(1 for e in evals if e['overall_score'] >= 4.0)
        stats['excluded'] = sum(1 for e in evals if e['recommended_action'] == 'exclude')
        stats['avg_relevance'] = sum(e['relevance_score'] for e in evals) / stats['total_evaluated']
        stats['avg_methodology'] = sum(e['methodological_soundness'] for e in evals) / stats['total_evaluated']
        stats['avg_impact'] = sum(e['impact_score'] for e in evals) / stats['total_evaluated']
    
    progress_bar.progress(100)
    status_text.text("✅ Workflow complete!")
    
    return {
        'response': response,
        'error': error,
        'statistics': stats,
        'logs': captured_logs,
        'files_generated': {
            'pdf': os.path.exists('executive_summary.pdf'),
            'html': os.path.exists('executive_summary.html')
        }
    }

# Header with logo
logo_col, title_col = st.columns([1, 4])

with logo_col:
    # Try to display logo with multiple fallback paths
    logo_found = False
    logo_paths = [
        'QuestScholar_logo.PNG',
        'questscholar_logo.png',
        'logo.png',
        'QuestScholar_logo.png'
    ]
    
    for logo_path in logo_paths:
        if os.path.exists(logo_path):
            try:
                st.image(logo_path, width=150)
                logo_found = True
                break
            except Exception:
                continue
    
    if not logo_found:
        # Display emoji as fallback
        st.markdown('<div style="font-size: 100px; text-align: center;">🎓</div>', unsafe_allow_html=True)

with title_col:
    st.markdown('<h1 class="main-header">QuestScholar</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Hunt Smarter, Research Deeper</p>', unsafe_allow_html=True)

# Check environment
with st.expander("🔧 System Status", expanded=False):
    issues = check_environment()
    if issues:
        for issue in issues:
            st.warning(issue)
    else:
        st.success("✅ All dependencies and files found")

# Sidebar configuration
st.sidebar.header("🎯 Research Configuration")

subject = st.sidebar.text_input(
    "Research Subject",
    value="Langerhans Cell Histiocytosis",
    help="💡 Tip: Be specific! 'BRAF mutations in melanoma' > 'cancer research'"
)

col1, col2 = st.sidebar.columns(2)
with col1:
    start_year = st.number_input("Start Year", min_value=1900, max_value=2026, value=2021)
with col2:
    end_year = st.number_input("End Year", min_value=1900, max_value=2026, value=2026)

st.sidebar.subheader("📚 Papers per Source")
semantic_limit = st.sidebar.slider("Semantic Scholar", 1, 20, 7)
pubmed_limit = st.sidebar.slider("PubMed", 1, 20, 7)
arxiv_limit = st.sidebar.slider("arXiv", 1, 20, 7)
openalex_limit = st.sidebar.slider("OpenAlex", 1, 20, 7)

source_limits = {
    'semantic_scholar': semantic_limit,
    'pubmed': pubmed_limit,
    'arxiv': arxiv_limit,
    'openalex': openalex_limit
}

st.sidebar.markdown("---")
run_button = st.sidebar.button("🚀 Start Research", type="primary", disabled=st.session_state.workflow_running)

# Main content area
if run_button and not st.session_state.workflow_running:
    st.session_state.workflow_running = True
    st.session_state.execution_logs = []
    st.session_state.results = None
    st.session_state.statistics = None
    
    # Progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Execution log
    with st.expander("📋 Execution Log", expanded=True):
        log_container = st.container()
    
    # Run workflow
    try:
        results = asyncio.run(
            run_workflow(subject, start_year, end_year, source_limits, progress_bar, status_text, log_container)
        )
        
        # Store results
        if results:
            st.session_state.results = results
            st.session_state.statistics = results.get('statistics', {})
        else:
            st.session_state.results = {
                'error': 'Workflow returned no results',
                'response': None,
                'statistics': {},
                'logs': [],
                'files_generated': {'pdf': False, 'html': False}
            }
            st.session_state.statistics = {}
    except Exception as e:
        st.session_state.results = {
            'error': str(e),
            'response': None,
            'statistics': {},
            'logs': [],
            'files_generated': {'pdf': False, 'html': False}
        }
        st.session_state.statistics = {}
    finally:
        st.session_state.workflow_running = False
        # Clean up progress indicators
        progress_bar.empty()
        status_text.empty()
        # Force rerun to display results
        st.rerun()

# Display results
if st.session_state.results:
    results = st.session_state.results
    
    if results.get('error'):
        st.error(f"**Workflow Error**\n\n{results['error']}")
        
        with st.expander("🔧 Troubleshooting Tips"):
            st.markdown("""
            **Common solutions:**
            
            1. **Environment Variables Issue:**
               - For Streamlit Cloud: Add secrets in dashboard (Settings → Secrets)
               - For local: Create `env` file in project root
               
            2. **Streamlit Cloud Setup:**
               ```toml
               # In Streamlit Cloud secrets
               GOOGLE_API_KEY = "your_key_here"
               ENTREZ_MAIL = "your_email@example.com"
               ```
            
            3. **Local Setup:**
               ```bash
               # Create env file
               echo 'GOOGLE_API_KEY=your_key_here' > env
               echo 'ENTREZ_MAIL=your@email.com' >> env
               ```
            
            4. **Verify your API key:**
               - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
               - Ensure key starts with `AIza`
               - Check quota limits
            
            5. **Other checks:**
               - [ ] Internet connectivity
               - [ ] All dependencies installed: `pip install -r requirements_streamlit.txt`
               - [ ] my_tools.py is present
               - [ ] Python 3.8 or higher
            """)
    else:
        st.success("✅ **Research Complete!**")
        
        # Statistics Dashboard
        st.subheader("📊 Collection Statistics")
        stats = results['statistics']
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Papers Collected", stats['total_collected'], 
                     help="Total papers found across all sources")
        with col2:
            st.metric("Evaluated", stats['total_evaluated'],
                     help="Papers that passed initial screening")
        with col3:
            st.metric("High-Rated (≥4.0)", stats['high_rated'],
                     help="Papers with excellent quality scores")
        with col4:
            st.metric("Excluded", stats['excluded'],
                     help="Papers filtered out by critic")
        
        # Quality scores
        if stats['total_evaluated'] > 0:
            st.subheader("📈 Average Quality Scores")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                score = stats['avg_relevance']
                st.metric("Relevance", f"{score:.2f}/5.0")
                st.progress(score / 5.0)
            with col2:
                score = stats['avg_methodology']
                st.metric("Methodology", f"{score:.2f}/5.0")
                st.progress(score / 5.0)
            with col3:
                score = stats['avg_impact']
                st.metric("Impact", f"{score:.2f}/5.0")
                st.progress(score / 5.0)
            
            # Quality interpretation
            avg_overall = (stats['avg_relevance'] + stats['avg_methodology'] + stats['avg_impact']) / 3
            
            if avg_overall >= 4.0:
                quality_msg = "🌟 **Exceptional** - High-quality, relevant research collection"
                quality_color = "success"
            elif avg_overall >= 3.5:
                quality_msg = "✅ **Good** - Solid research foundation"
                quality_color = "info"
            elif avg_overall >= 3.0:
                quality_msg = "⚠️ **Moderate** - Consider refining search criteria"
                quality_color = "warning"
            else:
                quality_msg = "❌ **Low** - Try different keywords or date range"
                quality_color = "error"
            
            if quality_color == "success":
                st.success(quality_msg)
            elif quality_color == "info":
                st.info(quality_msg)
            elif quality_color == "warning":
                st.warning(quality_msg)
            else:
                st.error(quality_msg)
        
        # Download reports
        st.subheader("📥 Download Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if results.get('files_generated', {}).get('pdf'):
                with open('executive_summary.pdf', 'rb') as f:
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=f,
                        file_name=f"QuestScholar_{subject.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        help="Professional PDF report for printing and citation"
                    )
                    st.caption("✓ PDF generated successfully")
            else:
                st.warning("⚠️ PDF report not available")
        
        with col2:
            if results.get('files_generated', {}).get('html'):
                with open('executive_summary.html', 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="🌐 Download HTML Report",
                        data=f,
                        file_name=f"QuestScholar_{subject.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.html",
                        mime="text/html",
                        help="Interactive HTML with download links and citations"
                    )
                    st.caption("✓ HTML generated successfully")
            else:
                st.warning("⚠️ HTML report not available")
        
        # Report features
        with st.expander("📋 Report Features"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **PDF Report:**
                - 📄 Professional formatting
                - 🎨 Custom branding
                - 📊 Critic evaluations
                - 🔢 Citation counts
                - ⭐ Quality rankings
                """)
            with col2:
                st.markdown("""
                **HTML Report:**
                - 🔗 Clickable links
                - ⬇️ Download buttons (arXiv)
                - 📋 Copy citations
                - 📱 Responsive design
                - 🎯 Interactive navigation
                """)
        
        # Raw data access
        with st.expander("🔬 Advanced: View Raw Data"):
            st.json({
                'subject': subject,
                'date_range': f"{start_year}-{end_year}",
                'statistics': stats,
                'timestamp': datetime.now().isoformat()
            })

else:
    # Welcome screen
    st.info("""
    👋 **Welcome to QuestScholar!**
    
    This AI-powered research tool helps you:
    - 🔍 Search multiple academic databases simultaneously
    - 🎯 Evaluate papers using AI critic agents
    - 📊 Generate comprehensive research reports
    - 📥 Export results in PDF and HTML formats
    
    **Getting Started:**
    1. Configure your research parameters in the sidebar
    2. Click "🚀 Start Research" to begin
    3. Wait for the analysis to complete (2-5 minutes)
    4. Download your reports
    
    **Pro Tips:**
    - Start with 5-10 papers per source for faster results
    - Use specific keywords for better relevance
    - Recent years (2020+) have better coverage
    """)
    
    # Setup instructions based on environment
    with st.expander("⚙️ First Time Setup"):
        tab1, tab2 = st.tabs(["Streamlit Cloud", "Local Installation"])
        
        with tab1:
            st.markdown("""
            ### Streamlit Cloud Setup
            
            **Step 1: Add Secrets**
            1. Go to your app settings (☰ menu → Settings)
            2. Click on "Secrets" in the left sidebar
            3. Add the following:
            
            ```toml
            GOOGLE_API_KEY = "your_google_api_key_here"
            ENTREZ_MAIL = "your_email@example.com"
            ```
            
            **Step 2: Get Google API Key**
            1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. Click "Create API Key"
            3. Copy the key (starts with `AIza`)
            4. Paste into Streamlit secrets
            
            **Step 3: Save and Reboot**
            - Click "Save" in secrets editor
            - Reboot the app
            - Done! 🎉
            """)
        
        with tab2:
            st.markdown("""
            ### Local Installation Setup
            
            **Step 1: Create Environment File**
            ```bash
            # Create env file (no extension!)
            cat > env << EOF
            GOOGLE_API_KEY=your_google_api_key_here
            ENTREZ_MAIL=your_email@example.com
            EOF
            ```
            
            **Step 2: Install Dependencies**
            ```bash
            pip install -r requirements_streamlit.txt
            ```
            
            **Step 3: Run the App**
            ```bash
            streamlit run streamlit_app.py
            ```
            
            **Quick Launcher (Alternative):**
            ```bash
            # Linux/Mac
            chmod +x run_questscholar.sh
            ./run_questscholar.sh
            
            # Windows
            run_questscholar.bat
            ```
            """)
    
    # Quick examples
    with st.expander("💡 Example Research Topics"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Medical Research:**
            - Langerhans Cell Histiocytosis
            - CRISPR gene therapy
            - mRNA vaccine efficacy
            - Cancer immunotherapy
            """)
        with col2:
            st.markdown("""
            **Technology:**
            - Quantum computing applications
            - Large language models
            - Neural network architectures
            - Cybersecurity frameworks
            """)
    
    # Tips for better results
    with st.expander("🎯 Tips for High-Quality Results"):
        st.markdown("""
        **To get better quality scores (3.5+):**
        
        ✅ **DO:**
        - Use specific terms: "BRAF V600E mutations" not "cancer"
        - Include methodology: "randomized controlled trial diabetes"
        - Specify outcomes: "COVID-19 vaccine efficacy children"
        - Recent years work best: 2020-2026
        - Start with 5-7 papers per source
        
        ❌ **AVOID:**
        - Too broad: "medicine", "technology", "research"
        - Too narrow: "XYZ-123 protein in cell line ABC"
        - Mixing unrelated topics: "AI and climate and health"
        - Very old date ranges: 1950-1970
        
        **Quality Score Breakdown:**
        - **4.5+** (⭐⭐ Exceptional): Landmark studies, RCTs, 100+ citations
        - **4.0-4.4** (⭐ Excellent): High-quality research, 50+ citations
        - **3.5-3.9** (✓ Good): Solid contributions, well-designed
        - **3.0-3.4** (○ Acceptable): Standard research
        - **<3.0** (⚠️ Low): Consider refining your search
        
        **Example transformations:**
        - ❌ "heart disease" → ✅ "atrial fibrillation anticoagulation therapy"
        - ❌ "AI" → ✅ "transformer models natural language processing"
        - ❌ "rare diseases" → ✅ "Langerhans cell histiocytosis BRAF mutations"
        """)


# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
### About QuestScholar
**Version:** 4.00  
**Website:** [questscholar.com](https://www.questscholar.com) (Under Construction)

**Features:**
- Multi-source paper collection
- AI-powered quality evaluation
- Interactive HTML reports
- Professional PDF exports
""")