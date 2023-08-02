import streamlit as st
import os
import pytesseract
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFPageCountError
import threading
import time

def create_text_folder():
    text_folder_path = 'Library/TEXT'
    if not os.path.exists(text_folder_path):
        os.makedirs(text_folder_path)

def save_images_from_pdf(pathtoPDF, pathtoImage):
    for root, dirs, files in os.walk(pathtoPDF):
        for f in files:
            path = os.path.join(root, f)
            subdir = root.split(pathtoPDF)[-1]
            image_folder = os.path.join(pathtoImage, subdir)
            
            # Convert the PDF to a list of image pages
            pages = convert_from_path(path)
            
            os.makedirs(image_folder, exist_ok=True)
            
            # Loop through each page and save it as an image
            for i, page in enumerate(pages):
                image_path = os.path.join(image_folder, f'page_{i}.png')
                page.save(image_path, 'PNG')

            st.write(f"Saved images from {f} to {image_folder}")


def convert_pdf_to_text(pathtoPDF, pathtoText, pagelimit=1000, resolution=200):
    for root, dirs, files in os.walk(pathtoPDF):
        for f in files:
            path = os.path.join(root, f)
            if '.' in f[:3]:
                continue
            subdir = root.split(pathtoPDF)[-1]
            outputfile = os.path.join(pathtoText, subdir, f.split('.')[0] + '.txt')
            
            # Check if .txt file already exists
            if os.path.exists(outputfile):
                print(f".txt file for {f} already exists. Skipping conversion.")
                continue
            
            # Convert the PDF to a list of image pages
            pages = convert_from_path(path, resolution)
            # Loop through each page and perform OCR on the image
            for i, page in enumerate(pages):
                if i == pagelimit:  # page limit
                    break
                try:
                    # Convert the image page to grayscale
                    image = page.convert('L')
                    # Use Tesseract to perform OCR on the image and get the text
                    text = pytesseract.image_to_string(image)
                    # Create the output directory if it doesn't exist
                    os.makedirs(os.path.dirname(outputfile), exist_ok=True)
                    mode = 'w' if i == 0 else 'a'
                    with open(outputfile, mode) as file:
                        file.write(text)
                        file.write(" ")
                        file.write(f'\n{f}, Page: {i + 1}\n')
                        file.write(" ")
                except PDFPageCountError:
                    print(f'Error: Unable to extract page {i + 1} from {f}')
                    continue

def process_pdfs(pathtoPDF, pathtoText, status_box):
    try:
        pathtoImage = 'Squire_GPT/IMAGE'
        save_images_from_pdf(pathtoPDF, pathtoImage)
        convert_pdf_to_text(pathtoPDF, pathtoText)
        status_box.write("Processing complete!")
    except Exception as e:
        status_box.write(f"Error occurred during processing: {str(e)}")

def spearhead_library():
    st.title("Spear_Head_Library")
    st.markdown("Welcome to SpearHead_Library! This app allows you to store and search through your documents.")

    # File upload widget
    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

    if uploaded_file is not None:
        with open(os.path.join("Library/PDF", uploaded_file.name), "wb") as file:
            file.write(uploaded_file.getbuffer())
        st.success(f"{uploaded_file.name} has been uploaded successfully!")

    pdf_folder_path = 'Library/PDF'
    pdf_files = os.listdir(pdf_folder_path)
    if pdf_files:
        if st.button("Process"):
            pathtoPDF = pdf_folder_path
            pathtoText = 'Library/Text'
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
                progress_bar.progress(50)  # Update progress (50% as an example)
            processing_thread.join()
            progress_bar.progress(100)

if __name__ == "__main__":
    spearhead_library()
