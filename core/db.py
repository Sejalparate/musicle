import mysql.connector
from youtubesearchpython import VideosSearch
from core.config import settings

# Database connection
db = mysql.connector.connect(
    host=settings.DB_HOST,
    user=settings.DB_USER,
    passwd=settings.DB_PASSWORD,
    database=settings.DB_NAME
)
cursor = db.cursor()

# Extract playlist names
def get_playlist_names():
    cursor.execute('SELECT playlist_name FROM playlists')
    return [row[0] for row in cursor.fetchall()]

# Extract playlist details
def get_playlist_details(playlist_name):
    cursor.execute('SELECT * FROM playlists WHERE playlist_name = %s', (playlist_name,))
    return cursor.fetchone()

# Creates new playlist
def create_playlist(playlist_name, description):
    sql = "INSERT INTO playlists(playlist_name, description) VALUES (%s, %s)"
    val = (playlist_name, description)

    cursor.execute(sql, val)
    db.commit()

# Deletes existing playlist
def delete_playlist(playlist_name):
    cursor.execute("DELETE FROM playlists WHERE playlist_name = %s", (playlist_name,))
    db.commit()

# Function to get YouTube link for a song
def get_youtube_link(song_title, artists):
    try:
        search_query = f"{song_title} {artists}"
        video_search = VideosSearch(search_query, limit=1)
        results = video_search.result()
        if results and 'link' in results['result'][0]:
            youtube_link = results['result'][0]['link']
            update_youtube_link(song_title, artists, youtube_link)
            return  youtube_link
    except Exception as e:
        print(f"Error fetching YouTube link: {e}")
    return None

# Adds songs to playlist
def add_song_to_playlist(playlist_name, song_title, artists, album, release_year, genre, language, youtube_link):
    add_song_query = """
            INSERT INTO songs(song_title, artists, album, release_year, genre, language, playlist_name, youtube_link) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    val = (song_title, artists, album, release_year, genre, language, playlist_name, youtube_link)
    cursor.execute(add_song_query, val)
    db.commit()

# Get song details for a playlist  
def get_song_details(playlist_name):
    get_song_query = """
        SELECT song_title, artists, album, release_year, genre, language, youtube_link
        FROM songs
        WHERE playlist_name = %s
    """
    cursor.execute(get_song_query, (playlist_name,))
    return cursor.fetchall()

# Updates song details
def update_song_details(playlist_name, old_title, new_title, new_artists, new_album, new_release_year, new_genre, new_language):
    update_query = """
        UPDATE songs
        SET song_title = %s, artists = %s, album = %s, release_year = %s, genre = %s, language = %s
        WHERE playlist_name = %s AND song_title = %s
    """
    update_values = (new_title, new_artists, new_album, new_release_year, new_genre, new_language, playlist_name, old_title)

    cursor.execute(update_query, update_values)
    db.commit()

# Update YouTube link in the database
def update_youtube_link(song_title, artists, youtube_link):
    try:
        # Fetch the existing record from the database
        cursor.execute('SELECT * FROM songs WHERE song_title = %s AND artists = %s', (song_title, artists))
        record = cursor.fetchone()

        if record:
            # Update the YouTube link
            update_query = "UPDATE songs SET youtube_link = %s WHERE song_title = %s AND artists = %s"
            update_values = (youtube_link, song_title, artists)
            cursor.execute(update_query, update_values)
            db.commit()
            print("YouTube link updated successfully!")
        else:
            print("Song not found in the database.")
    except Exception as e:
        print(f"Error updating YouTube link: {e}")

# Delete song details
def delete_song(playlist_name, song_title):
    delete_query = """
        DELETE FROM songs
        WHERE playlist_name = %s AND song_title = %s
    """
    delete_values = (playlist_name, song_title)

    cursor.execute(delete_query, delete_values)
    db.commit()