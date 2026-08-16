# Version 1 Evolution Design

If tasked to expand Version 0 to support PSUR, PBRER, DSUR, and CSR, the system must shift from a hardcoded script to a configuration-driven platform. The core philosophy of "Deterministic Evidence -> Scoped Prompts -> LLM Narrative" remains, but the orchestration becomes dynamic.

## 1. Configurable Report Templates
Instead of hardcoding sections in `main.py`, the system will use JSON/YAML configuration files for each report type.
A `pbrer_config.yaml` would define:
- `sections`: List of sections to include.
- For each section:
  - `data_queries`: The specific pandas aggregation functions to run.
  - `prompt_template`: The specific instructions for that section.

## 2. Reusable Analysis Modules
`analyzer.py` will evolve into a modular library of analyses (e.g., `DemographicAnalyzer`, `SeriousReactionAnalyzer`). 
The configuration file will call these modules by name. The same "serious case count" logic can be injected into a PADER's "Summary Analysis" and a PSUR's "Worldwide Marketing Experience" section.

## 3. Evidence Tracing & Human Review
The pipeline will output an intermediate JSON artifact containing:
`{ "section_name": "Trends", "generated_text": "...", "evidence_used": {"total_cases": 1024} }`
A frontend UI would render this intermediate JSON. When a reviewer clicks a generated sentence, the UI highlights the `"evidence_used"` payload, providing 100% traceability before the reviewer clicks "Approve".

## 4. Evaluation Engine
We would implement a deterministic verifier. After the LLM generates a section, a post-processing script uses NLP/regex to ensure every number present in the generated text actually exists in the `evidence_used` payload. If a hallucinated number is found, the generation fails validation.
