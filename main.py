import os
import json
import yaml
from dotenv import load_dotenv

from analyzer import DataAnalyzer
from generator import ReportGenerator
from src.evidence_builder import EvidenceBuilder
from src.evaluator import GroundingEvaluator

def main():
    load_dotenv()
    
    # Configuration
    dataset_path = "../Bisoprolol_icsr_sample_1068rows.xlsx"
    output_md_path = "PADER_Report.md"
    audit_log_path = "audit_log.json"
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY is missing from environment or .env file.")
        return

    print("Step 1: Loading Report Configuration...")
    with open("config/reports.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    pader_config = config["reports"]["PADER"]
    system_prompt = pader_config["system_prompt"]
    sections_config = pader_config["sections"]

    print("Step 2: Running deterministic data analysis...")
    analyzer = DataAnalyzer(dataset_path)
    evidence_builder = EvidenceBuilder(analyzer)

    print("Step 3: Initializing AI Generation Engine...")
    generator = ReportGenerator()
    
    report_md = []
    audit_log = []

    # Deterministic Header
    reporting_period = analyzer.get_reporting_period()
    report_md.append(f"# {pader_config['title']}")
    report_md.append(f"**Reporting Period**: {reporting_period['start_date']} to {reporting_period['end_date']}\n")
    report_md.append(f"---\n")

    print("Step 4: Generating Sections...")
    for section in sections_config:
        print(f"Generating {section['title']}...")
        
        # 1. Build scoped evidence
        evidence_packet = evidence_builder.build_packet(section["evidence_keys"])
        
        # 2. Generate text
        generated_text = generator.generate_section(
            system_prompt=system_prompt,
            user_instructions=section["instructions"],
            evidence=evidence_packet
        )
        
        # 3. Evaluate Grounding
        evaluation = GroundingEvaluator.evaluate(generated_text, evidence_packet)
        if not evaluation["is_grounded"]:
            print(f"  [!] WARNING: Potential hallucination in section {section['id']}")
            print(f"  [!] Unsupported numbers: {evaluation['unsupported_numbers']}")
        
        # 4. Append
        report_md.append(f"## {section['title']}")
        report_md.append(generated_text + "\n")
        
        audit_log.append({
            "section_id": section["id"],
            "evidence_packet": evidence_packet,
            "generated_text": generated_text,
            "evaluation": evaluation
        })

    # Hardcoded deterministic footers
    print("Appending History of Actions...")
    report_md.append("## 7. History of Actions")
    report_md.append("No history of actions data was supplied with this dataset.\n")

    print("Appending Case Index...")
    report_md.append("## 8. Case Index / Listing")
    report_md.append("A structured case listing accompanies this report. (See raw dataset `Bisoprolol_icsr_sample_1068rows.xlsx`).\n")

    # Output Report
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_md))
    print(f"Report generated successfully: {output_md_path}")

    # Output Audit Log
    with open(audit_log_path, "w", encoding="utf-8") as f:
        json.dump(audit_log, f, indent=2)
    print(f"Audit log saved to: {audit_log_path}")

if __name__ == "__main__":
    main()
