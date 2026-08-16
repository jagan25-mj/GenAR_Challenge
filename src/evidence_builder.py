import json

class EvidenceBuilder:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        # Pre-compute all facts
        self.reporting_period = self.analyzer.get_reporting_period()
        self.case_volume = self.analyzer.get_case_volume()
        self.demographics = self.analyzer.get_demographics()
        self.reactions = self.analyzer.get_reactions(top_n=5)
        self.outcomes = self.analyzer.get_outcomes()
        self.serious_criteria = self.analyzer.get_serious_criteria()

    def build_packet(self, required_keys: list[str]) -> dict:
        """
        Dynamically builds the evidence payload for a section, including only the requested keys.
        """
        packet = {}
        for key in required_keys:
            if key == "reporting_period":
                packet["reporting_period"] = self.reporting_period
            elif key == "case_volume":
                packet["case_volume"] = self.case_volume
            elif key == "demographics":
                packet["demographics"] = self.demographics
            elif key == "top_reactions":
                packet["top_reactions"] = self.reactions.get("top_reactions", {})
            elif key == "top_serious_reactions":
                packet["top_serious_reactions"] = self.reactions.get("top_serious_reactions", {})
            elif key == "outcomes":
                packet["outcomes"] = self.outcomes
            elif key == "serious_cases_count":
                packet["serious_cases_count"] = self.case_volume.get("serious_cases", 0)
            elif key == "serious_criteria":
                packet["serious_criteria"] = self.serious_criteria
            else:
                packet[key] = f"Warning: Key {key} not found in deterministic analyzer."
        return packet
