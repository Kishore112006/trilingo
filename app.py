from flask import Flask, render_template, request, jsonify
import requests
from concurrent.futures import ThreadPoolExecutor

from database import (
    save_history,
    get_history,
    delete_history
)

app = Flask(__name__)


# ==========================================
# LANGUAGE DETECTION
# ==========================================

def detect_language(text):

    for char in text:

        # Telugu Unicode
        if '\u0C00' <= char <= '\u0C7F':
            return "Telugu"

        # Hindi Unicode
        if '\u0900' <= char <= '\u097F':
            return "Hindi"

    return "English"


# ==========================================
# TRANSLATION
# ==========================================

def translate(text, source, target):

    try:

        url = "https://api.mymemory.translated.net/get"

        params = {
            "q": text,
            "langpair": f"{source}|{target}"
        }

        response = requests.get(
            url,
            params=params,
            timeout=8
        )

        if response.status_code != 200:
            return "Translation unavailable"

        data = response.json()

        result = data.get(
            "responseData",
            {}
        ).get(
            "translatedText",
            ""
        )

        if not result:
            return "Translation unavailable"

        return result

    except Exception as e:

        print("Translation error:", e)

        return "Translation unavailable"


# ==========================================
# TRANSLATE TWO LANGUAGES AT SAME TIME
# ==========================================

def translate_parallel(text, source, targets):

    results = {}

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:

        futures = {}

        for target in targets:

            futures[target] = executor.submit(
                translate,
                text,
                source,
                target
            )

        for target, future in futures.items():

            try:

                results[target] = future.result(
                    timeout=10
                )

            except Exception:

                results[target] = "Translation unavailable"

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


    # Detect language

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
            "en",
            ["te", "hi"]
        )

        telugu = translations.get(
            "te",
            "Translation unavailable"
        )

        hindi = translations.get(
            "hi",
            "Translation unavailable"
        )


    # ======================================
    # TELUGU
    # ======================================

    elif language == "Telugu":

        telugu = word

        translations = translate_parallel(
            word,
            "te",
            ["en", "hi"]
        )

        english = translations.get(
            "en",
            "Translation unavailable"
        )

        hindi = translations.get(
            "hi",
            "Translation unavailable"
        )


    # ======================================
    # HINDI
    # ======================================

    elif language == "Hindi":

        hindi = word

        translations = translate_parallel(
            word,
            "hi",
            ["en", "te"]
        )

        english = translations.get(
            "en",
            "Translation unavailable"
        )

        telugu = translations.get(
            "te",
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
    # RESULT
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