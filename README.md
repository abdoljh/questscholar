# 🎓 QuestScholar

<div align="center">

![QuestScholar Logo](QuestScholar_logo.PNG)

**Hunt Smarter, Research Deeper**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.31+-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[**🚀 Quick Start**](#-quick-start) • [**📖 Documentation**](#-documentation) • [**🎥 Demo**](#-demo) • [**🤝 Contributing**](#-contributing)

</div>

-----

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Examples](#-examples)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

-----
<a id="-overview"></a>
## 🌟 Overview

QuestScholar is an AI-powered research analysis platform that revolutionizes academic literature review. By leveraging Google’s Gemini AI and a multi-agent architecture, it automatically searches, evaluates, and synthesizes research papers from multiple databases, saving researchers countless hours of manual work.

### The Problem

Traditional literature reviews are:

- ⏰ **Time-consuming**: Hours spent searching multiple databases
- 🎯 **Inconsistent**: Quality varies based on reviewer expertise
- 📊 **Fragmented**: Results scattered across different platforms
- 🔄 **Repetitive**: Manual deduplication and comparison
- 📝 **Labor-intensive**: Extensive note-taking and synthesis

### The Solution

QuestScholar automates the entire workflow:

1. **Parallel Search**: Simultaneously queries 4 major academic databases
1. **AI Evaluation**: Gemini models assess relevance, methodology, and impact
1. **Smart Filtering**: Automatic deduplication and quality ranking
1. **Report Generation**: Professional PDF and interactive HTML outputs
1. **Web Interface**: User-friendly Streamlit dashboard

-----
<a id="-key-features"></a>
## ✨ Key Features

### 🔍 Multi-Database Search

- **Semantic Scholar**: 200M+ papers with citation data
- **PubMed**: 35M+ biomedical literature citations
- **arXiv**: 2M+ preprints in STEM fields
- **OpenAlex**: 250M+ scholarly works

### 🤖 AI-Powered Analysis

- **Relevance Scoring** (0-5): How well papers match your topic
- **Methodology Assessment** (0-5): Research design quality evaluation
- **Impact Analysis** (0-5): Citation counts and venue prestige
- **Automated Tagging**: Review types, study designs, research areas

### 📊 Intelligent Processing

- **Deduplication**: Removes redundant papers across sources
- **Normalization**: Standardizes metadata formats
- **Quality Ranking**: Sorts by combined AI scores
- **Exclusion Logic**: Filters low-quality results

### 📄 Comprehensive Reports

**PDF Report Features:**

- Executive summary with key insights
- Table of contents with quality indicators
- Detailed bibliography with critic evaluations
- Custom branding and professional formatting
- Citation counts and venue information

**HTML Report Features:**

- Interactive navigation and search
- One-click downloads for arXiv papers
- Copy-to-clipboard citations (BibTeX)
- Responsive mobile-friendly design
- Real-time filtering and sorting

### 🎨 Modern Web Interface

- Real-time progress tracking
- Interactive statistics dashboard
- Configurable search parameters
- Error handling with helpful tips
- One-click report downloads

-----
<a id="-architecture"></a>
## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Web Interface                  │
│  (User Configuration, Progress Tracking, Results Display)   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Google ADK Agent System                    │
└─────────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Phase 1    │ │   Phase 2    │ │   Phase 3    │
│   Parallel   │ │ Aggregation  │ │    Critic    │
│   Search     │ │ & Dedupe     │ │  Evaluation  │
└──────────────┘ └──────────────┘ └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   Phase 4    │
                  │   Reports    │
                  └──────────────┘
                         │
                ┌────────┴────────┐
                ▼                 ▼
         ┌───────────┐     ┌───────────┐
         │    PDF    │     │   HTML    │
         │  Report   │     │  Report   │
         └───────────┘     └───────────┘
```

### Agent Workflow

**Phase 1: Parallel Research Team**

```python
ParallelAgent(
    SemanticResearcher,  # Gemini Flash
    PubMedResearcher,    # Gemini Flash
    ArxivResearcher,     # Gemini Flash
    OpenAlexResearcher   # Gemini Flash
)
```

**Phase 2: Aggregation & Deduplication**

```python
AggregatorPhase1
├── Deduplicate papers
├── Normalize metadata
└── Prepare for evaluation
```

**Phase 3: Critic Workflow**

```python
SequentialAgent(
    CriticFetcher,     # Retrieve papers
    CriticEvaluator    # Score & rank (Gemini Pro)
)
```

**Phase 4: Report Generation**

```python
ParallelAgent(
    PDFReporter,   # Generate PDF (Gemini Pro)
    HTMLReporter   # Generate HTML (Gemini Pro)
)
```

### Technology Stack

|Component          |Technology                               |Purpose                     |
|-------------------|-----------------------------------------|----------------------------|
|**Frontend**       |Streamlit                                |Web interface               |
|**AI Models**      |Google Gemini                            |Agent reasoning & evaluation|
|**Framework**      |Google ADK                               |Multi-agent orchestration   |
|**APIs**           |Semantic Scholar, PubMed, arXiv, OpenAlex|Paper sources               |
|**PDF Generation** |ReportLab                                |Professional reports        |
|**HTML Generation**|Custom templates                         |Interactive reports         |
|**Data Processing**|Pandas, BeautifulSoup                    |Text cleaning & parsing     |

-----
<a id="-quick-start"></a>
## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google API Key ([Get one free](https://makersuite.google.com/app/apikey))
- Email address (for PubMed API)

### One-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/questscholar.git
cd questscholar

# 2. Create environment file
cat > env << EOF
GOOGLE_API_KEY=your_google_api_key_here
Entrez_email=your_email@example.com
EOF

# 3. Run launcher (handles dependencies automatically)
chmod +x run_questscholar.sh
./run_questscholar.sh
```

Your browser will open to `http://localhost:8501` 🎉

-----
<a id="-installation"></a>
## 📦 Installation

### Method 1: Automated Setup (Recommended)

**Linux/macOS:**

```bash
./run_questscholar.sh
```

**Windows:**

```bash
run_questscholar.bat
```

The launcher automatically:

- ✅ Checks Python version
- ✅ Creates virtual environment
- ✅ Installs dependencies
- ✅ Verifies configuration
- ✅ Launches the app

### Method 2: Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements_streamlit.txt

# Install system fonts (Linux only)
sudo apt-get install fonts-dejavu-core

# Launch application
streamlit run streamlit_app.py
```

### Method 3: Docker

```bash
# Build image
docker build -t questscholar .

# Run container
docker run -p 8501:8501 \
  -e GOOGLE_API_KEY="your_key" \
  -e Entrez_email="your_email" \
  questscholar
```

### Verify Installation

```bash
# Check all imports
python -c "import streamlit; import google.adk; import semanticscholar; print('✓ All OK')"

# Check Streamlit
streamlit --version

# Test run
streamlit run streamlit_app.py
```

-----
<a id="-usage"></a>
## 💻 Usage

### Basic Workflow

1. **Configure Search Parameters**
- Enter research subject (e.g., “machine learning in healthcare”)
- Set date range (e.g., 2020-2026)
- Choose papers per source (5-20 recommended)
1. **Execute Research**
- Click “🚀 Start Research”
- Monitor real-time progress
- Wait 2-5 minutes for completion
1. **Review Results**
- Examine statistics dashboard
- Check quality scores
- Review excluded papers
1. **Download Reports**
- PDF for professional use
- HTML for interactive exploration

### Interface Guide

#### Sidebar Configuration

```
┌──────────────────────────┐
│ Research Subject         │
│ [Text Input]             │
├──────────────────────────┤
│ Start Year │ End Year    │
│ [2021]     │ [2026]      │
├──────────────────────────┤
│ Papers per Source        │
│ Semantic Scholar: 7      │
│ PubMed: 7                │
│ arXiv: 7                 │
│ OpenAlex: 7              │
├──────────────────────────┤
│ [🚀 Start Research]      │
└──────────────────────────┘
```

#### Main Dashboard

```
┌────────────────────────────────────┐
│ 📊 Collection Statistics           │
├────────────────────────────────────┤
│  Papers  │ Evaluated │ High │ Excl │
│    21    │    19     │  12  │  3   │
├────────────────────────────────────┤
│ 📈 Quality Scores                  │
│ Relevance:    ████▌ 4.2/5.0       │
│ Methodology:  ████  4.0/5.0       │
│ Impact:       ███▌  3.5/5.0       │
├────────────────────────────────────┤
│ 📥 Download Reports                │
│ [📄 PDF] [🌐 HTML]                │
└────────────────────────────────────┘
```

### Command-Line Options

```bash
# Custom port
streamlit run streamlit_app.py --server.port 8502

# Custom address
streamlit run streamlit_app.py --server.address 0.0.0.0

# Disable file watcher (production)
streamlit run streamlit_app.py --server.fileWatcherType none

# Browser options
streamlit run streamlit_app.py --browser.gatherUsageStats false
```

### Python API Usage

```python
from my_tools import (
    SemanticScholarTool, PubMedTool, 
    CriticTool, PDFReportTool
)

# Search papers
semantic = SemanticScholarTool()
result = semantic.search(
    subject="quantum computing",
    start_year=2020,
    end_year=2024,
    num_papers=10
)

# Evaluate quality
critic = CriticTool()
papers_json = critic.get_papers_for_evaluation()
evaluations = critic.evaluate_papers(papers_json)

# Generate report
pdf = PDFReportTool()
pdf.generate_report(
    executive_summary="Your summary here",
    subject="quantum computing"
)
```

-----
<a id="-configuration"></a>
## ⚙️ Configuration

### Environment Variables

Create a file named `env`:

```bash
# Required
GOOGLE_API_KEY=AIzaSyA...your_key_here
Entrez_email=researcher@university.edu

# Optional
GEMINI_MODEL=gemini-pro-latest
MAX_PAPERS_PER_SOURCE=20
REPORT_TIMEOUT=300
```

### Streamlit Configuration

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#667eea"        # Brand color
backgroundColor = "#ffffff"     # Page background
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
enableCORS = false
maxUploadSize = 200
maxMessageSize = 200

[browser]
gatherUsageStats = false
serverAddress = "localhost"
```

### PDF Report Customization

Edit `my_tools.py`:

```python
# Logo settings
LOGO_PATH = "QuestScholar_logo.PNG"
LOGO_WIDTH = 1.5 * cm
LOGO_HEIGHT = 1.5 * cm

# Watermark settings
WATERMARK_OPACITY = 0.20
WATERMARK_CENTERED = True

# Colors
HEADER_LINE_COLOR = colors.darkgrey
FOOTER_LINE_COLOR = colors.lightgrey

# Fonts
DEFAULT_FONT = 'DejaVuSans'  # or 'Helvetica'
```

### Agent Instructions

Customize search strategies in `streamlit_app.py`:

```python
semantic_researcher = Agent(
    name="SemanticResearcher",
    model=Gemini(model="gemini-flash-latest"),
    instruction="""
    Your custom instructions here:
    - Focus on highly cited papers
    - Prioritize recent publications
    - Include review articles
    """,
    tools=[semantic_tool]
)
```

-----
<a id="-api-documentation"></a>
## 📚 API Documentation

### Tool Classes

#### SemanticScholarTool

```python
class SemanticScholarTool:
    def search(self, subject: str, start_year: int, 
               end_year: int, num_papers: int) -> str:
        """
        Search Semantic Scholar database.
        
        Args:
            subject: Research topic or keywords
            start_year: Start year (inclusive)
            end_year: End year (inclusive)
            num_papers: Maximum papers to return
            
        Returns:
            Status message with count of papers added
        """
```

#### CriticTool

```python
class CriticTool:
    def evaluate_papers(self, evaluations: str) -> str:
        """
        Store critic evaluations for papers.
        
        Args:
            evaluations: JSON string with paper evaluations
            
        Expected JSON structure:
        [{
            "paper_title": str,
            "relevance_score": float (0-5),
            "methodological_soundness": float (0-5),
            "impact_score": float (0-5),
            "redundancy_flag": bool,
            "flags": [str],
            "recommended_action": "include" | "exclude",
            "rationale": str
        }]
        
        Returns:
            Success message with count
        """
    
    def get_papers_for_evaluation(self) -> str:
        """
        Retrieve papers for evaluation.
        
        Returns:
            JSON string with papers data
        """
    
    def deduplicate_collection(self) -> str:
        """
        Remove duplicate papers by title similarity.
        
        Returns:
            Status message with removed count
        """
```

#### PDFReportTool

```python
class PDFReportTool:
    def generate_report(self, executive_summary: str, 
                       subject: str) -> str:
        """
        Generate professional PDF report.
        
        Args:
            executive_summary: 250-word summary
            subject: Research topic
            
        Generates:
            executive_summary.pdf
            
        Returns:
            Status message with paper counts
        """
```

#### HTMLReportTool

```python
class HTMLReportTool:
    def generate_html_report(self, executive_summary: str, 
                            subject: str) -> str:
        """
        Generate interactive HTML report.
        
        Args:
            executive_summary: 250-word summary
            subject: Research topic
            
        Generates:
            executive_summary.html
            
        Returns:
            Status message with paper counts
        """
```

### Agent Architecture

```python
# Root agent structure
root_agent = SequentialAgent(
    name="ResearchSystem",
    sub_agents=[
        ParallelAgent([
            semantic_researcher,
            pubmed_researcher,
            arxiv_researcher,
            openalex_researcher
        ]),
        aggregator_phase1,
        SequentialAgent([
            critic_fetcher,
            critic_evaluator
        ]),
        ParallelAgent([
            pdf_reporter,
            html_reporter
        ])
    ]
)
```

### Evaluation Criteria

**Relevance Score (0-5):**

- 5: Core research directly on topic
- 4: Directly relevant (specific populations, outcomes)
- 3: Mentions topic but broader scope
- 2: Tangentially related
- 1: Generic, barely related

**Methodology Score (0-5):**

- 5: RCT, large cohort, systematic review
- 4: Well-designed study
- 3: Adequate methodology
- 2: Case reports, weak design
- 1: Poor quality

**Impact Score (0-5):**

- 5: 100+ citations, top journal
- 4: 50-99 citations
- 3: 10-49 citations
- 2: 1-9 citations or very recent
- 1: No citations

-----
<a id="-examples"></a>
## 🎯 Examples

### Example 1: Medical Research

```python
# Configuration
subject = "CRISPR gene therapy clinical trials"
start_year = 2020
end_year = 2024
papers_per_source = 15

# Expected results:
# - 40-50 papers collected
# - High methodology scores (clinical trials)
# - Recent publications emphasized
# - Focus on human studies
```

**Sample Output:**

```
Papers Collected: 47
Evaluated: 44
High-Rated (≥4.0): 23
Excluded: 3

Average Scores:
Relevance: 4.5/5.0
Methodology: 4.2/5.0
Impact: 3.8/5.0

Quality: ⭐⭐ Exceptional
```

### Example 2: Computer Science

```python
# Configuration
subject = "transformer architectures large language models"
start_year = 2017
end_year = 2024
papers_per_source = 20

# Expected results:
# - 60-70 papers collected
# - Many preprints from arXiv
# - High citation counts
# - Mix of theoretical and applied
```

**Sample Output:**

```
Papers Collected: 68
Evaluated: 65
High-Rated (≥4.0): 42
Excluded: 3

Average Scores:
Relevance: 4.7/5.0
Methodology: 4.0/5.0
Impact: 4.3/5.0

Quality: ⭐⭐ Exceptional
```

### Example 3: Interdisciplinary Research

```python
# Configuration
subject = "climate change impact on public health"
start_year = 2015
end_year = 2024
papers_per_source = 10

# Expected results:
# - Diverse methodologies
# - Multiple databases contribute
# - Mix of review and primary research
# - Geographic diversity
```

**Sample Output:**

```
Papers Collected: 38
Evaluated: 36
High-Rated (≥4.0): 18
Excluded: 2

Average Scores:
Relevance: 4.1/5.0
Methodology: 3.8/5.0
Impact: 3.5/5.0

Quality: ✅ Good
```

### Example 4: Narrow Specialization

```python
# Configuration
subject = "Langerhans Cell Histiocytosis BRAF mutations"
start_year = 2018
end_year = 2024
papers_per_source = 10

# Expected results:
# - Fewer but highly relevant papers
# - High relevance scores
# - Mix of case studies and research
# - Specialized journals
```

**Sample Output:**

```
Papers Collected: 24
Evaluated: 22
High-Rated (≥4.0): 16
Excluded: 2

Average Scores:
Relevance: 4.6/5.0
Methodology: 3.9/5.0
Impact: 3.4/5.0

Quality: ⭐ Excellent
```

-----
<a id="-deployment"></a>
## 🌐 Deployment

### Local Development

```bash
# Standard port
streamlit run streamlit_app.py

# Custom configuration
streamlit run streamlit_app.py --server.port 8080 --server.address 0.0.0.0
```

### Streamlit Cloud (Free)

1. **Prepare Repository**
   
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```
1. **Deploy**
- Visit [share.streamlit.io](https://share.streamlit.io)
- Connect GitHub account
- Select repository
- Set main file: `streamlit_app.py`
1. **Configure Secrets**
   
   ```toml
   # In Streamlit Cloud dashboard
   GOOGLE_API_KEY = "your_key_here"
   Entrez_email = "your_email@example.com"
   ```
1. **Deploy**
- Click “Deploy”
- Wait 2-5 minutes
- Access at `https://yourapp.streamlit.app`

### Docker Deployment

**Dockerfile:**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y fonts-dejavu-core

COPY requirements_streamlit.txt .
RUN pip install --no-cache-dir -r requirements_streamlit.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit_app.py"]
```

**Deploy:**

```bash
docker build -t questscholar .
docker run -d -p 8501:8501 \
  --name questscholar \
  -e GOOGLE_API_KEY="your_key" \
  -e Entrez_email="your_email" \
  questscholar
```

### AWS EC2

```bash
# Launch EC2 instance (Ubuntu 22.04)
# SSH into instance

# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv fonts-dejavu-core

# Clone repository
git clone https://github.com/yourusername/questscholar.git
cd questscholar

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_streamlit.txt

# Create env file
nano env  # Add your credentials

# Run with nohup
nohup streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &

# Configure firewall
sudo ufw allow 8501
```

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/questscholar

# Deploy
gcloud run deploy questscholar \
  --image gcr.io/PROJECT_ID/questscholar \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_key,Entrez_email=your_email
```

### Heroku

```bash
# Login
heroku login

# Create app
heroku create questscholar-app

# Set config
heroku config:set GOOGLE_API_KEY=your_key
heroku config:set Entrez_email=your_email

# Deploy
git push heroku main
```

-----
<a id="-troubleshooting"></a>
## 🔧 Troubleshooting

### Common Issues

#### Issue: “Module not found” errors

**Solution:**

```bash
pip install --upgrade -r requirements_streamlit.txt

# If still failing, try:
pip install --force-reinstall -r requirements_streamlit.txt
```

#### Issue: API Key not working

**Symptoms:**

- “GOOGLE_API_KEY not found”
- Authentication errors

**Solution:**

```bash
# Check env file exists
ls -la env

# Check file contents (hide key!)
head env

# Verify format (no spaces, no quotes)
GOOGLE_API_KEY=AIzaSyA...
Entrez_email=user@example.com

# Test in Python
python -c "import os; from dotenv import load_dotenv; load_dotenv('env'); print(os.getenv('GOOGLE_API_KEY'))"
```

#### Issue: Font errors in PDF generation

**Symptoms:**

- “TTFont not found”
- PDF generation fails

**Solution:**

```bash
# Linux
sudo apt-get update
sudo apt-get install fonts-dejavu-core

# macOS
brew install --cask font-dejavu

# Windows
# Usually pre-installed, if not:
# Download from https://dejavu-fonts.github.io/
```

#### Issue: Port already in use

**Symptoms:**

- “Port 8501 is already in use”

**Solution:**

```bash
# Find process using port
lsof -i :8501  # macOS/Linux
netstat -ano | findstr :8501  # Windows

# Kill process
kill -9 PID  # Replace PID with process ID

# Or use different port
streamlit run streamlit_app.py --server.port 8502
```

#### Issue: Slow performance

**Symptoms:**

- Long wait times
- Timeouts

**Solution:**

- Reduce papers per source (try 5 instead of 15)
- Use more recent date range (last 3-5 years)
- Check internet connection speed
- Verify API quota not exceeded
- Consider upgrading to Gemini Pro

#### Issue: Papers not evaluating

**Symptoms:**

- “0 papers evaluated”
- Missing critic scores

**Solution:**

```python
# Run diagnostic in Python
from my_tools import COLLECTED_PAPERS, CRITIC_EVALUATIONS

print(f"Collected: {len(COLLECTED_PAPERS)}")
print(f"Evaluated: {len(CRITIC_EVALUATIONS)}")

# If collected > 0 but evaluated = 0:
# Check critic agent logs for errors
# Verify Gemini Pro model access
```

### Debug Mode

Enable detailed logging:

```python
# In streamlit_app.py, add at top:
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in Streamlit interface:
if st.sidebar.checkbox("Debug Mode"):
    st.write("Session State:", st.session_state)
    st.write("Collected Papers:", len(COLLECTED_PAPERS))
    st.write("Evaluations:", len(CRITIC_EVALUATIONS))
```

### Getting Help

1. **Check logs**: Review execution logs in Streamlit interface
1. **System status**: Expand “System Status” section
1. **Documentation**: Read relevant sections above
1. **GitHub Issues**: Search for similar problems
1. **Community**: Join discussions

-----
<a id="-contributing"></a>
## 🤝 Contributing

We welcome contributions! Here’s how to get started:

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/questscholar.git
cd questscholar

# Create branch
git checkout -b feature/your-feature-name

# Install dev dependencies
pip install -r requirements_dev.txt

# Make changes and test
pytest tests/

# Submit PR
git push origin feature/your-feature-name
```

### Contribution Guidelines

**Code Style:**

- Follow PEP 8
- Use type hints
- Add docstrings
- Comment complex logic

**Testing:**

- Write unit tests for new features
- Ensure existing tests pass
- Test on multiple platforms

**Documentation:**

- Update README for new features
- Add examples
- Document API changes

**Commit Messages:**

```
feat: Add support for new database
fix: Resolve PDF generation error
docs: Update installation guide
style: Format code with black
test: Add unit tests for critic agent
```

### Areas for Contribution

- 🔍 **New data sources**: Add support for additional databases
- 🤖 **AI models**: Integrate other LLMs (Claude, GPT-4)
- 📊 **Visualizations**: Enhanced charts and graphs
- 🌐 **Internationalization**: Multi-language support
- 🎨 **UI/UX**: Interface improvements
- 📱 **Mobile**: Better mobile experience
- ⚡ **Performance**: Optimization and caching
- 🧪 **Testing**: Increase test coverage

-----
<a id="-license"></a>
## 📄 License

This project is licensed under the MIT License - see the <LICENSE> file for details.

```
MIT License

Copyright (c) 2026 QuestScholar Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

-----
<a id="-acknowledgments"></a>
## 🙏 Acknowledgments

### Technology Partners

- **[Google Gemini](https://deepmind.google/technologies/gemini/)** - AI models for evaluation
- **[Streamlit](https://streamlit.io)** - Web framework
- **[Semantic Scholar](https://www.semanticscholar.org/)** - Academic search API
- **[PubMed](https://pubmed.ncbi.nlm.nih.gov/)** - Biomedical literature database
- **[arXiv](https://arxiv.org/)** - Preprint repository
- **[OpenAlex](https://openalex.org/)** - Open scholarly data

### Libraries & Tools

- **[ReportLab](https://www.reportlab.com/)** - PDF generation
- **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)** - HTML parsing
- **[Biopython](https://biopython.org/)** - PubMed access
- **[Pillow](https://python-pillow.org/)** - Image processing

### Inspiration

This project was inspired by the need to democratize access to comprehensive literature reviews and make academic research more efficient and accessible to all.

### Contributors

Thanks to all contributors who have helped shape QuestScholar:

<a href="https://github.com/yourusername/questscholar/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yourusername/questscholar" />
  