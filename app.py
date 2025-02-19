import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any

import streamlit as st

from helper import AIAssistant, get_current_year, text_to_speech, fetch_news_data

# ============================ UI CONFIGURATION ============================

st.set_page_config(layout="wide")  # Configure page layout for better visibility
st.title("IntelliSearch AI 🤖")  # Application header

# ============================ CONFIGURATION PANEL ============================

with st.sidebar:
    with st.expander("📖 User Guide"):
        st.markdown(
            """
            ## 🧠 IntelliSearch AI 🤖 - Smart Research Companion
            Welcome to **IntelliSearch**, your intelligent research companion powered by 
            advanced AI to discover news, trends, and insights across multiple sources.

            ### 🔹 Usage Guide:
            1. **📌 Select Data Source**  
               - Pick your preferred source type (News, Academic Papers, Web Content).
            2. **📊 Result Count**  
               - Specify number of results (1-10).
            3. **🌍 Regional Settings**  
               - Set geographical preference for results.  
               *(Example: "us-en" for USA, "in-en" for India)*
            4. **⏳ Time Range**  
               - Filter content by recency:  
                 - **Past Day** 🕐 (Latest Updates)  
                 - **Past Week** 🗓 (Current Trends)  
                 - **Past Month** 📅 (Significant Events)  
                 - **Past Year** 📆 (Comprehensive Research)  
            5. **💬 Results Overview & Conversation Log**  
               - Interactive results display.  
               - AI-powered summary with source citations.

            ---

            ### 🔹 Sample Queries:
            **📰 News Discovery**
            - *"Latest developments in AI technology"*
            - *"Current space exploration updates"*

            **📖 Academic Research**
            - *"Top-cited quantum computing papers"*
            - *"Deep learning progress in 2024"*

            **🌍 Regional Updates**
            - *"Silicon Valley startup news"*
            - *"Current UK political landscape"*

            **⚡ AI Analysis**
            - *"Crypto market analysis summary"*
            - *"Weekly AI industry insights with context"*

            """
        )

    # Search configuration inputs
    result_count: int = st.number_input("📊 Result Limit", value=7, step=1, min_value=1, max_value=10)
    region_code: str = st.text_input("🌍 Region Code (e.g., us-en, in-en)", value="us-en")
    temporal_filter: str = st.selectbox(
        "⏳ Time Range",
        ["Past Day", "Past Week", "Past Month", "Past Year"],
        index=1
    )

    # Map user-friendly time filters to API parameters
    time_period_map: Dict[str, str] = {"Past Day": "d", "Past Week": "w", "Past Month": "m", "Past Year": "y"}
    temporal_filter = time_period_map[temporal_filter]

    ai_only_mode: bool = st.checkbox("💬 AI Mode (Skip Search)")

    # Session reset option
    if st.button("🧹 Reset Session"):
        st.session_state.messages = []
        st.rerun()

    # Dynamic copyright footer
    st.markdown(f"<h6>📅 Copyright © 2010-{get_current_year()} Present</h6>", unsafe_allow_html=True)

# ============================ CONVERSATION MANAGEMENT ============================

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, str]] = [] # type: ignore

# Validate message format
if not isinstance(st.session_state.messages, list) or not all(isinstance(msg, dict) for msg in st.session_state.messages):
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ============================ QUERY PROCESSING ============================

# Handle user input
if query := st.chat_input("What would you like to know?"):
    st.chat_message("user").markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    # Initialize results table
    results_table: str = "**No matching results found.**"

    try:
        with st.spinner("Processing request..."):
            if ai_only_mode:
                search_response: str = "<empty>"
            else:
                # Execute search query
                search_output: Dict[str, Any] = asyncio.run(
                    fetch_news_data(query=query, region=region_code, count=result_count, time_filter=temporal_filter)
                )

                if search_output["status"] == "success":
                    markdown_results: List[Dict[str, Any]] = search_output["results"]
                    search_response = f"Search results:\n{markdown_results}"

                    def sanitize_title(raw_title: str) -> str:
                        """
                        Formats title for proper display by replacing delimiter characters.

                        Args:
                            raw_title (str): Original title text.

                        Returns:
                            str: Formatted title suitable for display.
                        """
                        return raw_title.replace("|", " - ").strip()

                    def format_rating(raw_rating: str) -> str:
                        """
                        Creates visual star rating representation.

                        Args:
                            raw_rating (str): Numerical rating value.

                        Returns:
                            str: Star-based rating display (⭐ and ⭐½).
                        """
                        try:
                            rating_val: float = float(raw_rating)
                            full_count: int = int(rating_val)
                            has_half: str = "⭐½" if (rating_val - full_count) >= 0.5 else ""
                            return "⭐" * full_count + has_half
                        except ValueError:
                            return "⭐"

                    # Construct results table
                    results_table = "| # | Title | Rating | Summary |\n|---|------|--------|---------|\n"

                    for item in markdown_results:
                        clean_title = sanitize_title(item['title'])
                        raw_rating = str(item.get('rating', '⭐')).strip()

                        if raw_rating.replace('.', '', 1).isdigit():
                            rating_display = format_rating(raw_rating)
                        else:
                            rating_display = "⭐"

                        if item.get('link', '').startswith("http"):
                            title_display = f"[{clean_title}]({item['link']})"
                        else:
                            title_display = clean_title

                        summary_text = item.get('summary', '').strip()
                        truncated_summary = summary_text[:100] + "..." if len(summary_text) > 100 else summary_text

                        results_table += f"| {item['num']} | {title_display} | {rating_display} | {truncated_summary} |\n"
            
            # Generate AI response
            assistant = AIAssistant()
            assistant.history = st.session_state.messages.copy()
            response = assistant.generate_response(
                f"""
                Query: {query}
                Results: {search_response}
                Context: {[item['summary'] for item in search_output.get("results", [])]}
                Use search results if available, otherwise base response on conversation history.
                """
            )

    except Exception as e:
        st.warning(f"Search error occurred: {e}")
        response = "Service temporarily unavailable. Please try again."

    # Generate audio response
    text_to_speech(response)

    # Display response
    with st.chat_message("assistant"):
        st.markdown(response, unsafe_allow_html=True)
        st.audio("output.mp3", format="audio/mpeg", loop=True)
        with st.expander("Source References:", expanded=True):
            st.markdown(results_table, unsafe_allow_html=True)

    # Update conversation log
    complete_response: str = f"{response}\n\n{results_table}"
    st.session_state.messages.append({"role": "assistant", "content": complete_response})