import fitz
import docx


def load_pdf(file_path):

    text = ""

    doc = fitz.open(file_path)

    for page in doc:
        text += page.get_text()

    return text


def load_docx(file_path):

    text = ""

    doc = docx.Document(file_path)

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


def load_file(file_path, file_name):

    if file_name.lower().endswith(".pdf"):
        return load_pdf(file_path)

    elif file_name.lower().endswith(".docx"):
        return load_docx(file_path)

    else:
        raise ValueError("Unsupported file format")