import asyncio
import json
import os
import pickle
import subprocess
import time
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional
import httpx
import keras
import numpy as np
import requests
import re
from bs4 import BeautifulSoup
from gtts import gTTS
from huggingface_hub import hf_hub_download
from keras.utils import pad_sequences
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures
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

    async def rate_article_credibility(self, article_title: str, article_content: str) -> str:
        """
        Rate the credibility of an article using a locally created model.

        Args:
            article_title (str): The title of the article.
            article_content (str): The full content of the article.

        Returns:
            str: A credibility rating based on the model's prediction.
        """
        try:
            # Load the model and tokenizer
            model_path: str = hf_hub_download(repo_id="krishnam229/Deliverable3", filename="model.keras")
            tokenizer_path: str = hf_hub_download(repo_id="krishnam229/Deliverable3", filename="tokenizer.pkl")

            new_model = keras.models.load_model(model_path)
            with open(tokenizer_path, "rb") as f:
                tokenizer = pickle.load(f)

            # Preprocess the input data
            max_length: int = new_model.input_shape[0][1]
            X_text: List[List[int]] = tokenizer.texts_to_sequences([article_title])
            X_text = pad_sequences(X_text, maxlen=max_length, padding='post')
            X_func_rating: np.ndarray = np.array([5]).reshape(-1, 1)  # Dummy rating for example

            # Make predictions
            predictions: np.ndarray = new_model.predict({"text_input": X_text, "func_rating_input": X_func_rating})
            prediction: int = np.argmax(predictions, axis=1)[0]

            application_logger.log_info(f"Article credibility rated: {prediction}", level="INFO")
            return str(prediction)

        except Exception as e:
            application_logger.log_error(f"Error rating article credibility: {e}")
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
        retries: int = 3
        for attempt in range(retries):
            try:
                response: requests.Response = requests.get(article_url, headers=browser_headers, timeout=10)
                if response.status_code == 403:
                    application_logger.log_error(f"Access forbidden to article: {response.status_code}")
                    return "Access forbidden to article."
                if response.status_code != 200:
                    application_logger.log_error(f"Failed to fetch article: {response.status_code}")
                    return "Failed to fetch article."

                soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
                paragraphs: List[BeautifulSoup] = soup.find_all("p")

                # Extract and return cleaned text
                article_content: str = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
                application_logger.log_info(f"Article content extracted from {article_url}", level="INFO")
                return article_content

            except requests.exceptions.Timeout:
                application_logger.log_warning(f"Timeout occurred while fetching article: {article_url}, attempt {attempt + 1}")
                if attempt < retries - 1:
                    time.sleep(2)  # Wait before retrying
                    continue
                return "Error: Timeout occurred while fetching article."

    except Exception as e:
        application_logger.log_error(f"Error extracting article content: {e}")
        return f"Error extracting article content: {e}"

        return "Failed to fetch article after multiple attempts."

# ============================ NEWS SEARCH ============================

async def fetch_news_data(query: str, count: int = 5, region: str = "us-en", time_filter: str = "w") -> Dict[str, Any]:
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

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without UI
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")  # Disable push notifications
    chrome_options.add_argument("--disable-popup-blocking") # Prevent popups interfering

    
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")
    #chrome_options.add_argument("--user-data-dir=C:\\temp\\selenium_profile")

    driver: webdriver.Chrome = webdriver.Chrome(options=chrome_options)

    duckduckgo_news_url: str = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}&kl={region}&df={time_filter}&ia=news"
    driver.get(duckduckgo_news_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "result__body")))
    soup: BeautifulSoup = BeautifulSoup(driver.page_source, "html.parser")
    search_results: List[BeautifulSoup] = soup.find_all("div", class_="result__body")

    async def process_article(result: BeautifulSoup, index: int) -> Optional[Dict[str, Any]]:
        """
        Process a single search result and extract relevant information.

        Args:
            result (BeautifulSoup): The search result to process.
            index (int): The index of the search result.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the extracted information, or None if an error occurs.
        """
        try:
            title_tag: Optional[BeautifulSoup] = result.find("a", class_="result__a")
            if not title_tag:
                application_logger.log_warning(f"Title tag not found for result index {index}")
                return None

            title: str = title_tag.text.strip()
            raw_link: str = title_tag["href"]

            match: Optional[re.Match] = re.search(r"uddg=(https?%3A%2F%2F[^&]+)", raw_link)
            link: str = urllib.parse.unquote(match.group(1)) if match else "Unknown Link"

            snippet_tag: Optional[BeautifulSoup] = result.find("a", class_="result__snippet")
            summary: str = snippet_tag.text.strip() if snippet_tag else "No summary available."

            article_content: str = extract_article_content(link)

            bot: AIAssistant = AIAssistant()

            # Rate the credibility of the article
            rating: str = await bot.rate_article_credibility(title, article_content)

            application_logger.log_info(f"Processed article: {title}", level="INFO")

            return {
                "num": index + 1,
                "link": link,
                "title": title,
                "summary": summary,
                "body": article_content,
                "rating": rating
            }
        except Exception as e:
            application_logger.log_error(f"Error processing article: {e}")
            return None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks: List[concurrent.futures.Future] = [executor.submit(process_article, result, index) for index, result in enumerate(search_results[:count])]
        extracted_results: List[Optional[Dict[str, Any]]] = [task.result() for task in concurrent.futures.as_completed(tasks)]

    driver.quit()

    extracted_results = [res for res in extracted_results if res is not None]

    if extracted_results:
        application_logger.log_info(f"News search completed successfully with {len(extracted_results)} results", level="INFO")
        return {"status": "success", "results": extracted_results}
    else:
        application_logger.log_error("No valid news search results found")
        return {"status": "error", "message": "No valid news search results found"}


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