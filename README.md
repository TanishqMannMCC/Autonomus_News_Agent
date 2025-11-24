# Autonomus_News_Agent

Autonomous News Agent

An intelligent news aggregator that fetches articles using NewsAPI and generates concise AI summaries using Google's Gemini model. It operates in two modes: an interactive web app and a fully automated daily email agent.

Features

Interactive Mode: A Streamlit web app to search for news on any topic and get instant AI summaries.

Autonomous Mode: A scheduled background agent that fetches news for configured topics and emails summaries daily.

AI Power: Uses Google Gemini 1.5 Flash for high-quality abstractive summarization.

Cloud Hosted: Runs automatically on GitHub Actions (Serverless).

Project Structure

main.py: Core logic for fetching news and generating summaries.

app.py: Streamlit user interface.

scheduled_multi_user_agent.py: Script for the automated agent.

users_config.json: Configuration file for users, topics, and email addresses.

Setup & Installation

Clone the repository.

Install dependencies:

pip install -r requirements.txt
pip install streamlit python-dotenv


Set up API keys (NewsAPI, Gemini) and Email credentials.

Usage

Run Interactive App:

streamlit run app.py


Run Automated Agent Manually:

python scheduled_multi_user_agent.py


Automation

The project uses GitHub Actions to run the agent daily at 08:00 UTC. Configuration is managed via users_config.json and GitHub Secrets.
