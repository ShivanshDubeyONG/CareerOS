import re


class LinkExtractor:

    @staticmethod
    def extract(text: str):

        links = {
            "github": None,
            "linkedin": None,
            "leetcode": None,
            "kaggle": None,
            "huggingface": None,
            "medium": None,
            "portfolio": None,
            "other": [],
        }

        # Find actual URLs only
        urls = re.findall(
            r'https?://[^\s<>"\']+|www\.[^\s<>"\']+',
            text,
            flags=re.IGNORECASE
        )

        for url in urls:

            url = url.rstrip(".,;:)]}")

            lower_url = url.lower()

            if "github.com" in lower_url:
                links["github"] = url

            elif "linkedin.com" in lower_url:
                links["linkedin"] = url

            elif "leetcode.com" in lower_url:
                links["leetcode"] = url

            elif "kaggle.com" in lower_url:
                links["kaggle"] = url

            elif "huggingface.co" in lower_url:
                links["huggingface"] = url

            elif "medium.com" in lower_url:
                links["medium"] = url

            else:
                links["other"].append(url)

        return links


link_extractor = LinkExtractor()