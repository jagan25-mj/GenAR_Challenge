import json
from google import genai
from google.genai import types

class ReportGenerator:
    def __init__(self):
        # Assumes GEMINI_API_KEY is in the environment
        self.client = genai.Client()
        # You can use gemini-3.5-flash
        self.model_name = "gemini-3.5-flash"

    def generate_section(self, system_prompt: str, user_instructions: str, evidence: dict) -> str:
        """
        Generates a section using the exact scoped evidence provided.
        """
        # We format the evidence explicitly as JSON to ground the model.
        prompt = f"Instructions: {user_instructions}\n\nEvidence payload:\n{json.dumps(evidence, indent=2)}"
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.0, # Zero temperature for deterministic, factual reporting
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating section: {e}")
            return f"[Error generating content: {e}]"
