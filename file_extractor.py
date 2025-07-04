from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import TextConverter
import os
import io
import logging
from typing import List, Optional
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    This function returns a text from pdf file
    :param pdf_path: path for the pdf file
    :return: text
    """
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        r_manager = PDFResourceManager()
        output = io.StringIO()
        converter = TextConverter(r_manager, output, laparams=LAParams())
        p_interpreter = PDFPageInterpreter(r_manager, converter)

        with open(pdf_path, 'rb') as file:
            for page in PDFPage.get_pages(file, caching=True, check_extractable=True):
                p_interpreter.process_page(page)
                text = output.getvalue()
            
        converter.close()
        output.close()
        
        if not text.strip():
            logger.warning(f"Empty text extracted from PDF: {pdf_path}")
            
        return text
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

def read_files(file_path: str) -> List[str]:
    """
    This function returns a list of texts from multiple files
    :param file_path: path for the directory that contains multiple pdf, docx and doc files
    :return: returns list of texts
    """
    fileTXT: List[str] = []
    
    try:
        if not os.path.exists(file_path):
            logger.warning(f"Directory {file_path} does not exist")
            return fileTXT

        if not os.path.isdir(file_path):
            logger.warning(f"Path {file_path} is not a directory")
            return fileTXT

        for filename in os.listdir(file_path):
            if filename.startswith('.'):  # Skip hidden files
                continue
                
            file_full_path = os.path.join(file_path, filename)
            
            if not os.path.isfile(file_full_path):
                continue
            
            try:
                if filename.lower().endswith(".pdf"):
                    text = extract_text_from_pdf(file_full_path)
                    if text.strip():  # Only add non-empty text
                        fileTXT.append(text)
                    else:
                        logger.warning(f"Empty text extracted from PDF: {filename}")
                
                elif filename.lower().endswith(".txt"):
                    # Handle plain text files
                    try:
                        with open(file_full_path, 'r', encoding='utf-8') as f:
                            text = f.read()
                        if text.strip():
                            fileTXT.append(text)
                        else:
                            logger.warning(f"Empty text file: {filename}")
                    except Exception as e:
                        logger.error(f"Error reading text file {filename}: {str(e)}")
                        
            except Exception as e:
                logger.error(f"Error processing file {filename}: {str(e)}")
                continue
        
        logger.info(f"Successfully processed {len(fileTXT)} files from {file_path}")
        return fileTXT
        
    except Exception as e:
        logger.error(f"Error reading files from {file_path}: {str(e)}")
        return fileTXT

if __name__ == "__main__":
    # Test the function
    test_path = os.path.join(os.path.dirname(__file__), "files", "resumes")
    txt = read_files(test_path)
    print(f"Extracted {len(txt)} documents")
    for i, text in enumerate(txt[:3]):  # Show first 3 documents
        print(f"Document {i+1} preview: {text[:100]}...")