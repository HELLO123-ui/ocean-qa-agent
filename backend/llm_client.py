import json
import os
from typing import List, Dict, Any

from groq import Groq

from .models import TestCase

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


# Use environment variable GROQ_API_KEY
_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _chat(system: str, user: str, temperature: float = 0.2) -> str:
    """
    Generic helper to call Groq's chat completion API.
    """
    response = _client.chat.completions.create(
    model=GROQ_MODEL,
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ],
    temperature=temperature,
)
    return response.choices[0].message.content.strip()


# ---------- Test case generation ----------

def generate_test_cases(query: str, context: str) -> List[Dict[str, Any]]:
    """
    Call the LLM to generate documentation-grounded test cases.
    Returns a list of dicts that match TestCase schema.
    """
    system_prompt = (
        "You are a senior QA engineer. "
        "You design comprehensive positive and negative test cases strictly "
        "based on the given project documentation. "
        "DO NOT invent features that are not present in the context. "
        "If some detail is not specified, leave it generic instead of guessing."
    )

    user_prompt = f"""
Context (project documentation and HTML description):
--------------------
{context}
--------------------

User request:
{query}

Output requirements:
- Use ONLY information from the Context above.
- Produce EXHAUSTIVE positive and negative test cases relevant to the request.
- Return STRICTLY valid JSON with the following structure and no additional text:

{{
  "test_cases": [
    {{
      "test_id": "TC-001",
      "feature": "Discount Code",
      "scenario": "Apply a valid discount code SAVE15",
      "preconditions": ["Cart contains at least one item"],
      "steps": [
        "Navigate to checkout page",
        "Enter 'SAVE15' in discount field",
        "Click Apply"
      ],
      "test_data": {{"discount_code": "SAVE15"}},
      "expected_result": "Total price is reduced by 15% and updated total is displayed.",
      "grounded_in": ["product_specs.md: discount rule section"]
    }}
  ]
}}
"""

    raw = _chat(system_prompt, user_prompt, temperature=0.15)

    # Ensure we end up with pure JSON
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        data = json.loads(raw[start:end])

    test_cases = data.get("test_cases", [])
    return test_cases


# ---------- Selenium script generation ----------

def generate_selenium_script(
    test_case: Dict[str, Any],
    checkout_html: str,
    context: str,
) -> str:
    """
    Call the LLM to generate a runnable Selenium Python test script
    for a single test case.
    """
    system_prompt = (
        "You are an expert Test Automation engineer who writes clean, "
        "runnable Selenium scripts in Python. "
        "Use explicit, reliable locators (id, name, CSS selectors) that MUST "
        "match the provided checkout.html. "
        "If a specific element id or name is not clearly present in the HTML, "
        "use a robust CSS selector based on text."
    )

    user_prompt = f"""
checkout.html (full source):
--------------------
{checkout_html}
--------------------

Documentation context (specs, UI/UX rules, etc.):
--------------------
{context}
--------------------

Test case to automate (JSON):
--------------------
{json.dumps(test_case, indent=2)}
--------------------

Write a SINGLE, complete Python function called `test_{test_case["test_id"].lower()}` 
that uses Selenium WebDriver with Chrome to implement this test case.

Requirements:
- Import the necessary Selenium modules (webdriver, By, WebDriverWait, expected_conditions).
- Start from an empty browser session and open the local checkout.html file.
- Follow the test steps in order and add short comments for each step.
- Use appropriate waits before interacting with elements.
- At the end, assert the expected result in a reasonable way (e.g., checking text or value).
- Always quit the driver in a finally block.
- Output ONLY Python code, without markdown backticks or extra explanation.
"""

    code = _chat(system_prompt, user_prompt, temperature=0.1)
    return code
