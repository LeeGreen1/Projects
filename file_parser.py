from typing import IO
import docx
import pypdf

def parse_document(file: IO, file_type: str) -> str:
    """
    Extracts text from an uploaded file stream (DOCX or PDF).

    Args:
        file: The file-like object (stream) from the upload.
        file_type: The MIME type of the file (e.g., 'application/pdf').

    Returns:
        The extracted text as a single string, or an error message.
    """
    text = ""
    try:
        if 'wordprocessingml' in file_type or file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            document = docx.Document(file)
            for para in document.paragraphs:
                text += para.text + "\n"
            return text.strip()
        
        elif file_type == 'application/pdf':
            reader = pypdf.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
            
        else:
            return f"Error: Unsupported file type '{file_type}'"
            
    except Exception as e:
        return f"Error: Failed to parse the file. Reason: {e}"