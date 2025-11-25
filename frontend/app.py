import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import streamlit as st
import pandas as pd

from backend.ingestion import build_knowledge_base, get_html_content
from backend.rag import query_kb
from backend.llm_client import generate_test_cases, generate_selenium_script

st.set_page_config(
    page_title="Autonomous QA Agent",
    page_icon="🧪",
    layout="wide",
)

# ---------- Session state ----------

if "kb_built" not in st.session_state:
    st.session_state.kb_built = False

if "test_cases" not in st.session_state:
    st.session_state.test_cases = []

if "checkout_html" not in st.session_state:
    st.session_state.checkout_html = ""


# ---------- Sidebar ----------

with st.sidebar:
    st.title("🧪 QA Agent")
    st.markdown(
        """
    **Steps**

    1. Upload docs + `checkout.html`  
    2. Build Knowledge Base  
    3. Generate Test Cases  
    4. Select a case → Generate Selenium Script
    """
    )
    st.markdown("---")
    st.markdown("**Status**")
    st.write("KB built:", "✅" if st.session_state.kb_built else "❌")
    st.write("Test cases:", len(st.session_state.test_cases))


st.title("Autonomous QA Agent - Ocean AI Assignment")
st.caption("Upload project documentation once, then let the agent design QA plans and Selenium scripts.")


# ---------- Section 1: Upload + Build KB ----------

st.header("1️⃣ Upload Project Assets & Build Knowledge Base")

col1, col2 = st.columns(2)

with col1:
    support_files = st.file_uploader(
        "Support documents (MD / TXT / JSON / PDF)",
        type=["md", "txt", "json", "pdf"],
        accept_multiple_files=True,
        help="Upload 3–5 documents such as product_specs, UI/UX guide, API docs.",
    )

with col2:
    checkout_file = st.file_uploader(
        "`checkout.html` file",
        type=["html"],
        accept_multiple_files=False,
        help="Single-page E-Shop Checkout HTML.",
    )

if st.button("🚀 Build Knowledge Base", use_container_width=True):
    if not support_files or not checkout_file:
        st.error("Please upload at least one support document **and** the `checkout.html` file.")
    else:
        with st.spinner("Parsing documents and building vector database..."):
            docs = [(f.name, f.read()) for f in support_files]
            checkout_html = checkout_file.read().decode("utf-8", errors="ignore")
            msg = build_knowledge_base(docs, checkout_html)

        st.session_state.kb_built = True
        st.session_state.checkout_html = checkout_html

        st.success("Knowledge base built successfully ✅")
        st.info(msg)


st.markdown("---")

# ---------- Section 2: Test Case Generation ----------

st.header("2️⃣ Generate Documentation-Grounded Test Cases")

default_query = "Generate all positive and negative test cases for the discount code feature."

query = st.text_area(
    "Describe what you want test cases for",
    value=default_query,
    help="You can ask for a specific feature, flow, or module.",
)

if st.button("🧠 Generate Test Cases", use_container_width=True):
    if not st.session_state.kb_built:
        st.error("Please build the knowledge base first.")
    else:
        with st.spinner("Retrieving relevant documentation and generating test cases..."):
            context = query_kb(query)
            test_cases_raw = generate_test_cases(query, context)

        st.session_state.test_cases = test_cases_raw

        if not test_cases_raw:
            st.warning("No test cases were generated. Try a different query.")
        else:
            st.success(f"Generated {len(test_cases_raw)} test cases ✅")

# Show test cases in a table if any
if st.session_state.test_cases:
    st.subheader("Generated Test Cases")

    df = pd.DataFrame(
        [
            {
                "ID": tc["test_id"],
                "Feature": tc["feature"],
                "Scenario": tc["scenario"],
                "Expected Result": tc["expected_result"],
            }
            for tc in st.session_state.test_cases
        ]
    )
    st.dataframe(df, use_container_width=True)

st.markdown("---")

# ---------- Section 3: Selenium Script Generation ----------

st.header("3️⃣ Generate Selenium Test Script")

if not st.session_state.test_cases:
    st.info("Generate test cases above to enable Selenium script generation.")
else:
    options = [
        f'{tc["test_id"]} — {tc["scenario"]}'
        for tc in st.session_state.test_cases
    ]
    selected_label = st.selectbox("Select a test case to automate", options)
    selected_index = options.index(selected_label)
    selected_tc = st.session_state.test_cases[selected_index]

    st.markdown("**Selected Test Case (detailed)**")
    st.json(selected_tc, expanded=False)

    if st.button("💻 Generate Selenium Script", use_container_width=True):
        if not st.session_state.checkout_html:
            st.error("checkout.html is missing from session. Rebuild the knowledge base.")
        else:
            with st.spinner("Generating Selenium Python script..."):
                # Use the test scenario as an additional query to get focused context
                context = query_kb(
                    selected_tc["feature"] + " " + selected_tc["scenario"]
                )
                code = generate_selenium_script(
                    test_case=selected_tc,
                    checkout_html=st.session_state.checkout_html,
                    context=context,
                )

            st.success("Selenium script generated ✅")
            st.code(code, language="python")

st.markdown("---")
st.caption(
    "All test reasoning is grounded in the uploaded documentation and HTML structure. "
    "No hallucinated features are introduced."
)
