import os
import streamlit as st
from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# Set up page configuration
st.set_page_config(page_title="Smart OCR Scanner", page_icon="📄", layout="centered")
st.title("📄 Smart Document Text Extractor")
st.write("Upload a PDF or an Image to instantly extract plain text.")

uploaded_file = st.file_uploader("Choose a file...", type=["pdf", "png", "jpg", "jpeg", "bmp", "tiff"])

if uploaded_file is not None:
    # Save uploaded file temporarily to process it
    temp_filename = uploaded_file.name
    with open(temp_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    if st.button("Extract Text", type="primary"):
        with st.spinner("Running OCR Engine... Please wait..."):
            ext = os.path.splitext(temp_filename)[1].lower()
            extracted_text = ""
            
            # Scenario A: Direct Images
            if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                try:
                    img = Image.open(temp_filename)
                    extracted_text = pytesseract.image_to_string(img)
                except Exception as e:
                    extracted_text = f"Error reading image: {e}"
            else:
                # Scenario B: PDFs
                try:
                    reader = PdfReader(temp_filename)
                    total_pages = len(reader.pages)
                    
                    for page_num in range(total_pages):
                        text = reader.pages[page_num].extract_text()
                        
                        # Fallback to OCR if the page text is empty (scanned image PDF)
                        if not text or text.strip() == "":
                            images = convert_from_path(temp_filename, first_page=page_num+1, last_page=page_num+1)
                            if images:
                                text = pytesseract.image_to_string(images[0])
                        
                        extracted_text += f"--- Page {page_num + 1} of {total_pages} ---\n"
                        extracted_text += (text.strip() if text and text.strip() else "[No text found on this page.]")
                        extracted_text += "\n\n" + "="*40 + "\n\n"
                except Exception as e:
                    if "invalid pdf header" in str(e).lower() or "stream has ended" in str(e).lower():
                        # Scenario C: Disguised PDF
                        try:
                            img = Image.open(temp_filename)
                            extracted_text = "--- Extracted Text from Disguised Asset ---\n" + pytesseract.image_to_string(img)
                        except Exception as img_err:
                            extracted_text = f"Failed to parse disguised file: {img_err}"
                    else:
                        extracted_text = f"An unexpected error occurred: {e}"
            
            # Clean up the temporary file safely
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
            # Display Result
            st.success("Extraction Completed!")
            st.text_area("Extracted Text Output", value=extracted_text, height=400)