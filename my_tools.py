#===================================================
# my_tools.py
# Enhanced with Critic Agent Support
# Jan. 10, 2026
#===================================================
import semanticscholar
from Bio import Entrez
import arxiv
import requests
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
from bs4 import BeautifulSoup
from xml.sax.saxutils import escape
import os
import json
from typing import List, Dict, Any

#===================================================
# CONFIGURATION - ADJUST THESE VALUES AS NEEDED
#===================================================
LOGO_PATH = "QuestScholar_logo.PNG"
WATERMARK_PATH = "QuestScholar_logo.PNG"
COLLECTED_PAPERS = []

# WATERMARK SETTINGS (First Page Only)
WATERMARK_OPACITY = 0.20
WATERMARK_SCALE_FACTOR = 0.75
WATERMARK_CENTERED = True
WATERMARK_X_POS = None
WATERMARK_Y_POS = None

# LOGO SETTINGS (All Pages Except First)
LOGO_WIDTH = 1.5 * cm
LOGO_HEIGHT = 1.5 * cm
LOGO_X_POS = 19.0 * cm
LOGO_Y_POS = A4[1] - 1.7 * cm
LOGO_ON_FIRST_PAGE = False

# HEADER/FOOTER SETTINGS
HEADER_LINE_COLOR = colors.darkgrey
HEADER_LINE_WIDTH = 1.5
HEADER_LINE_Y = A4[1] - 1.6 * cm

FOOTER_LINE_COLOR = colors.lightgrey
FOOTER_LINE_WIDTH = 1.5
FOOTER_LINE_Y = A4[1] - 28.0 * cm

FOOTER_FONT_SIZE = 9
FOOTER_PAGE_X = A4[0] - 1.5 * cm
FOOTER_TITLE_X = 1.5 * cm
FOOTER_Y = 1.2 * cm

#===================================================
# CRITIC EVALUATION STORAGE
#===================================================
CRITIC_EVALUATIONS = {}

# Create dummy logo if it doesn't exist
if not os.path.exists(LOGO_PATH):
    print(f"Creating dummy logo at {LOGO_PATH}...")
    try:
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (400, 200), color=(70, 130, 180))
        d = ImageDraw.Draw(img)
        d.rectangle([20, 20, 380, 180], outline=(255, 255, 255), width=3)
        d.text((180, 80), "QuestScholar", fill=(255, 255, 255))
        d.text((200, 120), "Logo", fill=(255, 255, 255))
        img.save(LOGO_PATH, 'PNG')
        print(f"Dummy logo created at {LOGO_PATH}")
    except Exception as e:
        print(f"Could not create dummy logo: {e}")

# Font Registration 
try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
    pdfmetrics.registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSans-Bold')
    DEFAULT_FONT = 'DejaVuSans'
except Exception:
    print("Warning: DejaVu fonts not found, falling back to Helvetica")
    DEFAULT_FONT = 'Helvetica'

def clean_text(text):
    if not text: 
        return "No abstract available."
    
    # First, decode HTML entities and get plain text
    text = BeautifulSoup(text, "html.parser").get_text()
    
    # Normalize Unicode characters to their closest ASCII equivalent
    import unicodedata
    text = unicodedata.normalize('NFKD', text)
    
    # Replace common problematic characters explicitly
    replacements = {
        '\u2010': '-',  # HYPHEN
        '\u2011': '-',  # NON-BREAKING HYPHEN
        '\u2012': '-',  # FIGURE DASH
        '\u2013': '-',  # EN DASH
        '\u2014': '--', # EM DASH
        '\u2015': '--', # HORIZONTAL BAR
        '\u2018': "'",  # LEFT SINGLE QUOTATION MARK
        '\u2019': "'",  # RIGHT SINGLE QUOTATION MARK
        '\u201c': '"',  # LEFT DOUBLE QUOTATION MARK
        '\u201d': '"',  # RIGHT DOUBLE QUOTATION MARK
        '\u2026': '...', # HORIZONTAL ELLIPSIS
        '\xa0': ' ',    # NON-BREAKING SPACE
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove any remaining non-ASCII characters that might cause issues
    # (optional - only if you want strictly ASCII output)
    # text = text.encode('ascii', 'ignore').decode('ascii')
    
    return escape(text)

def truncate_abstract(text, n=100):
    if not text or text == "No abstract available.": return text
    words = text.split()
    return " ".join(words[:n]) + "..." if len(words) > n else text

def reconstruct_abstract(inverted_index):
    if not inverted_index: return "No abstract available."
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions: word_positions.append((pos, word))
    word_positions.sort(key=lambda x: x[0])
    return " ".join([word for _, word in word_positions])

class SemanticScholarTool:
    def search(self, subject: str, start_year: int, end_year: int, num_papers: int) -> str:
        s2 = semanticscholar.SemanticScholar()
        try:
            results = s2.search_paper(query=subject, limit=min(num_papers*3, 100))
            count = 0
            for paper in results:
                p_year = getattr(paper, 'year', None)
                if p_year and start_year <= p_year <= end_year:
                    paper_data = {
                        'title': getattr(paper, 'title', 'Untitled'),
                        'authors': [a['name'] for a in getattr(paper, 'authors', [])] if getattr(paper, 'authors', None) else ['Unknown'],
                        'pub_year': p_year,
                        'abstract': clean_text(getattr(paper, 'abstract', '')),
                        'url': getattr(paper, 'url', 'N/A'),
                        'source': 'Semantic Scholar',
                        'citation_count': getattr(paper, 'citationCount', 0),
                        'venue': getattr(paper, 'venue', 'Unknown'),
                        'paper_id': f"ss_{count}_{p_year}"
                    }
                    COLLECTED_PAPERS.append(paper_data)
                    count += 1
                    if count >= num_papers: break
            return f"Semantic Scholar: Added {count} papers."
        except Exception as e: return f"SS Error: {str(e)}"

class PubMedTool:
    def search(self, subject: str, start_year: int, end_year: int, num_papers: int) -> str:
        Entrez.email = "researcher@example.com"
        try:
            query = f"({subject}) AND ({start_year}[pdat] : {end_year}[pdat])"
            handle = Entrez.esearch(db="pubmed", term=query, retmax=num_papers)
            id_list = Entrez.read(handle)["IdList"]
            if not id_list: return "PubMed: 0 papers added."
            handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml")
            papers = Entrez.read(handle)
            count = 0
            for paper in papers['PubmedArticle']:
                art = paper['MedlineCitation']['Article']
                pmid = paper['MedlineCitation']['PMID']
                paper_data = {
                    'title': art.get('ArticleTitle', 'Untitled'),
                    'authors': [f"{a.get('LastName','')} {a.get('Initials','')}" for a in art.get('AuthorList', [])],
                    'pub_year': art['Journal']['JournalIssue']['PubDate'].get('Year', 'N/A'),
                    'abstract': clean_text(' '.join(art.get('Abstract', {}).get('AbstractText', []))),
                    'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    'source': 'PubMed',
                    'citation_count': 0,
                    'venue': art.get('Journal', {}).get('Title', 'Unknown'),
                    'paper_id': f"pm_{pmid}"
                }
                COLLECTED_PAPERS.append(paper_data)
                count += 1
            return f"PubMed: Added {count} papers."
        except Exception as e: return f"PubMed Error: {e}"

class ArXivTool:
    def search(self, subject: str, start_year: int, end_year: int, num_papers: int) -> str:
        client = arxiv.Client()
        try:
            search = arxiv.Search(query=subject, max_results=num_papers*2)
            count = 0
            for res in client.results(search):
                if start_year <= res.published.year <= end_year:
                    paper_data = {
                        'title': res.title,
                        'authors': [a.name for a in res.authors],
                        'pub_year': res.published.year,
                        'abstract': clean_text(res.summary),
                        'url': res.entry_id,
                        'source': 'arXiv',
                        'citation_count': 0,
                        'venue': 'arXiv Preprint',
                        'paper_id': res.entry_id.split('/')[-1]
                    }
                    COLLECTED_PAPERS.append(paper_data)
                    count += 1
                    if count >= num_papers: break
            return f"arXiv: Added {count} papers."
        except Exception as e: return f"arXiv Error: {e}"

class OpenAlexTool:
    def search(self, subject: str, start_year: int, end_year: int, num_papers: int) -> str:
        try:
            r = requests.get("https://api.openalex.org/works",
                params={'search': subject, 'filter': f"publication_year:{start_year}-{end_year}", 'per_page': num_papers})
            data = r.json()
            count = 0
            for work in data.get('results', []):
                paper_data = {
                    'title': work.get('display_name'),
                    'authors': [a.get('author', {}).get('display_name') for a in work.get('authorships', [])],
                    'pub_year': work.get('publication_year'),
                    'abstract': clean_text(reconstruct_abstract(work.get('abstract_inverted_index'))),
                    'url': work.get('doi') or work.get('id'),
                    'source': 'OpenAlex',
                    'citation_count': work.get('cited_by_count', 0),
                    'venue': work.get('primary_location', {}).get('source', {}).get('display_name', 'Unknown'),
                    'paper_id': work.get('id', f"oa_{count}")
                }
                COLLECTED_PAPERS.append(paper_data)
                count += 1
            return f"OpenAlex: Added {count} papers."
        except Exception as e: return f"OpenAlex Error: {e}"

class CriticTool:
    """
    Tool for the Critic Agent to evaluate papers and provide structured assessments.
    """
    def evaluate_papers(self, evaluations: str) -> str:
        """
        Store critic evaluations for papers.
        
        Args:
            evaluations: JSON string containing list of paper evaluations
        """
        global CRITIC_EVALUATIONS
        try:
            evals = json.loads(evaluations)
            count = 0
            
            for eval_item in evals:
                title = eval_item.get('paper_title', '').lower().strip()
                
                CRITIC_EVALUATIONS[title] = {
                    'relevance_score': eval_item.get('relevance_score', 3.0),
                    'methodological_soundness': eval_item.get('methodological_soundness', 3.0),
                    'impact_score': eval_item.get('impact_score', 3.0),
                    'redundancy_flag': eval_item.get('redundancy_flag', False),
                    'flags': eval_item.get('flags', []),
                    'recommended_action': eval_item.get('recommended_action', 'include'),
                    'rationale': eval_item.get('rationale', ''),
                    'overall_score': (
                        eval_item.get('relevance_score', 3.0) * 0.4 +
                        eval_item.get('methodological_soundness', 3.0) * 0.3 +
                        eval_item.get('impact_score', 3.0) * 0.3
                    )
                }
                count += 1
            
            return f"Critic: Successfully evaluated {count} papers. Evaluations stored for aggregation."
        except json.JSONDecodeError as e:
            return f"Critic Error: Invalid JSON format - {str(e)}"
        except Exception as e:
            return f"Critic Error: {str(e)}"

    def get_papers_for_evaluation(self) -> str:
        """
        Return current paper collection in JSON format for critic evaluation.
        """
        global COLLECTED_PAPERS
        
        if not COLLECTED_PAPERS:
            return json.dumps({"error": "No papers available for evaluation"})
        
        papers_for_eval = []
        for paper in COLLECTED_PAPERS:
            papers_for_eval.append({
                'title': paper['title'],
                'authors': paper['authors'][:3],
                'pub_year': paper['pub_year'],
                'abstract': truncate_abstract(paper['abstract'], 150),
                'source': paper['source'],
                'citation_count': paper.get('citation_count', 0),
                'venue': paper.get('venue', 'Unknown')
            })
        
        return json.dumps({
            'total_papers': len(papers_for_eval),
            'papers': papers_for_eval
        }, indent=2)

    def deduplicate_collection(self) -> str:
        """
        Physically removes duplicate papers from the global COLLECTED_PAPERS list 
        based on title similarity. This should be called before the Critic phase.
        """
        global COLLECTED_PAPERS
        if not COLLECTED_PAPERS:
            return "No papers found in collection to deduplicate."

        initial_count = len(COLLECTED_PAPERS)
        unique_papers = []
        seen_titles = set()

        for paper in COLLECTED_PAPERS:
            # Normalize title: lowercase, remove non-alphanumeric, strip whitespace
            raw_title = paper.get('title', '').lower()
            clean_title = "".join(filter(str.isalnum, raw_title)).strip()
            
            if not clean_title or clean_title == "untitled":
                unique_papers.append(paper) # Keep it if we can't verify
                continue

            if clean_title not in seen_titles:
                seen_titles.add(clean_title)
                unique_papers.append(paper)
        
        # Update the global list with the cleaned version
        COLLECTED_PAPERS[:] = unique_papers
        removed = initial_count - len(unique_papers)
        
        return f"Deduplication Success: Removed {removed} duplicates. {len(unique_papers)} unique papers remain."

class PDFReportTool:
    def generate_report(self, executive_summary: str, subject: str) -> str:
        global COLLECTED_PAPERS, CRITIC_EVALUATIONS
        
        if not COLLECTED_PAPERS: 
            return "Error: Collection is empty."
        
        # Deduplicate and apply critic rankings
        unique_papers = []
        seen = set()
        
        for p in COLLECTED_PAPERS:
            key = p['title'].lower().strip()
            if key not in seen: 
                seen.add(key)
                
                if key in CRITIC_EVALUATIONS:
                    p['critic_evaluation'] = CRITIC_EVALUATIONS[key]
                    p['critic_rank'] = CRITIC_EVALUATIONS[key]['overall_score']
                    p['critic_action'] = CRITIC_EVALUATIONS[key]['recommended_action']
                else:
                    p['critic_rank'] = 3.0
                    p['critic_action'] = 'include'
                
                unique_papers.append(p)
        
        # Sort by critic ranking, then citation count
        unique_papers.sort(
            key=lambda x: (x.get('critic_rank', 0), x.get('citation_count', 0)),
            reverse=True
        )
        
        # Filter out excluded papers
        included_papers = [p for p in unique_papers if p.get('critic_action') != 'exclude']
        excluded_count = len(unique_papers) - len(included_papers)

        doc = SimpleDocTemplate("executive_summary.pdf", pagesize=A4, 
                                rightMargin=1.5*cm, leftMargin=1.5*cm, 
                                topMargin=1.5*cm, bottomMargin=2.5*cm)
        styles = getSampleStyleSheet()
        
        # Styles
        title_style = ParagraphStyle('T', parent=styles['Title'], 
                                     fontName="Helvetica-Bold", fontSize=22, 
                                     color=colors.navy, spaceAfter=20)
        h_style = ParagraphStyle('H', parent=styles['Heading2'], 
                                 fontName="Helvetica-Bold", fontSize=14, 
                                 color=colors.darkblue, spaceBefore=12)
        summary_style = ParagraphStyle('S', parent=styles['Normal'], 
                                       fontName="Helvetica", fontSize=11, 
                                       leading=14, alignment=TA_JUSTIFY)
        toc_style = ParagraphStyle('TOC', parent=styles['Normal'], 
                                   fontName="Helvetica", fontSize=10, leftIndent=15)
        bib_title_style = ParagraphStyle('BT', parent=styles['Normal'], 
                                         fontName="Helvetica-Bold", fontSize=10)
        bib_meta_style = ParagraphStyle('BM', parent=styles['Normal'], 
                                        fontName="Helvetica", fontSize=9, 
                                        textColor=colors.darkslategrey)
        critic_style = ParagraphStyle('CS', parent=styles['Normal'], 
                                      fontName="Helvetica-Bold", fontSize=9, 
                                      textColor=colors.darkgreen, leftIndent=10)
        url_style = ParagraphStyle('U', parent=styles['Normal'], 
                                   fontName="Helvetica", fontSize=8, 
                                   textColor=colors.blue)

        story = []
        
        # Title Page
        story.append(Paragraph(f"Research Report: {subject}", title_style))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", bib_meta_style))
        story.append(Spacer(1, 0.75 * cm))
        story.append(Paragraph("Executive Summary", h_style))
        story.append(Paragraph(executive_summary.replace('\n', '<br/>'), summary_style))
        
        if excluded_count > 0:
            story.append(Spacer(1, 0.5 * cm))
            stats_text = (f"<b>Quality Control:</b> {len(included_papers)} papers included, "
                         f"{excluded_count} excluded after critic evaluation.")
            story.append(Paragraph(stats_text, bib_meta_style))
        
        story.append(PageBreak())

        # TOC
        story.append(Paragraph("Table of Contents", h_style))
        for i, paper in enumerate(included_papers, 1):
            has_eval = 'critic_evaluation' in paper
            score = paper.get('critic_rank', 3.0)
            
            # Visual quality indicator
            if score >= 4.5:
                prefix = "★★ "
                score_color = "darkgreen"
            elif score >= 4.0:
                prefix = "★ "
                score_color = "darkgreen"
            else:
                prefix = ""
                score_color = "darkgrey"
            
            clean_title = paper['title'][:80].replace('[', '').replace(']', '')
            
            toc_entry = f"<a href='#paper{i}' color='black'>{i}. {prefix}<b>{clean_title}...</b></a>"
            if has_eval:
                toc_entry += f" <font color='{score_color}'>[{score:.1f}]</font>"
            
            story.append(Paragraph(toc_entry, toc_style))
        story.append(PageBreak())

        # Bibliography
        story.append(Paragraph(f"Detailed Bibliography ({len(included_papers)} Sources)", h_style))
        
        for i, paper in enumerate(included_papers, 1):
            has_eval = 'critic_evaluation' in paper
            score = paper.get('critic_rank', 3.0)
            elements = []
            
            anchor = f"<a name='paper{i}'/>"
            
            # Enhanced title with quality indicators
            if has_eval and score >= 4.5:
                title_text = f"{anchor}★★ <b>EXCEPTIONAL: {paper['title']}</b>"
            elif has_eval and score >= 4.0:
                title_text = f"{anchor}★ <b>HIGHLY RATED: {paper['title']}</b>"
            else:
                title_text = f"{anchor}<b>{i}. {paper['title']}</b>"
            
            elements.append(Paragraph(title_text, bib_title_style))
            
            # Metadata
            meta_info = f"<i>{paper['source']} | {paper['pub_year']} | {paper.get('venue', 'Unknown')}"
            if paper.get('citation_count', 0) > 0:
                meta_info += f" | Citations: {paper['citation_count']}"
            meta_info += "</i>"
            elements.append(Paragraph(meta_info, bib_meta_style))
            
            # Abstract
            elements.append(Paragraph(truncate_abstract(paper['abstract'], 100), bib_meta_style))
            
            # Critic Evaluation
            if has_eval:
                eval_data = paper['critic_evaluation']
                elements.append(Spacer(1, 0.125 * cm))
                
                # Color-coded overall score
                overall_score = eval_data.get('overall_score', 
                    (eval_data['relevance_score'] * 0.4 + 
                     eval_data['methodological_soundness'] * 0.3 + 
                     eval_data['impact_score'] * 0.3))
                
                if overall_score >= 4.5:
                    score_color = "darkgreen"
                    score_label = "EXCEPTIONAL"
                elif overall_score >= 4.0:
                    score_color = "green"
                    score_label = "EXCELLENT"
                elif overall_score >= 3.5:
                    score_color = "darkorange"
                    score_label = "GOOD"
                else:
                    score_color = "darkgrey"
                    score_label = "ACCEPTABLE"
                
                eval_text = (f"<b><font color='{score_color}'>● Critic Assessment [{score_label}: {overall_score:.2f}/5.0]</font></b><br/>"
                           f"Relevance: {eval_data['relevance_score']:.1f} | "
                           f"Methodology: {eval_data['methodological_soundness']:.1f} | "
                           f"Impact: {eval_data['impact_score']:.1f}<br/>"
                           f"<i>{eval_data['rationale']}</i>")
                
                if eval_data['flags']:
                    eval_text += f"<br/><b>Tags:</b> {', '.join(eval_data['flags'])}"
                
                elements.append(Paragraph(eval_text, critic_style))
            
            elements.append(Paragraph(f"URL: {paper['url']}", url_style))
            elements.append(Spacer(1, 0.65 * cm))
            story.append(KeepTogether(elements))

        def add_first_page_elements(canvas_obj, doc):
            """FIXED: Properly balanced saveState/restoreState calls"""
            canvas_obj.saveState()
            w, h = doc.pagesize
            
            # Watermark
            try:
                watermark_img = Image.open(WATERMARK_PATH)
                # Create nested state for alpha manipulation
                canvas_obj.saveState()
                canvas_obj.setFillAlpha(WATERMARK_OPACITY)
                
                img_width, img_height = watermark_img.size
                new_width = w * WATERMARK_SCALE_FACTOR
                new_height = (img_height / img_width) * new_width
                
                if WATERMARK_CENTERED:
                    x_pos = (w - new_width) / 2
                    y_pos = (h - new_height) / 2
                else:
                    x_pos = WATERMARK_X_POS if WATERMARK_X_POS is not None else (w - new_width) / 2
                    y_pos = WATERMARK_Y_POS if WATERMARK_Y_POS is not None else (h - new_height) / 2
                
                canvas_obj.drawImage(ImageReader(watermark_img), x_pos, y_pos, 
                               width=new_width, height=new_height,
                               preserveAspectRatio=True, mask='auto')
                watermark_img.close()
                canvas_obj.restoreState()  # Restore the nested state
            except Exception as e:
                print(f"Warning: Could not load watermark: {e}")
            
            # Header/Footer
            canvas_obj.setStrokeColor(HEADER_LINE_COLOR)
            canvas_obj.setLineWidth(HEADER_LINE_WIDTH)
            canvas_obj.line(1.5*cm, HEADER_LINE_Y, w-1.5*cm, HEADER_LINE_Y)
            
            canvas_obj.setStrokeColor(FOOTER_LINE_COLOR)
            canvas_obj.setLineWidth(FOOTER_LINE_WIDTH)
            canvas_obj.line(1.5*cm, FOOTER_LINE_Y, w-1.5*cm, FOOTER_LINE_Y)
            
            canvas_obj.setFont("Helvetica", FOOTER_FONT_SIZE)
            canvas_obj.setFillColor(colors.black)
            canvas_obj.drawRightString(FOOTER_PAGE_X, FOOTER_Y, f"Page {canvas_obj.getPageNumber()}")
            canvas_obj.drawString(FOOTER_TITLE_X, FOOTER_Y, f"QuestScholar Research: {subject[:45]}")
            
            canvas_obj.restoreState()

        def add_later_pages_elements(canvas_obj, doc):
            """FIXED: Properly balanced saveState/restoreState calls"""
            canvas_obj.saveState()
            w, h = doc.pagesize
            
            # Logo
            try:
                logo_img = Image.open(LOGO_PATH)
                canvas_obj.drawImage(ImageReader(logo_img), LOGO_X_POS, LOGO_Y_POS, 
                               width=LOGO_WIDTH, height=LOGO_HEIGHT, 
                               preserveAspectRatio=True, mask='auto')
                logo_img.close()
            except Exception as e:
                print(f"Warning: Could not load logo: {e}")
            
            # Header/Footer
            canvas_obj.setStrokeColor(HEADER_LINE_COLOR)
            canvas_obj.setLineWidth(HEADER_LINE_WIDTH)
            canvas_obj.line(1.5*cm, HEADER_LINE_Y, w-1.5*cm, HEADER_LINE_Y)
            
            canvas_obj.setStrokeColor(FOOTER_LINE_COLOR)
            canvas_obj.setLineWidth(FOOTER_LINE_WIDTH)
            canvas_obj.line(1.5*cm, FOOTER_LINE_Y, w-1.5*cm, FOOTER_LINE_Y)
            
            canvas_obj.setFont("Helvetica", FOOTER_FONT_SIZE)
            canvas_obj.setFillColor(colors.black)
            canvas_obj.drawRightString(FOOTER_PAGE_X, FOOTER_Y, f"Page {canvas_obj.getPageNumber()}")
            canvas_obj.drawString(FOOTER_TITLE_X, FOOTER_Y, f"QuestScholar Research: {subject[:45]}")
            
            canvas_obj.restoreState()

        doc.build(story, onFirstPage=add_first_page_elements, onLaterPages=add_later_pages_elements)
        
        summary_msg = f"PDF Generated: executive_summary.pdf ({len(included_papers)} papers"
        if excluded_count > 0:
            summary_msg += f", {excluded_count} excluded by critic"
        summary_msg += ")"
        
        return summary_msg

def clear_papers():
    global COLLECTED_PAPERS, CRITIC_EVALUATIONS
    COLLECTED_PAPERS = []
    CRITIC_EVALUATIONS = {}
    return "Library and evaluations cleared."

class HTMLReportTool:
    """
    Generates interactive HTML report with download functionality.
    Replaces or complements the PDF report generation.
    """
    
    def generate_html_report(self, executive_summary: str, subject: str) -> str:
        global COLLECTED_PAPERS, CRITIC_EVALUATIONS
        
        if not COLLECTED_PAPERS:
            return "Error: Collection is empty."
        
        # Deduplicate and apply critic rankings
        unique_papers = []
        seen = set()
        
        for p in COLLECTED_PAPERS:
            key = p['title'].lower().strip()
            if key not in seen:
                seen.add(key)
                
                if key in CRITIC_EVALUATIONS:
                    p['critic_evaluation'] = CRITIC_EVALUATIONS[key]
                    p['critic_rank'] = CRITIC_EVALUATIONS[key]['overall_score']
                    p['critic_action'] = CRITIC_EVALUATIONS[key]['recommended_action']
                else:
                    p['critic_rank'] = 3.0
                    p['critic_action'] = 'include'
                
                unique_papers.append(p)
        
        # Sort by critic ranking, then citation count
        unique_papers.sort(
            key=lambda x: (x.get('critic_rank', 0), x.get('citation_count', 0)),
            reverse=True
        )
        
        # Filter out excluded papers
        included_papers = [p for p in unique_papers if p.get('critic_action') != 'exclude']
        excluded_count = len(unique_papers) - len(included_papers)
        
        # Generate HTML
        html_content = self._generate_html(
            subject=subject,
            executive_summary=executive_summary,
            papers=included_papers,
            excluded_count=excluded_count
        )
        
        # Write to file
        with open('executive_summary.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        summary_msg = f"HTML Generated: executive_summary.html ({len(included_papers)} papers"
        if excluded_count > 0:
            summary_msg += f", {excluded_count} excluded by critic"
        summary_msg += ")"
        
        return summary_msg
    
    def _generate_html(self, subject: str, executive_summary: str, 
                       papers: list, excluded_count: int) -> str:
        """Generate complete HTML document"""
        
        # Calculate statistics
        high_rated = sum(1 for p in papers if p.get('critic_rank', 0) >= 4.0)
        exceptional = sum(1 for p in papers if p.get('critic_rank', 0) >= 4.5)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Report: {self._escape_html(subject)}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .header .date {{
            margin-top: 10px;
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .stats-bar {{
            display: flex;
            justify-content: space-around;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
            flex-wrap: wrap;
        }}
        
        .stat {{
            text-align: center;
            padding: 10px;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .executive-summary {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            font-size: 1.05em;
            line-height: 1.8;
        }}
        
        .paper-card {{
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 25px;
            transition: all 0.3s ease;
            position: relative;
        }}
        
        .paper-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        .paper-rank {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: #667eea;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        
        .paper-rank.exceptional {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        
        .paper-rank.excellent {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        .paper-rank.good {{
            background: #f39c12;
        }}
        
        .paper-title {{
            font-size: 1.4em;
            color: #2c3e50;
            margin-bottom: 12px;
            padding-right: 100px;
            font-weight: 600;
            line-height: 1.4;
        }}
        
        .paper-meta {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-bottom: 15px;
            font-size: 0.9em;
            color: #666;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .meta-icon {{
            font-weight: bold;
        }}
        
        .paper-abstract {{
            color: #555;
            line-height: 1.7;
            margin-bottom: 15px;
            text-align: justify;
        }}
        
        .critic-evaluation {{
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin-top: 15px;
            border-radius: 4px;
        }}
        
        .critic-scores {{
            display: flex;
            gap: 15px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }}
        
        .score-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .score-bar {{
            width: 60px;
            height: 8px;
            background: #ddd;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .score-fill {{
            height: 100%;
            background: #4caf50;
            transition: width 0.3s ease;
        }}
        
        .critic-rationale {{
            font-style: italic;
            color: #555;
            margin-top: 10px;
        }}
        
        .tags {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 10px;
        }}
        
        .tag {{
            background: #e3f2fd;
            color: #1976d2;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .download-section {{
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #e9ecef;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.95em;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }}
        
        .btn-primary {{
            background: #667eea;
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #5568d3;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-secondary {{
            background: #f8f9fa;
            color: #495057;
            border: 1px solid #dee2e6;
        }}
        
        .btn-secondary:hover {{
            background: #e9ecef;
        }}
        
        .download-status {{
            display: none;
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        
        .download-status.success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        
        .download-status.error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        
        .download-status.loading {{
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }}
        
        .toc {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        
        .toc-item {{
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .toc-item:last-child {{
            border-bottom: none;
        }}
        
        .toc-link {{
            color: #667eea;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.2s ease;
        }}
        
        .toc-link:hover {{
            color: #5568d3;
            padding-left: 10px;
        }}
        
        .quality-badge {{
            font-size: 0.8em;
            padding: 2px 8px;
            border-radius: 10px;
            font-weight: bold;
        }}
        
        .quality-exceptional {{
            background: #d4edda;
            color: #155724;
        }}
        
        .quality-excellent {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
            }}
            
            .download-section {{
                display: none;
            }}
            
            .paper-card {{
                page-break-inside: avoid;
            }}
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .stats-bar {{
                flex-direction: column;
            }}
            
            .paper-rank {{
                position: static;
                display: inline-block;
                margin-bottom: 10px;
            }}
            
            .paper-title {{
                padding-right: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 Research Report</h1>
            <div class="subtitle">{self._escape_html(subject)}</div>
            <div class="date">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
        </div>
        
        <div class="stats-bar">
            <div class="stat">
                <div class="stat-value">{len(papers)}</div>
                <div class="stat-label">Papers Included</div>
            </div>
            <div class="stat">
                <div class="stat-value">{exceptional}</div>
                <div class="stat-label">Exceptional (≥4.5)</div>
            </div>
            <div class="stat">
                <div class="stat-value">{high_rated}</div>
                <div class="stat-label">Highly Rated (≥4.0)</div>
            </div>
            {f'<div class="stat"><div class="stat-value">{excluded_count}</div><div class="stat-label">Excluded</div></div>' if excluded_count > 0 else ''}
        </div>
        
        <div class="content">
            <div class="section">
                <h2 class="section-title">📋 Executive Summary</h2>
                <div class="executive-summary">
                    {self._format_text(executive_summary)}
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">📑 Table of Contents</h2>
                <div class="toc">
                    {self._generate_toc(papers)}
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">📚 Detailed Bibliography</h2>
                {self._generate_papers_html(papers)}
            </div>
        </div>
    </div>
    
    <script>
        {self._generate_javascript()}
    </script>
</body>
</html>"""

    def _generate_toc(self, papers: list) -> str:
        """Generate table of contents"""
        toc_html = ""
        for i, paper in enumerate(papers, 1):
            score = paper.get('critic_rank', 3.0)
            title = self._escape_html(paper['title'][:80])
            
            quality_badge = ""
            if score >= 4.5:
                quality_badge = '<span class="quality-badge quality-exceptional">★★ Exceptional</span>'
            elif score >= 4.0:
                quality_badge = '<span class="quality-badge quality-excellent">★ Excellent</span>'
            
            toc_html += f'''
                <div class="toc-item">
                    <a href="#paper{i}" class="toc-link">
                        <span><strong>{i}.</strong> {title}...</span>
                        {quality_badge}
                        <span style="margin-left: auto; color: #999;">[{score:.1f}]</span>
                    </a>
                </div>
            '''
        
        return toc_html
    
    def _generate_papers_html(self, papers: list) -> str:
        """Generate HTML for all papers"""
        papers_html = ""
        
        for i, paper in enumerate(papers, 1):
            score = paper.get('critic_rank', 3.0)
            has_eval = 'critic_evaluation' in paper
            
            # Determine rank class
            rank_class = "good"
            rank_label = f"{score:.1f}/5.0"
            if score >= 4.5:
                rank_class = "exceptional"
                rank_label = f"★★ {score:.1f}/5.0"
            elif score >= 4.0:
                rank_class = "excellent"
                rank_label = f"★ {score:.1f}/5.0"
            
            # Build paper card
            papers_html += f'''
            <div class="paper-card" id="paper{i}">
                <div class="paper-rank {rank_class}">{rank_label}</div>
                
                <h3 class="paper-title">{i}. {self._escape_html(paper['title'])}</h3>
                
                <div class="paper-meta">
                    <div class="meta-item">
                        <span class="meta-icon">📖</span>
                        <span>{self._escape_html(paper['source'])}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-icon">📅</span>
                        <span>{paper['pub_year']}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-icon">🏛️</span>
                        <span>{self._escape_html(paper.get('venue', 'Unknown'))}</span>
                    </div>
                    {f'<div class="meta-item"><span class="meta-icon">📊</span><span>{paper["citation_count"]} citations</span></div>' if paper.get('citation_count', 0) > 0 else ''}
                    <div class="meta-item">
                        <span class="meta-icon">✍️</span>
                        <span>{self._escape_html(", ".join(paper['authors'][:3]))}{" et al." if len(paper['authors']) > 3 else ""}</span>
                    </div>
                </div>
                
                <div class="paper-abstract">
                    {self._format_text(truncate_abstract(paper['abstract'], 100))}
                </div>
            '''
            
            # Add critic evaluation if available
            if has_eval:
                eval_data = paper['critic_evaluation']
                papers_html += f'''
                <div class="critic-evaluation">
                    <strong style="color: #2e7d32;">🎯 Critic Assessment</strong>
                    <div class="critic-scores">
                        {self._generate_score_bar("Relevance", eval_data['relevance_score'])}
                        {self._generate_score_bar("Methodology", eval_data['methodological_soundness'])}
                        {self._generate_score_bar("Impact", eval_data['impact_score'])}
                    </div>
                    <div class="critic-rationale">
                        {self._escape_html(eval_data['rationale'])}
                    </div>
                    {self._generate_tags(eval_data.get('flags', []))}
                </div>
                '''
            
            # Add download section
            papers_html += self._generate_download_section(paper, i)
            
            papers_html += "</div>"
        
        return papers_html
    
    def _generate_score_bar(self, label: str, score: float) -> str:
        """Generate visual score bar"""
        percentage = (score / 5.0) * 100
        return f'''
        <div class="score-item">
            <span style="min-width: 90px; font-size: 0.85em;">{label}:</span>
            <div class="score-bar">
                <div class="score-fill" style="width: {percentage}%"></div>
            </div>
            <span style="font-weight: bold; font-size: 0.9em;">{score:.1f}</span>
        </div>
        '''
    
    def _generate_tags(self, flags: list) -> str:
        """Generate tag badges"""
        if not flags:
            return ""
        
        tags_html = '<div class="tags">'
        for flag in flags:
            tags_html += f'<span class="tag">{self._escape_html(flag.replace("_", " ").title())}</span>'
        tags_html += '</div>'
        return tags_html
    
    def _generate_download_section(self, paper: dict, index: int) -> str:
        """Generate download buttons and status area"""
        source = paper['source']
        url = paper.get('url', '')
        paper_id = paper.get('paper_id', f'paper_{index}')
        
        # Determine if we can attempt PDF download
        can_download = False
        pdf_url = ""
        
        if source == 'arXiv' and 'arxiv.org/abs/' in url:
            can_download = True
            pdf_url = url.replace('/abs/', '/pdf/') + '.pdf'
        elif source == 'PubMed':
            # PMC open access - users can try
            can_download = True
            pdf_url = url  # Will attempt via CORS proxy
        
        download_btn = ""
        if can_download:
            safe_title = self._escape_html(paper['title'][:50]).replace("'", "\\'")
            download_btn = f'''
                <button class="btn btn-primary" onclick="downloadPDF('{pdf_url}', '{safe_title}', 'status_{index}', '{source}')">
                    ⬇️ Download PDF
                </button>
            '''
        
        return f'''
        <div class="download-section">
            {download_btn}
            <a href="{self._escape_html(url)}" target="_blank" class="btn btn-secondary">
                🔗 View Source
            </a>
            <button class="btn btn-secondary" onclick="copyBibTeX('{index}')">
                📋 Copy Citation
            </button>
        </div>
        <div id="status_{index}" class="download-status"></div>
        <textarea id="bibtex_{index}" style="display:none;">{self._generate_bibtex(paper, index)}</textarea>
        '''
    
    def _generate_bibtex(self, paper: dict, index: int) -> str:
        """Generate BibTeX citation"""
        source = paper['source']
        authors = " and ".join(paper['authors'][:5])
        title = paper['title']
        year = paper['pub_year']
        venue = paper.get('venue', 'Unknown')
        
        return f'''@article{{paper{index},
  author = {{{authors}}},
  title = {{{title}}},
  year = {{{year}}},
  journal = {{{venue}}},
  source = {{{source}}}
}}'''
    
    def _generate_javascript(self) -> str:
        """Generate JavaScript for interactive features"""
        return '''
        // Download PDF function
        async function downloadPDF(url, title, statusId, source) {
            const statusEl = document.getElementById(statusId);
            statusEl.className = 'download-status loading';
            statusEl.style.display = 'block';
            statusEl.textContent = '⏳ Attempting download...';
            
            try {
                // For arXiv, direct download works
                if (source === 'arXiv') {
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = sanitizeFilename(title) + '.pdf';
                    link.target = '_blank';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    statusEl.className = 'download-status success';
                    statusEl.textContent = '✅ Download initiated! Check your downloads folder.';
                    setTimeout(() => { statusEl.style.display = 'none'; }, 5000);
                    return;
                }
                
                // For other sources, attempt fetch with CORS proxy
                const proxyUrl = 'https://corsproxy.io/?' + encodeURIComponent(url);
                const response = await fetch(proxyUrl);
                
                if (!response.ok) {
                    throw new Error('PDF not available via direct download');
                }
                
                const blob = await response.blob();
                const blobUrl = window.URL.createObjectURL(blob);
                
                const link = document.createElement('a');
                link.href = blobUrl;
                link.download = sanitizeFilename(title) + '.pdf';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                window.URL.revokeObjectURL(blobUrl);
                
                statusEl.className = 'download-status success';
                statusEl.textContent = '✅ Download complete!';
                setTimeout(() => { statusEl.style.display = 'none'; }, 5000);
                
            } catch (error) {
                statusEl.className = 'download-status error';
                statusEl.innerHTML = `❌ Direct download failed. <a href="${url}" target="_blank" style="color: #721c24; text-decoration: underline;">Open in new tab</a> to download manually.`;
                setTimeout(() => { statusEl.style.display = 'none'; }, 10000);
            }
        }
        
        // Sanitize filename
        function sanitizeFilename(name) {
            return name.replace(/[^a-z0-9]/gi, '_').substring(0, 50);
        }
        
        // Copy BibTeX citation
        function copyBibTeX(index) {
            const textarea = document.getElementById('bibtex_' + index);
            const statusEl = document.getElementById('status_' + index);
            
            textarea.style.display = 'block';
            textarea.select();
            document.execCommand('copy');
            textarea.style.display = 'none';
            
            statusEl.className = 'download-status success';
            statusEl.style.display = 'block';
            statusEl.textContent = '✅ Citation copied to clipboard!';
            setTimeout(() => { statusEl.style.display = 'none'; }, 3000);
        }
        
        // Smooth scroll for TOC links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
        '''
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not text:
            return ""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
    
    def _format_text(self, text: str) -> str:
        """Format text with paragraphs"""
        if not text:
            return ""
        
        paragraphs = text.split('\n\n')
        formatted = ""
        for para in paragraphs:
            para = para.strip()
            if para:
                # Replace single newlines with spaces
                para = para.replace('\n', ' ')
                formatted += f"<p>{self._escape_html(para)}</p>"
        
        return formatted if formatted else f"<p>{self._escape_html(text)}</p>"