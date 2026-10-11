# LangChain Multi-Agent Research System

A powerful multi-agent research system built with LangChain that autonomously researches topics, gathers information, writes comprehensive reports, and evaluates their quality using AI-powered agents.

<p align="center">
  <strong> Research Automation •  Multi-Agent Orchestration •  Intelligent Report Generation</strong>
</p>

---

##  Features

- **Multi-Agent Architecture**: Specialized agents for searching, reading, writing, and critiquing
- **Automated Web Research**: Intelligent web search with Tavily API
- **Smart Content Extraction**: Advanced web scraping with multiple fallback strategies
- **Hybrid Research Engine**: Combines broad web context (top 5 search snippets) with deep evidence extraction (top 2 full articles) to prevent LLM hallucination and token overflow.
- **Algorithmic Relevance Scoring**: Automatically ranks search results using Tavily's mathematical scoring to guarantee the Reader Agent only scrapes the highest-quality primary sources.
- **AI-Powered Report Generation**: Automatically generates structured research reports
- **Quality Evaluation**: Built-in critic agent for report validation and scoring
- **Interactive UI**: Streamlit-based user interface for easy interaction
- **Pipeline Orchestration**: Seamless coordination of multiple agents

---

##  Architecture

```
┌─────────────────────────────────────────────────────┐
│           Streamlit UI (app.py)                     │
│      Multi-Agent Research Assistant Interface       │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│      Research Pipeline (pipeline.py)                │
│        Orchestrates multi-agent workflow            │
└──────────────────┬──────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼───┐    ┌────▼─────┐   ┌───▼────┐
│Search │    │   Reader  │   │ Writer │
│Agent  │    │   Agent   │   │ Chain  │
└───┬───┘    └────┬─────┘   └───┬────┘
    │             │             │
    │  ┌──────────▼─────────┐   │
    └─▶│  Tools Layer       │◀──┘
       │                    │
       │ • web_search      │
       │ • scrape_url      │
       │                    │
       └────────┬───────────┘
                │
            ┌───▼────────┐
            │ Critic     │
            │ Chain      │
            └────────────┘
```

### Agent Responsibilities

- **Search Agent**: Queries the web using Tavily, mathematically scores and ranks results, and isolates the top target URLs for deep reading.
- **Reader Agent**: Autonomously extracts and synthesizes full-page text specifically from the highest-scoring target URLs.
- **Writer Chain**: Composes structured, professional research reports
- **Critic Chain**: Evaluates reports and provides improvement suggestions

---

##  Technologies Used

| Technology | Purpose |
|-----------|---------|
| **LangChain** | Multi-agent orchestration and chain management |
| **Groq(OpenAI-GPT-OSS-20B)** | Language model for agents and chains |
| **Streamlit** | Interactive web UI |
| **Tavily API** | Web search and information retrieval |
| **BeautifulSoup4** | HTML parsing and content extraction |
| **Trafilatura** | Web content extraction |
| **Readability-lxml** | Article content extraction |
| **Python-dotenv** | Environment configuration management |
| **Rich** | Terminal output formatting |

---

##  Prerequisites

- Python 3.14.7 or higher
- Groq API Key
- Tavily API Key

---

##  Installation

### 1. Clone the Repository

```bash
git clone https://github.com/shubhamkx34/LangChain-Multi-Agent-Research-System.git
```

### 2. Create Environment (Conda)

```bash
conda create -n langagent python=3.14.7 -y
conda activate langagent

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

##  Usage

### Run with Streamlit UI (Recommended)

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

### Run as a Script

```bash
python main.py

```

##  Project Structure

```
.
├── app.py                      # Streamlit web interface
├── main.py                     # CLI entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── LICENSE                     # License file
├── demo.excalidraw            # Architecture diagram
│
└── src/
    ├
    ├──agents/
    │      └── agents.py  # Search, Reader, Writer, Critic agents
    │           
    ├── tools/
    │      └── tools.py            # web_search, scrape_url tools
    │  
    └── pipelines/
           └── pipeline.py         # Main research orchestration
        
```

---

## 🔄 Workflow

1. **User Input**: Enter a research topic via UI or script
2. **Search Phase**: Search agent queries Tavily, scores results (0-1), and separates the top URLs from broad snippets.
3. **Reading Phase**: Reader agent extracts and summarizes deep content exclusively from the top 2 ranked URLs.
4. **Writing Phase**: Writer chain synthesizes the broad snippets and deep scraped text into a unified, structured report.
5. **Review Phase**: Critic chain evaluates the report and provides scores
6. **Output**: Display final report with feedback and scores

---

## 📊 Example Output

The system generates reports with:
- Comprehensive introduction and background
- Key findings with detailed explanations
- Well-sourced conclusions
- Structured sections and proper formatting
- Quality scores from 1-10


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
