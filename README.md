# Multi-Agent Research Assistant

A Streamlit application that turns a research topic into a structured report with web sources and a separate critique. The workflow combines two tool-using LangGraph agents with LangChain writing and review chains, using Tavily for search and Mistral for language generation.

## How a request moves through the system

| Stage | Implementation | Output |
| --- | --- | --- |
| 1. Search | A ReAct agent calls `web_search`, which requests up to five Tavily results and formats their titles, URLs, and short snippets. | Search summary and source URLs |
| 2. Read | A second ReAct agent receives the first 800 characters of that summary, chooses one URL, and calls `scrape_url` to extract page text with Requests and Beautiful Soup. | Up to 3,000 characters of cleaned page text |
| 3. Write | A Mistral-backed prompt chain combines the search summary and extracted text to draft an introduction, at least three key findings, a conclusion, and a sources section. | Markdown-style research report |
| 4. Critique | A separate prompt chain reviews the draft and returns a score out of 10, strengths, areas to improve, and a verdict. | Feedback shown alongside the report |

The stages run **sequentially**. A Python `state` dictionary carries `search_results`, `scraped_content`, `report`, and `feedback` between them. The critic evaluates the draft once; it does not automatically rewrite or approve it.

## What the app provides

- Enter a topic and run the research workflow from a Streamlit form.
- Inspect the report, critique, search output, extracted page text, and run logs in separate tabs.
- Download the generated report as a Markdown file.
- Revisit previous runs during the current Streamlit session or clear that session history.
- Run the same pipeline from a terminal with `python pipeline.py`.

The app is a research **drafting aid**. Its source list is generated from search context, and the critique is an LLM response rather than an independent fact-check. Verify important claims against the linked sources before using a report.

## Tech stack

**Python · LangGraph · LangChain · Mistral (`mistral-small-latest`) · Tavily · Requests · Beautiful Soup · Streamlit**

The search and reader agents are created with LangGraph's `create_react_agent`. Writer and critic are LangChain prompt → model → string-parser chains. See [`agents.py`](agents.py), [`tools.py`](tools.py), and [`pipeline.py`](pipeline.py) for the respective components.

## Run locally

1. Clone the repository and install dependencies:

   ```bash
   git clone https://github.com/PriyanshuSharmapixel/Autonomous-Multi-Agent-AI-Research-System.git
   cd Autonomous-Multi-Agent-AI-Research-System
   python -m venv .venv
   # Activate .venv for your shell, then:
   python -m pip install -r requirements.txt
   ```

2. Provide `MISTRAL_API_KEY` and `TAVILY_API_KEY` as environment variables in your local environment. The project loads environment variables with `python-dotenv`; keep credentials out of commits. An internet connection and access to both APIs are required.
3. Start the web interface:

   ```bash
   streamlit run app.py
   ```

   Alternatively, run `python pipeline.py` and enter a topic at the prompt. The terminal path prints each stage's output but does not provide the Streamlit history or download button.

## Repository map

| File | Responsibility |
| --- | --- |
| [`app.py`](app.py) | Streamlit form, progress display, session history, result tabs, and Markdown download |
| [`pipeline.py`](pipeline.py) | Sequential orchestration and shared result state |
| [`agents.py`](agents.py) | Mistral client, search and reader agents, writer and critic prompts |
| [`tools.py`](tools.py) | Tavily search and single-page HTML text extraction |
| [`requirements.txt`](requirements.txt) | Python dependencies |

## Current scope and next steps

- Each Tavily search tool call requests **at most five results**. The reader is prompted to select **one** page for deeper extraction. Sites that block scraping or return limited content can reduce report quality.
- The search phase returns an error when it fails. A scrape failure is retained as a message so the writer can still proceed with the search summary.
- The critic's score is displayed as text; there is no threshold, structured score parsing, source verification, or revision loop.
- The repository does not include a benchmark dataset or recorded evaluation results. Runtime and score claims should be added only after repeatable testing.

Useful next improvements are structured source records, per-claim citations, evaluation against a small set of manually reviewed topics, and a revision step that responds to critic feedback.
