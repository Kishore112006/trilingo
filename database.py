from dotenv import load_dotenv
import os
import mysql.connector


# ==========================================
# LOAD .ENV FILE
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(ENV_FILE)


# ==========================================
# MYSQL CONNECTION
# ==========================================

def get_connection():

    password = os.getenv("DB_PASSWORD")

    connection = mysql.connector.connect(
        host=os.getenv(
            "DB_HOST",
            "localhost"
        ),

        user=os.getenv(
            "DB_USER",
            "root"
        ),

        password=password,

        database=os.getenv(
            "DB_NAME",
            "tridict"
        )
    )

    return connection


# ==========================================
# SAVE SEARCH HISTORY
# ==========================================

def save_history(
    word,
    language,
    english,
    telugu,
    hindi
):

    connection = get_connection()

    cursor = connection.cursor()

    sql = """
        INSERT INTO history
        (
            searched_word,
            detected_language,
            english,
            telugu,
            hindi
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        word,
        language,
        english,
        telugu,
        hindi
    )

    cursor.execute(
        sql,
        values
    )

    connection.commit()

    cursor.close()
    connection.close()


# ==========================================
# GET HISTORY
# ==========================================

def get_history():

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    sql = """
        SELECT
            id,
            searched_word,
            detected_language,
            english,
            telugu,
            hindi,
            searched_at
        FROM history
        ORDER BY searched_at DESC
        LIMIT 20
    """

    cursor.execute(sql)

    history = cursor.fetchall()

    cursor.close()
    connection.close()

    return history


# ==========================================
# DELETE HISTORY
# ==========================================

def delete_history():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM history"
    )

    connection.commit()

    cursor.close()
    connection.close()


# ==========================================
# TEST MYSQL CONNECTION
# ==========================================

if __name__ == "__main__":

    print(
        "Testing MySQL connection..."
    )

    try:

        connection = get_connection()

        print(
            "MySQL connection successful! ✅"
        )

        connection.close()

    except Exception as e:

        print(
            "MySQL connection failed! ❌"
        )

        print(e)