import streamlit as st
import os
from llama_index import SimpleDirectoryReader
from llama_index.node_parser import SimpleNodeParser
from llama_index import VectorStoreIndex
from pdf2image import convert_from_path
import threading

def load_data_and_index(path_to_texts):
    filename_fn = lambda filename: {'file_name': filename}
    documents = SimpleDirectoryReader(path_to_texts, file_metadata=filename_fn).load_data()
    parser = SimpleNodeParser()
    nodes = parser.get_nodes_from_documents(documents)
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine(max_nodes=6, max_tokens=500)
    return index, query_engine

def save_images_from_pdf(pdf_path, image_path):
    images = convert_from_path(pdf_path)
    for i, img in enumerate(images):
        img.save(f"{image_path}/page_{i}.png", "PNG")

def process_pdfs(status_box, path_to_pdfs, path_to_texts):
    for file in os.listdir(path_to_pdfs):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(path_to_pdfs, file)
            save_images_from_pdf(pdf_path, path_to_texts)
    status_box.write("PDFs processed and converted to text.")

def spearhead_library():
    st.title("SpearHead Library")

    # PDF upload
    uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
    process_button = st.button("Process PDFs")
    user_query = st.text_input("Enter your question:")
    status_box = st.empty()

    if process_button:
        if uploaded_files:
            # Create directories if they don't exist
            if not os.path.exists("Library/PDF"):
                os.makedirs("Library/PDF")
            if not os.path.exists("Library/TEXT"):
                os.makedirs("Library/TEXT")

            # Save the PDFs
            for uploaded_file in uploaded_files:
                with open(f"pdf_uploads/{uploaded_file.name}", "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            status_box.write("Processing PDFs...")
            # Process the uploaded PDFs in a separate thread to prevent blocking
            threading.Thread(target=process_pdfs, args=(status_box, "Library/PDF", "Library/TEXT")).start()
    
    if user_query:
        index, query_engine = load_data_and_index('Library/TEXT')
        response = query_engine.query(user_query)
        response_text = response.response
        filenames = [node.node.metadata['file_name'].split('/')[-1].split('.')[0] for node in response.source_nodes]
        st.write(response_text)
        st.write("Sources:", ', '.join(filenames))
    elif not user_query and not process_button:
        st.write("Upload PDFs, process them, then enter your query in the textbox.")

if __name__ == "__main__":
    spearhead_library()

