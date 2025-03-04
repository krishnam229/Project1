# IntelliSearch AI 🤖

## Overview
IntelliSearch AI is an advanced AI-powered research assistant that enables users to search and analyze news, academic papers, and web content efficiently. It integrates AI-driven analysis, credibility assessment, and intelligent summarization to enhance the search experience.

## Features
- **Multi-Source Search**: Fetch results from news sources, academic papers, and web content.
- **Region-Based Filtering**: Customize search results based on regional preferences.
- **Time Range Selection**: Filter results based on recency (Day, Week, Month, Year).
- **AI-Generated Summaries**: Extract key insights from articles.
- **Credibility Rating**: AI-driven evaluation of article credibility.
- **Text-to-Speech Output**: Converts AI responses into audio format.

## Tech Stack
- **Frontend**: Streamlit
- **Backend**: Python (Asyncio, Requests, HTTPX, BeautifulSoup)
- **AI Models**: Ollama (Llama 3.2), TensorFlow/Keras
- **Web Scraping**: Selenium, DuckDuckGo
- **Speech Synthesis**: Google Text-to-Speech (gTTS)

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Pip
- Virtual Environment (optional but recommended)

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/intellisearch-ai.git
   cd intellisearch-ai
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up Streamlit:
   ```sh
   streamlit run app.py
   ```

## Configuration
Modify search parameters in `app.py` under the sidebar section:
```python
result_count = st.number_input("📊 Result Limit", value=7, step=1, min_value=1, max_value=10)
region_code = st.text_input("🌍 Region Code", value="us-en")
temporal_filter = st.selectbox("⏳ Time Range", ["Past Day", "Past Week", "Past Month", "Past Year"], index=1)
```

## Usage
### Running IntelliSearch AI
Launch the application by running:
```sh
streamlit run app.py
```

### Performing a Search
1. Enter a query in the chat input.
2. Select the number of results and region code.
3. Choose a time range for filtering.
4. View AI-generated summaries and credibility ratings.
5. Optionally, enable AI-only mode to get responses without performing a search.

## Code Structure
```
intellisearch-ai/
│── deliverable2/
│   │── models/
│   │   │── model.keras
│   │   │── tokenizer.pkl
│   │── deliverable2.py
│   │── kr_hf_credibility_scorer.ipynb
│   │── requirements.txt
│   │── sample.csv
│   │── test_run_v2.py
│── logger/
│   │── __init__.py
│   │── app_logger.py
│── logs/
│── .gitignore
│── app.py                # Main application script
│── helper.py             # AI assistant, search functions, and web scraping
│── output.mp3            # Text-to-Speech output
│── README.md             # Documentation
│── requirements.txt      # Dependencies
```

## API and AI Integration
- **Ollama AI (Llama 3.2)**: Processes user queries and generates AI-driven responses.
- **Keras Model**: Evaluates article credibility based on content.
- **DuckDuckGo Search**: Retrieves news articles dynamically.
- **Google Text-to-Speech (gTTS)**: Converts AI responses to speech.

## Troubleshooting
- If Selenium fails to load pages, ensure ChromeDriver is up-to-date:
  ```sh
  pip install --upgrade webdriver-manager
  ```
- If AI responses are slow, increase processing power or optimize API calls.

## Contribution
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m "Added new feature"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a Pull Request.

## Contact
For queries or contributions, reach out at: km14292n@pace.edu

