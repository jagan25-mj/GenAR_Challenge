import os
import json
from openai import OpenAI

class ReportGenerator:
    def __init__(self):
        # Initialize the OpenAI client pointing to NVIDIA NIM
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ.get("NVIDIA_API_KEY", "NOT_SET"),
        )
        # Using Llama 3.1 8B Instruct hosted on NVIDIA infrastructure
        self.model_name = "meta/llama-3.1-8b-instruct"

    def generate_section(self, system_prompt: str, user_instructions: str, evidence: dict) -> str:
        """
        Generates a section using the exact scoped evidence provided.
        """
        prompt = f"Instructions: {user_instructions}\n\nEvidence payload:\n{json.dumps(evidence, indent=2)}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating section: {e}")
            return f"[Error generating content: {e}]"
