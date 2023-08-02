import streamlit as st
import os
import threading
import time
import re
from pathlib import Path
from pdf2text import process_pdfs, create_text_folder
from llama_index import SimpleDirectoryReader, VectorStoreIndex
from llama_index.node_parser import SimpleNodeParser

# Helper Functions
def find_page_number(node_text, document_path):
    search_text = node_text[:30]
    
    with open(document_path, 'r', encoding='utf-8') as f:
        content = f.read()

    position = content.find(search_text)
    if position == -1:
        return None

    subsequent_content = content[position:]
    page_match = re.search(r'Page: (\d+)', subsequent_content)
    return int(page_match.group(1)) if page_match else None

@st.cache_resource()
def load_data_and_index():
    filename_fn = lambda filename: {'file_name': filename}
    documents = SimpleDirectoryReader('Library/TEXT', file_metadata=filename_fn).load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine(max_nodes=6, max_tokens=500)
    return index, query_engine

def get_response(user_query, query_engine):
    response = query_engine.query(user_query)
    node_texts = [node.node.text[:30] for node in response.source_nodes]
    filenames = [node.node.metadata['file_name'] for node in response.source_nodes]
    pages = [find_page_number(node_text, Path(f)) for node_text, f in zip(node_texts, filenames)]
    sources = [(f, p) for f, p in zip(filenames, pages) if p is not None]
    return response.response, sources

def spearhead_library():
    st.title("SpearHead_Library")

    # Ensure the necessary folders exist
    for folder in ["Library/PDF", "Library/TEXT"]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Step 1: Upload Files
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt"])

    if uploaded_file:
        file_extension = uploaded_file.name.split('.')[-1].lower()

        if file_extension == 'pdf':
            with open(os.path.join("Library/PDF", uploaded_file.name), "wb") as file:
                file.write(uploaded_file.getbuffer())
            st.success(f"{uploaded_file.name} has been stored!")
        elif file_extension == 'txt':
            with open(os.path.join("Library/TEXT", uploaded_file.name), "wb") as file:
                file.write(uploaded_file.getbuffer())
            st.success(f"{uploaded_file.name} has been uploaded!")

    pdf_files = os.listdir('Library/PDF')

    # Allow user to initiate the processing only if a PDF is present in the PDF folder
    if pdf_files:
        if st.button("Process PDF"):
            status_box = st.empty()
            processing_thread = threading.Thread(target=process_pdfs, args=('Library/PDF', 'Library/TEXT', status_box))
            processing_thread.start()
            
            progress_bar = st.progress(0)
            num_files = len(pdf_files)
            for i in range(num_files):
                while processing_thread.is_alive():
                    time.sleep(0.1)
                    progress_bar.progress((i + 1) / num_files * 100)
            processing_thread.join()

            st.success(f"All PDFs have been processed!")

            # Display the names of the processed PDFs to the user
            st.write("Processed PDFs:")
            for pdf_file in pdf_files:
                st.write(pdf_file)
            
            # Loading data to the vector database
            index, query_engine = load_data_and_index()

    # Allow user to initiate the processing only if a PDF is present in the PDF folder
    if os.listdir('Library/PDF'):
        pathtoPDF = 'Library/PDF'  # Moved up here
        pathtoText = 'Library/TEXT'  # Moved up here

        if st.button("Process PDF"):
            status_box = st.empty()
            processing_thread = threading.Thread(target=process_pdfs, args=(pathtoPDF, pathtoText, status_box))
            processing_thread.start()
            progress_bar = st.progress(0)
            cancel_button = st.button("Cancel Processing")
            while processing_thread.is_alive():
                if cancel_button:
                    status_box.write("Processing cancelled.")
                    break
                time.sleep(0.1)
                progress_bar.progress(50)
            processing_thread.join()
            progress_bar.progress(100)
            if os.listdir('Library/TEXT'):  # Check if the TEXT directory has any files before loading data
                index, query_engine = load_data_and_index()


    # Step 2: Input user queries and display responses
    # This part should be shown only if the index has been loaded (i.e., after PDF processing)
    # Check and initialize session state for user query
    if 'user_query' not in st.session_state:
        st.session_state.user_query = ""

    # Step 2: Input user queries and display responses
    # This part should be shown only if the index has been loaded (i.e., after PDF processing)
    if 'query_engine' in locals():
        st.session_state.user_query = st.text_input("Enter your question:", value=st.session_state.user_query)
        
        if st.session_state.user_query:
            response_text, sources = get_response(st.session_state.user_query, query_engine)
            
            # Check if the response is not empty
            if response_text:
                st.write("Response:", response_text)
                st.write("Sources:", ', '.join([f"{Path(f).stem} (Page: {p})" for f, p in sources]))
            else:
                st.write("No response found for the query.")

if __name__ == "__main__":
    spearhead_library()
