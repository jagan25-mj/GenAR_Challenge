import os
import json
import yaml
import pandas as pd
from dotenv import load_dotenv

from analyzer import DataAnalyzer
from generator import ReportGenerator
from src.evidence_builder import EvidenceBuilder
from src.evaluator import GroundingEvaluator

def run_report(report_id, dataset_path, output_md_path):
    load_dotenv()
    
    with open("config/reports.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    report_config = config["reports"][report_id]
    system_prompt = report_config["system_prompt"]
    sections_config = report_config["sections"]

    analyzer = DataAnalyzer(dataset_path)
    evidence_builder = EvidenceBuilder(analyzer)
    generator = ReportGenerator()
    
    report_md = []
    report_md.append(f"# {report_config['title']}\n")

    test_results = {"report_id": report_id, "sections": []}

    print(f"--- Running Test: {report_id} ---")
    for section in sections_config:
        evidence_packet = evidence_builder.build_packet(section["evidence_keys"])
        generated_text = generator.generate_section(
            system_prompt=system_prompt,
            user_instructions=section["instructions"],
            evidence=evidence_packet
        )
        evaluation = GroundingEvaluator.evaluate(generated_text, evidence_packet)
        
        report_md.append(f"## {section['title']}")
        report_md.append(generated_text + "\n")
        
        test_results["sections"].append({
            "section_id": section["id"],
            "generated_text": generated_text,
            "is_grounded": evaluation["is_grounded"],
            "unsupported_numbers": evaluation["unsupported_numbers"]
        })
        
        if not evaluation["is_grounded"]:
            print(f"[!] HALLUCINATION CAUGHT in {section['id']}: Unsupported numbers {evaluation['unsupported_numbers']}")
        else:
            print(f"[OK] {section['id']} passed grounding.")

    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_md))
        
    return test_results

def main():
    results = []
    
    # Setup Empty Dataset for Test 3
    empty_df = pd.DataFrame(columns=[
        "safetyreportid", "receivedate", "serious", "patient_patientonsetage", 
        "patient_patientsex", "occurcountry", "patient_reaction_reactionmeddrapt",
        "patient_reaction_reactionoutcome", "seriousnessdeath"
    ])
    empty_df.to_excel("empty.xlsx", index=False)
    
    real_data = "../Bisoprolol_icsr_sample_1068rows.xlsx"
    
    # Test 1: Reusability
    r1 = run_report("SIGNAL_SNAPSHOT", real_data, "Test1_Signal.md")
    results.append(r1)
    
    # Test 2: Adversarial
    r2 = run_report("ADVERSARIAL_TEST", real_data, "Test2_Adversarial.md")
    results.append(r2)
    
    # Test 3: Empty Data
    r3 = run_report("PADER", "empty.xlsx", "Test3_Empty.md")
    results.append(r3)

    # Save test results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("All tests completed. Check test_results.json")

if __name__ == "__main__":
    main()
