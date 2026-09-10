from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from sarvamai import SarvamAI
import os
import re

from database import (
    save_history,
    get_history,
    delete_history,
    create_table
)


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# SARVAM AI
# =========================================================

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

if not SARVAM_API_KEY:
    print("WARNING: SARVAM_API_KEY is not set!")

sarvam_client = None

if SARVAM_API_KEY:
    try:
        sarvam_client = SarvamAI(
            api_subscription_key=SARVAM_API_KEY
        )
        print("Sarvam AI connected! ✅")

    except Exception as e:
        print("Sarvam AI connection failed:", e)


# =========================================================
# LANGUAGE CODES
# =========================================================

LANGUAGE_CODES = {
    "English": "en-IN",
    "Telugu": "te-IN",
    "Hindi": "hi-IN"
}


# =========================================================
# LANGUAGE DETECTION
# =========================================================

def detect_language(text):

    # Telugu Unicode range
    if re.search(r"[\u0C00-\u0C7F]", text):
        return "Telugu"

    # Hindi Unicode range
    if re.search(r"[\u0900-\u097F]", text):
        return "Hindi"

    # Otherwise English
    return "English"


# =========================================================
# TRANSLATE TEXT
# =========================================================

def translate_text(text, source_language, target_language):

    # Same language
    if source_language == target_language:
        return text

    if not sarvam_client:
        return "Translation service unavailable"

    try:

        source_code = LANGUAGE_CODES[source_language]
        target_code = LANGUAGE_CODES[target_language]

        response = sarvam_client.text.translate(
            input=text,
            source_language_code=source_code,
            target_language_code=target_code,
            model="sarvam-translate:v1"
        )

        # Sarvam SDK response
        if hasattr(response, "translated_text"):
            return response.translated_text

        if isinstance(response, dict):
            return response.get(
                "translated_text",
                "Translation unavailable"
            )

        return str(response)

    except Exception as e:

        print(
            f"Translation error "
            f"{source_language} -> {target_language}:",
            e
        )

        return "Translation unavailable"


# =========================================================
# TRANSLATE INTO ALL THREE LANGUAGES
# =========================================================

def translate_all(text, detected_language):

    languages = [
        "English",
        "Telugu",
        "Hindi"
    ]

    results = {
        "English": "",
        "Telugu": "",
        "Hindi": ""
    }

    # Translate two languages in parallel
    target_languages = [
        language
        for language in languages
        if language != detected_language
    ]

    results[detected_language] = text

    with ThreadPoolExecutor(max_workers=2) as executor:

        futures = {
            language: executor.submit(
                translate_text,
                text,
                detected_language,
                language
            )
            for language in target_languages
        }

        for language, future in futures.items():

            try:
                results[language] = future.result()

            except Exception as e:

                print(
                    f"Error translating to {language}:",
                    e
                )

                results[language] = "Translation unavailable"

    return results


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# RESULT PAGE
# =========================================================

@app.route("/result")
def result():

    return render_template("result.html")


# =========================================================
# SEARCH API
# =========================================================

@app.route("/api/search", methods=["POST"])
def search():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data received"
            }), 400

        word = data.get("word", "").strip()

        if not word:

            return jsonify({
                "success": False,
                "error": "Please enter a word"
            }), 400

        # Sarvam supports up to 2000 characters
        if len(word) > 2000:

            return jsonify({
                "success": False,
                "error": "Please enter 2000 characters or less"
            }), 400

        # Detect language
        detected_language = detect_language(word)

        print(
            f"Searching: {word} | "
            f"Detected: {detected_language}"
        )

        # Translate
        translations = translate_all(
            word,
            detected_language
        )

        english = translations["English"]
        telugu = translations["Telugu"]
        hindi = translations["Hindi"]

        # =================================================
        # SAVE HISTORY
        # =================================================

        try:

            save_history(
                word,
                detected_language,
                english,
                telugu,
                hindi
            )

            print("History saved successfully! ✅")

        except Exception as e:

            # Don't stop search if history saving fails
            print(
                "History save failed:",
                e
            )

        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "success": True,

            "searched_word": word,

            "detected_language":
                detected_language,

            "english":
                english,

            "telugu":
                telugu,

            "hindi":
                hindi
        })

    except Exception as e:

        print(
            "Search API error:",
            e
        )

        return jsonify({

            "success": False,

            "error":
                "Something went wrong. Please try again."

        }), 500


# =========================================================
# HISTORY API
# =========================================================

@app.route("/api/history", methods=["GET"])
def history():

    try:

        history_data = get_history()

        # Convert datetime to string
        for item in history_data:

            if item.get("searched_at"):

                item["searched_at"] = \
                    item["searched_at"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

        return jsonify({

            "success": True,

            "history":
                history_data

        })

    except Exception as e:

        print(
            "History loading error:",
            e
        )

        return jsonify({

            "success": False,

            "error":
                "Unable to load history",

            "history":
                []

        }), 500


# =========================================================
# DELETE HISTORY API
# =========================================================

@app.route("/api/history/delete", methods=["POST"])
def clear_history():

    try:

        delete_history()

        print(
            "History deleted successfully! ✅"
        )

        return jsonify({

            "success": True,

            "message":
                "History cleared successfully"

        })

    except Exception as e:

        print(
            "History delete error:",
            e
        )

        return jsonify({

            "success": False,

            "error":
                "Unable to delete history"

        }), 500


# =========================================================
# CREATE DATABASE TABLE
# =========================================================

try:

    create_table()

    print(
        "Database history table ready! ✅"
    )

except Exception as e:

    print(
        "Database initialization failed:",
        e
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )