import psycopg2
from psycopg2 import sql
import traceback
import json

DB_NAME = "project3_test"
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"

JSON_FILE = "clean.json"

def create_database_if_not_exists(): 
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if the target database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()

        if not exists:
            # Create the database if it doesn't exist
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"Database {DB_NAME} created successfully.")
        else:
            print(f"Database {DB_NAME} already exists.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")


if __name__ == '__main__':

    create_database_if_not_exists()

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
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'user'
            );

            CREATE TABLE IF NOT EXISTS FavoritesLists (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL REFERENCES Users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS Playlists (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                user_id INT NOT NULL REFERENCES Users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS Songs (
                id SERIAL PRIMARY KEY,
                song_name VARCHAR(200) NOT NULL,
                game VARCHAR(200) NOT NULL,
                higher_bpm INT NOT NULL,
                lower_bpm INT NOT NULL,
                licensed BOOLEAN NOT NULL,
                changing_bpm BOOLEAN NOT NULL,
                runtime INT NOT NULL,
                artist VARCHAR(200) NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Charts (
                d SERIAL PRIMARY KEY,
                song_id INT NOT NULL REFERENCES Songs(id) ON DELETE CASCADE,
                is_doubles BOOLEAN NOT NULL,
                notes INT NOT NULL,
                freeze_notes INT DEFAULT 0,
                shock_notes INT DEFAULT 0,
                difficulty VARCHAR(50) NOT NULL,
                difficulty_rating INT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS FavoritesListSongs (
                favorites_list_id INT NOT NULL REFERENCES FavoritesLists(id) ON DELETE CASCADE,
                song_id INT NOT NULL REFERENCES Songs(id) ON DELETE CASCADE,
                PRIMARY KEY (favorites_list_id, song_id)
            );
            
            CREATE TABLE IF NOT EXISTS playlist_songs (
                playlist_id INT NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
                song_id INT NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
                added_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (playlist_id, song_id)
            );
        """)

        print("Tables created successfully.")

        with open(JSON_FILE, "r") as file:
            songs_data = json.load(file)

        import bcrypt
        hashed_password = bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("""
            INSERT INTO Users (name, email, password, role)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, ('Admin', 'admin@example.com', hashed_password.decode('utf-8'), 'admin'))
        user_id = cursor.fetchone()[0]
       
        cursor.execute("""
            INSERT INTO FavoritesLists (user_id)
            VALUES (%s)
            ON CONFLICT DO NOTHING
            RETURNING id;
        """, (user_id,))
        favorites_list_id = cursor.fetchone()[0]

        for song in songs_data:
            try:
                cursor.execute("""
                    INSERT INTO Songs (song_name, game, higher_BPM, lower_BPM, licensed, changing_BPM, runtime, artist)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
                """, (
                    song["songName"], song["game"], song["higherBPM"],
                    song["lowerBPM"], song["licensed"], song["changingBPM"],
                    song["runtime"], song["artist"]
                ))
                song_id = cursor.fetchone()[0]
            except Exception as e:
                print(f"Error inserting song '{song['songName']}': {e}")
                continue  # Skip to the next song if there's an issue

            for chart in song["charts"]:
                try:
                    if chart["notes"] is not None and chart["difficultyRating"] is not None:
                        cursor.execute("""
                            INSERT INTO Charts (song_id, is_doubles, notes, freeze_Notes, shock_Notes, difficulty, difficulty_Rating)
                            VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """, (
                            song_id,
                            chart["isDoubles"],
                            chart["notes"],
                            chart.get("freezeNotes", 0),  # Default to 0 if freezeNotes is missing or None
                            chart.get("shockNotes", 0),  # Default to 0 if shockNotes is missing or None
                            chart["difficulty"].lower(),
                            chart["difficultyRating"]
                        ))
                except Exception as e:
                    print(f"Error inserting chart for song ID {song_id}: {e}")
                    
        print("Data inserted successfully.")
        
    except Exception as e:
        print("Error occurred:", e)
        print(traceback.format_exc())
        
    finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            print("Database connection closed.")
            