import asyncio
import json
import os
import subprocess
import urllib
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import re
from bs4 import BeautifulSoup
from gtts import gTTS
from logger.app_logger import application_logger

# ============================ AI ASSISTANT CLASS ============================

class AIAssistant:
    """
    An AI assistant class that interfaces with a local Llama model via Ollama.
    """

    def __init__(self) -> None:
        """Initialize the AIAssistant instance with conversation memory."""
        self.conversation_log: List[Dict[str, str]] = [{"role": "system", "content": "You are a helpful assistant."}]
        application_logger.log_info("AI Assistant initialized", level="INFO")

    def generate_response(self, user_input: str) -> str:
        """
        Generate an AI response based on user input.
        """
        self.conversation_log.append({"role": "user", "content": user_input})
        application_logger.log_info("User input added to conversation log", level="INFO")

        # Format recent conversation history (limit to last 10 messages for efficiency)
        dialogue_history = "\n".join(
            f"{entry['role']}: {entry['content']}" for entry in self.conversation_log[-10:]
        )

        try:
            model_response = subprocess.run(
                ["ollama", "run", "llama3.2:latest"],
                input=dialogue_history,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )

            if model_response.returncode != 0:
                application_logger.log_error(f"Model execution error: {model_response.stderr}")
                return "I apologize, but I encountered an issue processing your request."

            ai_response = model_response.stdout.strip()  # It will already be a string due to `text=True`
            # if isinstance(ai_response, bytes):  # Only decode if it's in bytes (but it shouldn't be)
            #     ai_response = ai_response.decode('utf-8')
            self.conversation_log.append({"role": "assistant", "content": ai_response})
            application_logger.log_info("AI response generated", level="INFO")
            return ai_response

        except Exception as e:
            application_logger.log_error(f"Model query error: {e}")
            return "I apologize, but an error occurred while processing your request."

    async def evaluate_article_quality(self, article_title: str, article_content: str) -> str:
            """
            Evaluate and rate article quality based on title and content.
            """
            evaluation_prompt = f"""
            Analyze and rate this article on a scale of 1-5 based on:
            - Accuracy, clarity, and relevance.
            - Provide only a numeric rating (whole or half numbers allowed).
            
            **Title**: {article_title}
            **Content (first 1000 chars)**: {article_content[:1000]}
            
            **Example Valid Outputs:** `4`, `2.5`, `3`
            """

            try:
                model_response = subprocess.run(
                    ["ollama", "run", "llama3.2:latest"],
                    input=evaluation_prompt,
                    capture_output=True,
                    text=True,
                )

                if model_response.returncode != 0:
                    application_logger.log_error(f"Model execution error: {model_response.stderr}")
                    return "Error"

                rating = model_response.stdout.strip() 
                # if isinstance(rating, bytes):
                #     rating = rating.decode('utf-8')

                # Validate rating format (only 1-5 with optional .5)
                if rating.isdigit() and 1 <= int(rating) <= 5:
                    self.conversation_log.append({"role": "assistant", "content": rating})
                    application_logger.log_info(f"Article rated: {rating}", level="INFO")
                    return rating
                else:
                    application_logger.log_warning(f"Invalid rating received: {rating}")
                    return "Error"

            except Exception as e:
                application_logger.log_error(f"Model query error: {e}")
                return "Error"

# ============================ CONTENT EXTRACTION ============================

def extract_article_content(article_url: str) -> str:
    """
    Extract the main content from a news article URL.

    Args:
        article_url (str): The URL of the target article.

    Returns:
        str: Extracted article text content.
    """
    try:
        browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "Referer": "https://www.google.com"  # Simulate referring from a search engine
        }
        page_response = requests.get(article_url, headers=browser_headers, timeout=5)

        if page_response.status_code == 403:
            print(f"Access forbidden (403) for {article_url}")
            return None
        elif page_response.status_code != 200:
            print(f"Failed to fetch article from {article_url}. Status code: {page_response.status_code}")
            return None

        # page_content = BeautifulSoup(page_response.text, "html.parser")
        # text_blocks = page_content.find_all("p")

        # # Combine and clean text content
        # article_text = "\n".join([block.text.strip() for block in text_blocks if block.text.strip()])
        # application_logger.log_info(f"Content extracted from {article_url}", level="INFO")
        # return article_text
    
        page_content = page_response.text
        soup = BeautifulSoup(page_content, 'html.parser')
        paras = soup.find_all("p")
        # Extract the article content (assumes paragraphs are in <p> tags)
        article_text = "\n".join([p.text.strip() for p in paras if p.text.strip()])
        return article_text

    except Exception as e:
        application_logger.log_error(f"Content extraction error: {e}")
        return f"Content extraction error: {e}"



# ============================ NEWS SEARCH ============================

async def fetch_news_data(query: str, count: int = 5, region: str = "us-en", time_filter: str = "w") -> \
Dict[str, Any]:
    """
    Search and analyze news articles using DuckDuckGo with parallel processing.

    Args:
        query (str): Search terms.
        count (int): Number of articles to retrieve.
        region (str): Geographic region code (e.g., 'us-en', 'in-en').
        time_filter (str): Time range filter ('d'=day, 'w'=week, 'm'=month, 'y'=year).

    Returns:
        Dict[str, Any]: Processed news article data.
    """
    application_logger.log_info(f"Initiating news search for: {query}", level="INFO")

    search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}&kl={region}&df={time_filter}&ia=news"
    browser_headers = {"User-Agent": "Mozilla/5.0"}

    search_response = requests.get(search_url, headers=browser_headers)
    if search_response.status_code != 200:
        application_logger.log_error(f"Search request failed: {search_response.status_code}")
        return {"status": "error", "message": "Search request failed"}

    page_content = BeautifulSoup(search_response.text, "html.parser")
    article_elements = page_content.find_all("div", class_="result__body")

    async def process_single_article(element, index: int) -> Optional[Dict[str, Any]]:
        """Process and analyze a single news article."""
        try:
            title_element = element.find("a", class_="result__a")
            if not title_element:  # Check if None
                application_logger.log_warning(f"Title not found for result {index}")
                return None  # Skip this article

            headline = title_element.text.strip()
            raw_url = title_element.get("href", "")

            if not raw_url:  # Check if href exists
                application_logger.log_warning(f"URL missing for article: {headline}")
                return None  # Skip this article

            url_match = re.search(r"uddg=(https?%3A%2F%2F[^&]+)", raw_url)
            article_url = urllib.parse.unquote(url_match.group(1)) if url_match else "Unknown URL"

            summary_element = element.find("a", class_="result__snippet")
            article_summary = summary_element.text.strip() if summary_element else "Summary unavailable."

            article_body = extract_article_content(article_url)
            assistant = AIAssistant()
            quality_score = await assistant.evaluate_article_quality(headline, article_body)
            application_logger.log_info(f"Article processed: {headline}", level="INFO")

            return {
                "num": index + 1,
                "link": article_url,
                "title": headline,
                "summary": article_summary,
                "body": article_body,
                "rating": quality_score
            }

        except Exception as e:
            application_logger.log_error(f"Article processing error: {e}")
            return None

    processing_tasks = [process_single_article(element, idx) for idx, element in enumerate(article_elements[:count])]
    processed_articles = await asyncio.gather(*processing_tasks)

    valid_articles = [article for article in processed_articles if article is not None]

    if valid_articles:
        application_logger.log_info(f"Search completed with {len(valid_articles)} results", level="INFO")
        return {"status": "success", "results": valid_articles}
    else:
        application_logger.log_error("No valid articles found")
        return {"status": "error", "message": "No valid articles found"}


# ============================ UTILITY FUNCTIONS ============================

def get_current_year() -> int:
    """Get the current year as an integer."""
    return datetime.now().year


def text_to_speech(input_text: str) -> None:
    """Convert text to speech and save as audio file."""
    try:
        speech_generator = gTTS(text=input_text, lang="en")
        speech_generator.save("output.mp3")
        application_logger.log_info("Text successfully converted to audio", level="INFO")
    except Exception as e:
        application_logger.log_error(f"Audio conversion error: {e}")