import re

from app.extractors.resume_extractor import resume_extractor
from app.parsers.resume_parser import resume_parser
from app.schemas.resume_schema import ResumeLinks


class ResumeExtractionService:

    def extract(self, file_path: str):

        text = resume_parser.extract_text(file_path)

        resume = resume_extractor.extract(text)

        pdf_links = resume_parser.extract_links(file_path)

        resume.links = self.classify_links(pdf_links)

        return resume

    @staticmethod
    def clean_url(url: str):

        if not url:
            return None

        # Remove Markdown link formatting
        markdown_match = re.match(
            r"\[.*?\]\((https?://.*?)\)",
            url,
            re.IGNORECASE,
        )

        if markdown_match:
            url = markdown_match.group(1)

        url = url.strip()

        return url

    @classmethod
    def classify_links(cls, urls):

        links = ResumeLinks()

        for raw_url in urls:

            url = cls.clean_url(raw_url)

            if not url:
                continue

            lower_url = url.lower()

            # Ignore contact links here.
            # Email and phone are already extracted separately.
            if lower_url.startswith("mailto:"):
                continue

            if lower_url.startswith("tel:"):
                continue

            # GitHub
            if "github.com" in lower_url:

                # Main profile
                if re.match(
                    r"https?://(?:www\.)?github\.com/[^/]+/?$",
                    url,
                    re.IGNORECASE,
                ):
                    if links.github is None:
                        links.github = url

                # Repository/project
                else:
                    if url not in links.github_projects:
                        links.github_projects.append(url)

            # LinkedIn
            elif "linkedin.com" in lower_url:

                if links.linkedin is None:
                    links.linkedin = url

            # LeetCode
            elif "leetcode.com" in lower_url:

                if links.leetcode is None:
                    links.leetcode = url

            # Kaggle
            elif "kaggle.com" in lower_url:

                if links.kaggle is None:
                    links.kaggle = url

            # HuggingFace
            elif "huggingface.co" in lower_url:

                if links.huggingface is None:
                    links.huggingface = url

            # Medium
            elif "medium.com" in lower_url:

                if links.medium is None:
                    links.medium = url

            else:

                if url not in links.other:
                    links.other.append(url)

        return links


resume_extraction_service = ResumeExtractionService()