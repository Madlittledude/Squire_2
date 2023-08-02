import streamlit as st
from llama_index import SimpleDirectoryReader
from llama_index.node_parser import SimpleNodeParser
from llama_index import VectorStoreIndex
from pdf2image import convert_from_path
import threading
import io

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def load_data_and_index(text_data):
    filename_fn = lambda filename: {'file_name': filename}
    documents = [{'content': text, 'metadata': filename_fn(f"text_{i}")} for i, text in enumerate(text_data)]
    parser = SimpleNodeParser()
    nodes = parser.get_nodes_from_documents(documents)
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine(max_nodes=6, max_tokens=500)
    return index, query_engine

def process_pdf_data(pdf_data_list):
    text_results = []  # List to store processed text from each PDF
    for pdf_data in pdf_data_list:
        # Process the PDF data here; convert to text using your preferred method
        # For the current mockup, I'll just use a dummy conversion
        text_data = "Dummy Text " + pdf_data[:20]  # Modify this with your actual conversion method
        text_results.append(text_data)
    return text_results

def spearhead_library():
    st.title("SpearHead Library")

    # PDF upload
    uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
    process_button = st.button("Process PDFs")
    user_query = st.text_input("Enter your question:")
    status_box = st.empty()

    # Initiate session state for PDF data and processed texts
    if "pdf_data" not in st.session_state:
        st.session_state.pdf_data = []
    if "text_data" not in st.session_state:
        st.session_state.text_data = []

    if process_button:
        if uploaded_files:
            # Store the uploaded PDFs in session state
            for uploaded_file in uploaded_files:
                st.session_state.pdf_data.append(uploaded_file.read())
            status_box.write("Processing PDFs...")
            # Process the uploaded PDFs
            processed_texts = process_pdf_data(st.session_state.pdf_data)
            st.session_state.text_data.extend(processed_texts)
            status_box.write("PDFs processed and converted to text.")

    if user_query and st.session_state.text_data:
        index, query_engine = load_data_and_index(st.session_state.text_data)
        response = query_engine.query(user_query)
        response_text = response.response
        filenames = [node.node.metadata['file_name'].split('/')[-1].split('.')[0] for node in response.source_nodes]
        st.write(response_text)
        st.write("Sources:", ', '.join(filenames))
    elif not user_query and not process_button:
        st.write("Upload PDFs, process them, then enter your query in the textbox.")

if __name__ == "__main__":
    spearhead_library()


