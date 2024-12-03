import psycopg2
from psycopg2 import sql
import traceback
import json

DB_NAME = "project3_test"
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"

JSON_FILE = "../scraper/clean.json"
if __name__ == '__main__':


    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("""
        DROP TABLE IF EXISTS Users CASCADE;
            DROP TABLE IF EXISTS FavoritesLists CASCADE;
            DROP TABLE IF EXISTS FavoritesListsSongs CASCADE;
            DROP TABLE IF EXISTS Songs CASCADE;
            DROP TABLE IF EXISTS Charts CASCADE;
        """)
        print("Dropped tables successfully")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(100) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'user'
            );

            CREATE TABLE IF NOT EXISTS FavoritesLists (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL REFERENCES Users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS Songs (
                id SERIAL PRIMARY KEY,
                songName VARCHAR(200) NOT NULL,
                game VARCHAR(200) NOT NULL,
                higherBPM INT NOT NULL,
                lowerBPM INT NOT NULL,
                licensed BOOLEAN NOT NULL,
                changingBPM BOOLEAN NOT NULL,
                runtime INT NOT NULL,
                artist VARCHAR(200) NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Charts (
                id SERIAL PRIMARY KEY,
                song_id INT NOT NULL REFERENCES Songs(id) ON DELETE CASCADE,
                isDoubles BOOLEAN NOT NULL,
                notes INT NOT NULL,
                freezeNotes INT NOT NULL,
                shockNotes INT,
                difficulty VARCHAR(50) NOT NULL,
                difficultyRating INT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS FavoritesListSongs (
                favoritesList_id INT NOT NULL REFERENCES FavoritesLists(id) ON DELETE CASCADE,
                song_id INT NOT NULL REFERENCES Songs(id) ON DELETE CASCADE,
                PRIMARY KEY (favoritesList_id, song_id)
            );
        """)

        print("Tables created successfully.")

        with open(JSON_FILE, "r") as file:
            songs_data = json.load(file)

        cursor.execute("""
            INSERT INTO Users (name, email, password, role)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, ('Admin', 'admin@example.com', 'password', 'admin'))
        user_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO FavoritesLists (user_id)
            VALUES (%s)
            ON CONFLICT DO NOTHING
            RETURNING id;
        """, (user_id,))
        favorites_list_id = cursor.fetchone()[0]

        for song in songs_data:
            cursor.execute("""
                INSERT INTO Songs (songName, game, higherBPM, lowerBPM, licensed, changingBPM, runtime, artist)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """, (
                song["songName"], song["game"], song["higherBPM"],
                song["lowerBPM"], song["licensed"], song["changingBPM"],
                song["runtime"], song["artist"]
            ))
            song_id = cursor.fetchone()[0]

            for chart in song["charts"]:
                # chart is null if there are no notes or difficulty rating
                if chart["notes"] is not None and chart["difficultyRating"] is not None:
                    cursor.execute("""
                        INSERT INTO Charts (song_id, isDoubles, notes, freezeNotes, shockNotes, difficulty, difficultyRating)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """, (
                        song_id, chart["isDoubles"], chart["notes"],
                        chart["freezeNotes"], chart["shockNotes"],
                        chart["difficulty"], chart["difficultyRating"]
                    ))
                    
        print("Data inserted successfully.")
        cursor.close()
        conn.close()
        print("Database connection closed.")
    except Exception as e:
        print("Error occurred:", e)
        print(traceback.format_exc())