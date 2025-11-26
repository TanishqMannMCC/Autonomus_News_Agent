import streamlit as st
import os # <-- Add this
import sys # <-- Add this



# Import the functions from your main logic file (main.py)
# Ensure main.py defines these three things correctly.
# This is where the error likely happens if files/paths are wrong
try:
    from main import fetch_news_articles, get_summary, GEMINI_INITIALIZED
    st.write("Successfully imported from main.py") # <-- Add success message
except ImportError as e:
    st.error(f"ImportError: {e}")
    st.write("Please check:")
    st.write("1. Are 'app.py' and 'main.py' in the *exact same folder*?")
    st.write("2. Did you run 'streamlit run app.py' *from that specific folder* in your terminal?")
    st.stop() # Stop if import fails
except Exception as e:
    st.error(f"An unexpected error occurred during import: {e}")
    st.stop()


# --- STREAMLIT APP LAYOUT ---

st.title("📰 Autonomous News Agent")

# Check if Gemini was initialized correctly during import
if not GEMINI_INITIALIZED:
    st.error("Fatal Error: Could not initialize the Gemini summarization model. Please check API key and configuration in main.py or environment variables.")
    st.stop() # Stop the app if Gemini isn't working

# Get user input via Streamlit text box
query = st.text_input("Enter the news topic you are interested in:", placeholder="e.g., Artificial Intelligence, Tesla, India Elections")

# Add a button to trigger the search
search_button = st.button("Fetch & Summarize News")

# --- APP LOGIC (Triggered by button) ---

if search_button and query:
    # Use a spinner for better UX while fetching/summarizing
    with st.spinner(f'Fetching articles for "{query}" and generating summaries...'):
        # Call the fetching function from main.py
        news_result = fetch_news_articles(query)

        if news_result['status'] == 'ok':
            articles = news_result.get('articles', [])
            total_articles = news_result.get('total', 0)

            if articles:
                st.success(f"Found {total_articles} articles. Displaying summaries for the top {len(articles)}:")

                # Loop through and display the articles
                for i, article in enumerate(articles):
                    article_description = article.get('description')
                    article_title = article.get('title', 'No Title')
                    article_source = article.get('source', {}).get('name', 'Unknown Source')
                    article_url = article.get('url')

                    st.subheader(f"{i+1}. {article_title}")
                    st.write(f"**Source:** {article_source}")

                    # Call the summary function from main.py
                    summary = get_summary(article_description)
                    st.write(f"**Summary:** {summary}")

                    # Display URL as a clickable link
                    if article_url:
                        st.markdown(f"**URL:** [{article_url}]({article_url})")
                    else:
                        st.write("**URL:** Not available")
                    st.divider() # Adds a visual separator
            else:
                 st.info(f"Successfully searched, but no articles were found for '{query}'. Try a different topic.")

        else:
            # Display errors reported by fetch_news_articles
            st.error(f"Error fetching news: {news_result.get('message', 'Unknown error')}")

elif search_button and not query:
    st.warning("Please enter a topic to search for.")

