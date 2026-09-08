from flask import Flask, render_template, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from sarvamai import SarvamAI
import os

from database import (
    save_history,
    get_history,
    delete_history
)


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# FLASK APP
# ==========================================

app = Flask(__name__)


# ==========================================
# SARVAM CLIENT
# ==========================================

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

if not SARVAM_API_KEY:
    print("WARNING: SARVAM_API_KEY is not set.")

sarvam_client = (
    SarvamAI(api_subscription_key=SARVAM_API_KEY)
    if SARVAM_API_KEY
    else None
)


# ==========================================
# LANGUAGE DETECTION
# ==========================================

def detect_language(text):

    for char in text:

        # Telugu
        if '\u0C00' <= char <= '\u0C7F':
            return "Telugu"

        # Hindi / Devanagari
        if '\u0900' <= char <= '\u097F':
            return "Hindi"

    return "English"


# ==========================================
# LANGUAGE CODES
# ==========================================

LANGUAGE_CODES = {
    "English": "en-IN",
    "Telugu": "te-IN",
    "Hindi": "hi-IN"
}


# ==========================================
# SARVAM TRANSLATION
# ==========================================

def translate(text, source_language, target_language):

    try:

        if not sarvam_client:
            return "Translation unavailable"

        source_code = LANGUAGE_CODES[source_language]
        target_code = LANGUAGE_CODES[target_language]

        response = sarvam_client.text.translate(
            input=text,
            source_language_code=source_code,
            target_language_code=target_code,
            model="sarvam-translate:v1"
        )

        translated_text = response.translated_text

        if not translated_text:
            return "Translation unavailable"

        return translated_text.strip()

    except Exception as e:

        print("Sarvam translation error:", e)

        return "Translation unavailable"


# ==========================================
# PARALLEL TRANSLATION
# ==========================================

def translate_parallel(text, source_language, target_languages):

    results = {}

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:

        futures = {}

        for target_language in target_languages:

            futures[target_language] = executor.submit(
                translate,
                text,
                source_language,
                target_language
            )

        for target_language, future in futures.items():

            try:

                results[target_language] = future.result(
                    timeout=15
                )

            except Exception as e:

                print(
                    "Translation failed:",
                    e
                )

                results[target_language] = (
                    "Translation unavailable"
                )

    return results


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================================
# RESULT PAGE
# ==========================================

@app.route("/result")
def result_page():

    return render_template(
        "result.html"
    )


# ==========================================
# SEARCH
# ==========================================

@app.route(
    "/api/search",
    methods=["POST"]
)
def search():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "Invalid request."
        })


    word = data.get(
        "word",
        ""
    ).strip()


    if not word:

        return jsonify({
            "success": False,
            "message": "Please enter a word."
        })


    # ======================================
    # DETECT LANGUAGE
    # ======================================

    language = detect_language(word)


    english = ""
    telugu = ""
    hindi = ""


    # ======================================
    # ENGLISH
    # ======================================

    if language == "English":

        english = word

        translations = translate_parallel(
            word,
            "English",
            ["Telugu", "Hindi"]
        )

        telugu = translations.get(
            "Telugu",
            "Translation unavailable"
        )

        hindi = translations.get(
            "Hindi",
            "Translation unavailable"
        )


    # ======================================
    # TELUGU
    # ======================================

    elif language == "Telugu":

        telugu = word

        translations = translate_parallel(
            word,
            "Telugu",
            ["English", "Hindi"]
        )

        english = translations.get(
            "English",
            "Translation unavailable"
        )

        hindi = translations.get(
            "Hindi",
            "Translation unavailable"
        )


    # ======================================
    # HINDI
    # ======================================

    elif language == "Hindi":

        hindi = word

        translations = translate_parallel(
            word,
            "Hindi",
            ["English", "Telugu"]
        )

        english = translations.get(
            "English",
            "Translation unavailable"
        )

        telugu = translations.get(
            "Telugu",
            "Translation unavailable"
        )


    # ======================================
    # SAVE HISTORY
    # ======================================

    try:

        save_history(
            word,
            language,
            english,
            telugu,
            hindi
        )

    except Exception as e:

        print(
            "Database error:",
            e
        )


    # ======================================
    # RETURN RESULT
    # ======================================

    return jsonify({

        "success": True,

        "searched_word": word,

        "detected_language": language,

        "english": english,

        "telugu": telugu,

        "hindi": hindi

    })


# ==========================================
# HISTORY
# ==========================================

@app.route("/api/history")
def history():

    try:

        data = get_history()

        return jsonify({

            "success": True,

            "history": data

        })

    except Exception as e:

        print(
            "History error:",
            e
        )

        return jsonify({

            "success": False,

            "history": []

        })


# ==========================================
# DELETE HISTORY
# ==========================================

@app.route(
    "/api/history/delete",
    methods=["DELETE"]
)
def delete_history_api():

    try:

        delete_history()

        return jsonify({

            "success": True,

            "message":
            "History deleted successfully."

        })

    except Exception as e:

        print(
            "Delete error:",
            e
        )

        return jsonify({

            "success": False,

            "message":
            "Could not delete history."

        })


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )