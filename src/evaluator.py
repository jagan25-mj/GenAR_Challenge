import re
import json

class GroundingEvaluator:
    @staticmethod
    def extract_numbers(text: str) -> list[str]:
        """Extracts numerical sequences from text (e.g., '1024', '1,024', '99.9')."""
        # Find raw digits, possibly including commas and decimals
        matches = re.findall(r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b', text)
        # Normalize commas
        return [m.replace(',', '') for m in matches]

    @staticmethod
    def extract_numbers_from_dict(data: dict | list | str | int | float) -> set[str]:
        """Recursively extracts all numbers present in the evidence dict as a set of strings."""
        numbers = set()
        if isinstance(data, dict):
            for k, v in data.items():
                numbers.update(GroundingEvaluator.extract_numbers_from_dict(v))
                numbers.update(GroundingEvaluator.extract_numbers_from_dict(k))
        elif isinstance(data, list):
            for item in data:
                numbers.update(GroundingEvaluator.extract_numbers_from_dict(item))
        elif isinstance(data, str):
            numbers.update(GroundingEvaluator.extract_numbers(data))
        elif isinstance(data, (int, float)):
            numbers.add(str(data))
        return numbers

    @staticmethod
    def evaluate(generated_text: str, evidence_packet: dict) -> dict:
        """
        Validates that all numbers in the generated text are grounded in the evidence packet.
        """
        text_numbers = set(GroundingEvaluator.extract_numbers(generated_text))
        evidence_numbers = GroundingEvaluator.extract_numbers_from_dict(evidence_packet)

        unsupported_numbers = text_numbers - evidence_numbers
        
        is_grounded = len(unsupported_numbers) == 0
        
        return {
            "is_grounded": is_grounded,
            "text_numbers_found": list(text_numbers),
            "evidence_numbers_found": list(evidence_numbers),
            "unsupported_numbers": list(unsupported_numbers)
        }
