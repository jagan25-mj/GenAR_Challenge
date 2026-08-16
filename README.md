# PADER AI System (Version 0)

This repository contains Version 0 of the PADER AI System, built for the GenAR AI Engineering Challenge.

## How to Run
1. Ensure Python 3 is installed.
2. Create and activate a virtual environment: `python -m venv venv` and `.\venv\Scripts\activate` (Windows).
3. Install dependencies: `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and insert your Gemini API Key (`GEMINI_API_KEY`).
5. Run the orchestrator: `python main.py`.
6. The generated report will be saved to `PADER_Report.md`.

## Architecture & AI vs. Deterministic Split
The system strictly separates data aggregation from text generation to prevent hallucination and ensure evidence traceablility:
- **Deterministic Code (`analyzer.py`)**: Uses `pandas` to read the raw data, deduplicate on `safetyreportid`, and compute exact figures (case counts, demographics, top reactions).
- **Context Assembly (`prompts.py`)**: Injects the exact figures from the analyzer into predefined prompt templates, creating a scoped "packet" for the LLM.
- **AI Code (`generator.py`)**: Uses the `gemini-2.5-flash` model with a temperature of 0.0 to generate a neutral, regulatory narrative based purely on the prompt packet. The AI does zero data analysis.

## Key Prompts & Design Decisions
The `SYSTEM_PROMPT` enforces regulatory behavior:
> ONLY state what the data supports. Do NOT invent, hallucinate, or assume any facts. Do NOT make medical conclusions. Keep the tone neutral, professional, and regulatory.

The most critical design decision was **preventing the LLM from touching raw data or doing math**. It only sees the final numbers. For instance, the LLM receives: `Total cases: 1024, Serious cases: 1023`. It is then instructed to write a summary of those exact figures.

## Known Limitations
- The current implementation hardcodes logic for Bisoprolol.
- Some fields like "History of Actions" are deterministically stubbed because the dataset lacks them.
- Deduplication is strictly by `safetyreportid`. More complex real-world deduplication logic (e.g., initial vs follow-up reports) is not implemented.
