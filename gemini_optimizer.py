import google.generativeai as genai
import os
import time
import re

class ResumeOptimizer:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Google AI API key is required.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def _query_gemini(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"[ERROR] Gemini API call failed: {e}")
            return "" # Return empty on failure

    def enhance_resume_content(self, raw_resume_data: str) -> str:
        """
        Takes raw resume data as a string and returns a fully optimized version
        based on a comprehensive set of rules.
        """
        if not raw_resume_data.strip():
            return ""

        prompt = f"""You are an expert resume writer and ATS optimization specialist. Your goal is to rewrite the given resume to be over 90% ATS-friendly, recruiter-friendly, and highly professional. You must remove all dummy text and use only clear, factual information.

**General Rules:**
1.  **Perfection:** Correct all spelling, grammar, and punctuation errors.
2.  **Professional Tone:** Enhance sentences to be impactful and professional, using strong action verbs (e.g., Developed, Designed, Managed, Implemented).
3.  **Keywords:** Strategically include relevant ATS-friendly keywords (e.g., WordPress, HTML, CSS, JavaScript, PHP, MySQL, UI/UX, SEO).
4.  **Honesty:** Keep all details truthful. Do not invent or embellish experience.

**Section-Specific Formatting:**

*   **Skills:**
    *   Group skills into logical categories (e.g., Programming Languages, Frameworks, Tools).
    *   Separate skills within a category with commas.
    *   Example:
        `Skills`
        `Programming Languages: Python, JavaScript, SQL`
        `Frameworks: React, Django, Node.js`

*   **Education:**
    *   Provide the accurate course name, institution, GPA/percentage, and years.
    *   Format: `[Course Name], [Institution Name] - [GPA/Percentage] ([Start Year] - [End Year])`

*   **Experience:**
    *   Start each bullet point on a new line with a strong action verb.
    *   Clearly describe responsibilities and achievements.

*   **Projects:**
    *   Clearly state the technologies used, your role, and the results or impact of the project.

**Final Output Requirements:**
*   Produce plain text with each section clearly labeled.
*   Do not add any commentary or explanations, only the final rewritten resume content.

**Input Resume Data:**
{raw_resume_data}
"""
        return self._query_gemini(prompt)
