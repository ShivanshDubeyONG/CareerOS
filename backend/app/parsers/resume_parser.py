import os
import fitz
from docx import Document


class ResumeParser:

    def extract_text(self, file_path: str) -> str:

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pdf":

            doc = fitz.open(file_path)

            text = ""

            for page in doc:
                text += page.get_text()

            doc.close()

            return text

        elif extension == ".docx":

            document = Document(file_path)

            text = ""

            for paragraph in document.paragraphs:
                text += paragraph.text + "\n"

            return text

        else:
            raise ValueError("Unsupported file type.")

    def extract_links(self, file_path: str):

        extension = os.path.splitext(file_path)[1].lower()

        if extension != ".pdf":
            return []

        doc = fitz.open(file_path)

        links = []

        for page in doc:

            page_links = page.get_links()

            for link in page_links:

                uri = link.get("uri")

                if uri:
                    links.append(uri)

        doc.close()

        return list(dict.fromkeys(links))


resume_parser = ResumeParser()