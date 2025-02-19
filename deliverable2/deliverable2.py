"""
deliverable2.py
"""
import requests
import string
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

class URLValidator:
    """
    A robust URL validation class that evaluates the credibility of a webpage
    using multiple factors: domain trust, content relevance, fact-checking, bias detection, and citations.
    """
    def __init__(self, serpapi_key=None):
        self.serpapi_key = serpapi_key
        # Load models once to avoid redundant API calls
        self.similarity_model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
        self.fake_news_classifier = pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
        self.sentiment_analyzer = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment")

    def fetch_page_content(self, url: str) -> str:
        """Fetches and extracts text content from the given URL."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            content = " ".join([p.text for p in soup.find_all("p")])
            return content if content else ""
        except requests.RequestException:
            return ""

    def get_domain_trust(self, content: str) -> int:
        """Determines the domain trust score using fake news detection."""
        if not content:
            return 50  # Default neutral score
        result = self.fake_news_classifier(content[:512])[0]  # Limit text length
        return 100 if result["label"] == "REAL" else 30 if result["label"] == "FAKE" else 50

    def compute_similarity_score(self, user_query: str, content: str) -> int:
        """Computes semantic similarity between user query and page content."""
        if not content:
            return 0
        similarity = util.pytorch_cos_sim(self.similarity_model.encode(user_query), self.similarity_model.encode(content)).item()
        return int(similarity * 100)

    def check_facts(self, content: str) -> int:
        """Cross-checks extracted content using Google's Fact Check API."""
        if not content:
            return 50
        api_url = f"https://toolbox.google.com/factcheck/api/v1/claimsearch?query={content[:200]}"
        try:
            response = requests.get(api_url)
            data = response.json()
            return 80 if "claims" in data and data["claims"] else 40
        except:
            return 50

    def check_google_scholar(self, url: str) -> int:
        """Checks Google Scholar citations using SerpAPI."""
        params = {"q": url, "engine": "google_scholar", "api_key": self.serpapi_key}
        try:
            response = requests.get("https://serpapi.com/search", params=params)
            data = response.json()
            return min(len(data.get("organic_results", [])) * 10, 100)
        except:
            return 0

    def detect_bias(self, content: str) -> int:
        """Uses NLP sentiment analysis to detect potential bias in content."""
        if not content:
            return 50
        sentiment_result = self.sentiment_analyzer(content[:512])[0]
        return 100 if sentiment_result["label"] == "POSITIVE" else 50 if sentiment_result["label"] == "NEUTRAL" else 30

    def get_star_rating(self, score: float) -> tuple:
        """Converts a score (0-100) into a 1-5 star rating."""
        stars = max(1, min(5, round(score / 20)))
        return stars, "⭐" * stars

    def generate_explanation(self, domain_trust, similarity_score, fact_check_score, bias_score, citation_score) -> str:
        """Generates a human-readable explanation for the credibility score."""
        reasons = []
        if domain_trust < 50:
            reasons.append("Low domain authority detected.")
        if similarity_score < 50:
            reasons.append("Content is not highly relevant to the query.")
        if fact_check_score < 50:
            reasons.append("Limited fact-checking verification available.")
        if bias_score < 50:
            reasons.append("Potential bias detected in content.")
        if citation_score < 30:
            reasons.append("Few or no citations found for this content.")
        return " ".join(reasons) if reasons else "This source is highly credible and relevant."

    def rate_url_validity(self, user_query: str, url: str) -> dict:
        """Evaluates the validity of a webpage."""
        content = self.fetch_page_content(url)
        
        domain_trust = self.get_domain_trust(content)
        similarity_score = self.compute_similarity_score(user_query, content)
        fact_check_score = self.check_facts(content)
        bias_score = self.detect_bias(content)
        citation_score = self.check_google_scholar(url)

        final_score = (
            (0.3 * domain_trust) +
            (0.3 * similarity_score) +
            (0.2 * fact_check_score) +
            (0.1 * bias_score) +
            (0.1 * citation_score)
        )

        stars, icon = self.get_star_rating(final_score)
        explanation = self.generate_explanation(domain_trust, similarity_score, fact_check_score, bias_score, citation_score)

        return {
            "raw_scores": {
                "Domain Trust": domain_trust,
                "Content Relevance": similarity_score,
                "Fact-Check Score": fact_check_score,
                "Bias Score": bias_score,
                "Citation Score": citation_score,
                "Final Validity Score": final_score
            },
            "stars": {
                "score": stars,
                "icon": icon
            },
            "explanation": explanation
        }