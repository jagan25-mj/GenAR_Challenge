# GenAR AI Engineering Challenge - PADER System

This repository contains the upgraded **Version 1** architecture of the PADER AI System, built for the GenAR AI Engineering Challenge. It features a fully config-driven pipeline, dynamic evidence routing, and an automated grounding evaluator.

---

## 1. How do I run it?

**Setup Requirements:** Python 3.10+
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate   # (Windows)
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your API key: Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`.
4. Run the main pipeline (generates `PADER_Report.md` and `audit_log.json`):
   ```bash
   python main.py
   ```
5. *(Optional)* Run the stress test suite (tests Reusability, Hallucinations, and Empty Data):
   ```bash
   python run_tests.py
   ```

---

## 2. What's the architecture?

The pipeline is completely configuration-driven (see `architecture_diagram.mermaid`):
1. **Config Loader**: Reads `config/reports.yaml` to determine the report structure and data requirements.
2. **Data Analyzer**: Reads the raw CSV and deterministically calculates math/metrics.
3. **Evidence Builder**: Acts as a strict router. It pulls *only* the specific data fields requested by the YAML config and packages them into a JSON evidence payload for a specific section.
4. **AI Generator**: Takes the instructions and the evidence payload to write the narrative section.
5. **Grounding Evaluator**: Scans the generated text, extracts all numbers, and verifies they exist in the original evidence payload.

---

## 3. Where is AI used vs. deterministic code, and why that split?

We adhere to a strict separation of concerns to prevent hallucinations:
*   **Deterministic Code (`analyzer.py`, `evidence_builder.py`, `evaluator.py`)**: All math, data aggregation, filtering, and post-generation evaluation are purely deterministic. LLMs are historically bad at exact math, so they are never given the raw dataset.
*   **AI Code (`generator.py`)**: The AI (`gemini-3.5-flash` at Temperature `0.0`) is used **strictly for natural language generation**. It receives pre-calculated facts (e.g., `Total cases: 1024`) and simply translates them into professional regulatory prose.

---

## 4. What are the actual prompts/context templates your system assembles?

All prompts are highly decoupled and stored in `config/reports.yaml`. 
Here is the core **System Prompt** applied to all PADER requests:

> "You are an expert regulatory safety writer assisting with the drafting of a safety report.
> STRICT RULES:
> 1. ONLY state what the data supports. Do NOT invent, hallucinate, or assume any facts.
> 2. If a number says '1024 cases', write '1,024 cases'.
> 3. Do NOT make medical conclusions (e.g., do not say 'this is a confirmed safety signal'). State observations objectively.
> 4. Keep the tone neutral, professional, and regulatory.
> 5. Do not include markdown headers (like # or ##) in your response. Just write the paragraph text."

For each section, a dynamic packet is assembled:
```text
Instructions: <Specific instruction from YAML, e.g., 'Summarize the serious cases'>
Evidence payload: <JSON dict of purely the scoped data, e.g., {"serious_cases_count": 1023}>
```

---

## 5. How does the system stay grounded?

We use a two-pronged approach to ensure sentences are backed by data:
1. **Preventative (Scoped Evidence)**: The `EvidenceBuilder` strictly scopes the data. If the AI is writing the "Demographics" section, it is *only* given demographic data, preventing it from accidentally referencing adverse reactions.
2. **Reactive (Automated Evaluation)**: `evaluator.py` runs a regex engine over the generated text. It extracts every single number the AI generated and verifies it against the provided evidence packet. If the AI hallucinates a number, it is instantly caught and flagged in the `audit_log.json`.

---

## 6. How would you evaluate this at scale (1,000 generated reports, not one)?

1. **Automated CI/CD Evaluator Pipeline**: Because our `evaluator.py` runs completely programmatically, we would run it across all 1,000 reports and generate a dashboard of "Hallucination Scores". Any report with a flagged number is automatically halted from publishing.
2. **Adversarial Regression Testing**: We would maintain a suite of test cases (like the `ADVERSARIAL_TEST` and `SIGNAL_SNAPSHOT` seen in `run_tests.py`) that run on every commit to ensure the pipeline handles empty data, malicious prompts, and API timeouts gracefully.
3. **Human-in-the-Loop Web Dashboard**: For scale, we wouldn't use a CLI. We would wrap this Python backend in a React/FastAPI web interface, allowing reviewers to visually side-by-side compare the generated text against the strict evidence payload for a 5% randomized sample of reports.

---

## 7. What are the known limitations?

1. **Simple Deduplication**: The deterministic analyzer currently deduplicates strictly by `safetyreportid`. In the real world, we would need to handle follow-up reports vs. initial reports based on version dates.
2. **Dictionary NLP Limitations**: The `evaluator.py` currently ensures *numbers* are grounded. If the AI hallucinates a *word* (e.g., saying "Headache" instead of "Nausea"), the current regex evaluator won't catch it. I would implement an NLP/Cosine-Similarity check or a second "Evaluator LLM" pass to verify semantic facts.
3. **API Rate Limits**: The pipeline currently processes sequentially and can hit Free-Tier API limits (`429 RESOURCE_EXHAUSTED`). For production, we need an enterprise key and asynchronous generation (`asyncio`) to build sections concurrently.
