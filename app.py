import streamlit as st
import tempfile
import os
import base64
from io import BytesIO
from PIL import Image

from pdf_ingestion import save_to_json
from document_store import DocumentStore
from query_engine import QueryEngine
from pdf_parser import process_pdf

# ⚙️ Env vars
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

st.set_page_config(layout="wide")
st.title("📄 Intelligent Document Processing Agent")

store = DocumentStore()
engine = QueryEngine()

# Upload PDF
st.sidebar.header("Upload New PDF")
uploaded_files = st.sidebar.file_uploader("Upload academic papers (PDF)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_pdf in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_pdf.read())
            tmp_path = tmp.name

        st.sidebar.success(f"Uploaded: {uploaded_pdf.name}")

        with st.spinner(f"Processing {uploaded_pdf.name}..."):
            structured = process_pdf(tmp_path)
            path = save_to_json(structured, original_filename=uploaded_pdf.name)
            st.sidebar.success(f"Saved: {os.path.basename(path)}")

    store = DocumentStore()
    engine = QueryEngine()

# Select Paper
st.sidebar.header("Explore Stored Papers")
papers = store.list_papers()
paper_options = {p["title"]: p["id"] for p in papers}

if not paper_options:
    st.warning("⚠️ No papers available. Upload a PDF to begin.")
    st.stop()

selected_title = st.sidebar.selectbox("Choose a paper", list(paper_options.keys()))
selected_id = paper_options[selected_title]
paper_data = store.get_paper(selected_id)

# Flatten keys for dropdown (nested keys as path-style)
def flatten_keys(d, parent_key=''):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}/{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_keys(v, new_key))
        else:
            items.append(new_key)
    return items

available_keys = flatten_keys(paper_data)

# Dropdown selector
query_type = st.sidebar.selectbox("Choose query type", [
    "Direct Section Lookup",
    "Compare Papers",
    "Summarize Paper",
    "Extract Evaluation Metrics",
    "Q&A Bot",
    "Search Across Papers"
])

# Render helper

def render_image_item(item, title_prefix=""):
    if isinstance(item, dict) and "image_bytes" in item:
        try:
            image_data = base64.b64decode(item["image_bytes"])
            image = Image.open(BytesIO(image_data))
            st.image(image, caption=f"{title_prefix} - {item.get('name', 'Figure')}")
        except Exception as e:
            st.warning(f"⚠️ Error displaying image: {e}")
    else:
        st.text(str(item))

# Query logic
if query_type == "Direct Section Lookup":
    selected_key = st.selectbox("Select section or metadata", available_keys)
    keys = selected_key.split("/")
    content = paper_data
    try:
        for k in keys:
            content = content[k]
        st.subheader(f"📄 Content: {selected_key}")
        if selected_key.startswith("figures") and isinstance(content, list):
            idx = st.number_input("🔍 Index", min_value=1, max_value=len(content), value=1)
            render_image_item(content[idx - 1], title_prefix=selected_key)

        elif selected_key.startswith("tables") and isinstance(content, list):
            idx = st.number_input("🔍 Index", min_value=1, max_value=len(content), value=1)
            table_item = content[idx - 1]
            st.markdown(f"**📄 Page:** {table_item.get('page', 'N/A')}")

            # Try to render the table
            table_data = table_item.get("table")
            if isinstance(table_data, list) and all(isinstance(row, list) for row in table_data):
                import pandas as pd
                df = pd.DataFrame(table_data[1:], columns=table_data[0])
                st.dataframe(df)
            else:
                st.warning("⚠️ Unable to parse table format. Showing raw data:")
                st.write(table_data)

        elif isinstance(content, list):
            idx = st.number_input("🔍 Index", min_value=1, max_value=len(content), value=1)
            st.write(content[idx - 1])

        else:
            st.write(content)
    except Exception as e:
        st.error(f"Failed to fetch section: {e}")

elif query_type == "Compare Papers":
    compare_title = st.selectbox("Select another paper", [t for t in paper_options if t != selected_title])
    compare_id = paper_options[compare_title]
    compare_data = store.get_paper(compare_id)

    compare_keys = flatten_keys(compare_data)
    selected_key = st.selectbox("Section from current paper", available_keys, key="section1")
    compare_key = st.selectbox("Section from comparison paper", compare_keys, key="section2")

    def extract_from_path(data, path):
        try:
            for k in path.split("/"):
                data = data[k]
            return data
        except:
            return None

    content1 = extract_from_path(paper_data, selected_key)
    content2 = extract_from_path(compare_data, compare_key)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**📰 {selected_title} - {selected_key}**")
        if isinstance(content1, list):
            if content1:
                idx1 = st.number_input("🔍 Index", min_value=1, max_value=len(content1), value=1, key="idx1")
                render_image_item(content1[idx1 - 1], title_prefix=selected_key)
            else:
                st.warning("⚠️ No content.")
        else:
            st.write(content1)

    with col2:
        st.markdown(f"**📰 {compare_title} - {compare_key}**")
        if isinstance(content2, list):
            if content2:
                idx2 = st.number_input("🔍 Index", min_value=1, max_value=len(content2), value=1, key="idx2")
                render_image_item(content2[idx2 - 1], title_prefix=compare_key)
            else:
                st.warning("⚠️ No content.")
        else:
            st.write(content2)

    if st.button("Compare Selected Sections"):
        result = engine.compare_sections(selected_id, selected_key, compare_id, compare_key)
        st.subheader("📊 Section Comparison")
        st.write(result)

elif query_type == "Summarize Paper":
    if st.button("📝 Generate Summary"):
        result = engine.summarize_paper(selected_id)
        st.subheader("📘 Paper Summary")
        st.write(result)

elif query_type == "Extract Evaluation Metrics":
    metrics = st.text_input("Enter metrics (comma-separated)", value="accuracy, precision, recall, f1")
    if st.button("📈 Extract Metrics"):
        metric_list = [m.strip() for m in metrics.split(",")]
        result = engine.extract_metrics(selected_id, metric_list)
        st.subheader("📊 Extracted Metrics")
        st.json(result)

elif query_type == "Q&A Bot":
    question = st.text_input("Ask a question about this paper:")
    if st.button("💬 Ask Question"):
        with st.spinner("🧠 Thinking..."):
            result = engine.ask_question(selected_id, question)
        st.subheader("💡 Answer")
        st.write(result)

elif query_type == "Search Across Papers":
    query = st.text_input("Enter a keyword or phrase:")
    if st.button("Search All Papers"):
        results = engine.search_across_papers(query)
        if results:
            for res in results:
                st.markdown(f"### 📄 {res['paper_id']} | Section: {res['section']}")
                st.write(res['content'])
                st.markdown("---")
        else:
            st.warning("No relevant content found.")
