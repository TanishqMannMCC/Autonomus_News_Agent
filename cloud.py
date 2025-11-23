import requests
import json
import urllib3
import google.generativeai as genai
import os

# --- SETUP ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- SECURE KEY LOADING ---
# This looks for keys in the Environment (Cloud/GitHub) first.
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# --- Global variable for the Gemini model ---
gemini_model = None
GEMINI_INITIALIZED = False

def configure_gemini():
    """Configures and initializes the Gemini client and model."""
    global gemini_model, GEMINI_INITIALIZED
    
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        GEMINI_INITIALIZED = False
        return False

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        MODEL_NAME = 'gemini-2.5-flash'
        gemini_model = genai.GenerativeModel(MODEL_NAME)
        print(f"Successfully initialized Gemini model: {MODEL_NAME}")
        GEMINI_INITIALIZED = True
        return True
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        gemini_model = None
        GEMINI_INITIALIZED = False
        return False

# Initialize immediately
configure_gemini()

# --- HELPER FUNCTION (FOR GEMINI SUMMARIZATION) ---
def get_summary(text):
    global gemini_model

    if not GEMINI_INITIALIZED or gemini_model is None:
        return "Summary failed: Gemini model not initialized."

    if not text or not isinstance(text, str) or len(text.strip()) == 0:
        return "No summary available."

    prompt = f"Please summarize this news article description into a single, concise sentence: {text}"

    try:
        # Safety settings to prevent blocking
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        response = gemini_model.generate_content(prompt, safety_settings=safety_settings)

        if response.parts:
             return response.text.strip()
        else:
             return "Summary generation returned empty."

    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Summary failed to generate."


# --- NEWS FETCHING FUNCTION ---
def fetch_news_articles(query):
    if not NEWS_API_KEY:
        return {'status': 'error', 'message': 'NEWS_API_KEY not found.'}

    encoded_query = requests.utils.quote(query)
    url = f"https://newsapi.org/v2/everything?q={encoded_query}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"

    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'ok':
            return {'status': 'ok', 'articles': data.get('articles', [])[:5], 'total': data.get('totalResults', 0)}
        else:
            return {'status': 'error', 'message': f"NewsAPI Error: {data.get('message')}"}

    except Exception as e:
        return {'status': 'error', 'message': f"Error: {e}"}