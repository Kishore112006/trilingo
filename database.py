from dotenv import load_dotenv
import os
import mysql.connector


# Load .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)


# ==========================================
# MYSQL CONNECTION
# ==========================================

def get_connection():

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),

        # Aiven requires SSL
        ssl_disabled=False
    )

    return connection


# ==========================================
# CREATE HISTORY TABLE
# ==========================================

def create_table():

    connection = get_connection()
    cursor = connection.cursor()

    sql = """
    CREATE TABLE IF NOT EXISTS history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        searched_word VARCHAR(255) NOT NULL,
        detected_language VARCHAR(20) NOT NULL,
        english VARCHAR(255),
        telugu VARCHAR(255),
        hindi VARCHAR(255),
        searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    cursor.execute(sql)
    connection.commit()

    cursor.close()
    connection.close()

    print("History table ready! ✅")


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

    cursor.execute(sql, values)

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
# TEST CONNECTION
# ==========================================

if __name__ == "__main__":

    print("Testing Aiven MySQL connection...")

    try:

        connection = get_connection()

        print("MySQL connection successful! ✅")

        connection.close()

    except Exception as e:

        print("MySQL connection failed! ❌")

        print(e)