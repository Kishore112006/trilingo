import mysql.connector


def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="5BS",
        database="tridict"
    )

    return connection


def save_history(word, language, english, telugu, hindi):

    connection = get_connection()
    cursor = connection.cursor()

    sql = """
        INSERT INTO history
        (searched_word, detected_language, english, telugu, hindi)
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


def get_history():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM history
        ORDER BY searched_at DESC
        LIMIT 20
    """

    cursor.execute(sql)

    history = cursor.fetchall()

    cursor.close()
    connection.close()

    return history


def delete_history():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM history")

    connection.commit()

    cursor.close()
    connection.close()


# Test MySQL connection
if __name__ == "__main__":

    print("Testing MySQL connection...")

    try:

        connection = get_connection()

        print("MySQL connection successful! ✅")

        connection.close()

    except Exception as e:

        print("MySQL connection failed! ❌")

        print(e)