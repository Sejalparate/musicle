import mysql.connector
import streamlit as st
import pandas as pd

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="qwerty",
    database="music_db"
)
# Enter your credentials
cursor = db.cursor()

print("Connection established")

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

    st.success("Playlist created successfully!")
    st.session_state.playlist_created = True

# Deletes existing playlist
def delete_playlist(playlist_name):
    sql = "DELETE FROM playlists WHERE playlist_name = %s"
    cursor.execute(sql, (playlist_name,))
    db.commit()

    st.success("Playlist deleted successfully!")

# Adds songs to playlist
def add_song_to_playlist(playlist_name, song_title, artists, album, release_year, genre, language):
    sql = "INSERT INTO songs(song_title, artists, album, release_year, genre, language, playlist_name) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (song_title, artists, album, release_year, genre, language, playlist_name)

    cursor.execute(sql, val)
    db.commit()

    st.success(f"Song added to playlist {playlist_name}")

# Get song details for a playlist 
def get_song_details(playlist_name):
    cursor.execute('SELECT song_title, artists, album, release_year, genre, language FROM songs WHERE playlist_name = %s', (playlist_name,))
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

# Streamlit app
def main():
    st.set_page_config(layout="wide")
    st.title("Musicle")

    page = st.sidebar.radio("Navigation", ["Create Playlist", "View Playlists", "Add Songs", "Edit Song Details", "Delete Playlist"])

    # Create playlist page
    if page == "Create Playlist":
        st.header("Create Playlist")
        with st.form("create_playlist_form"):
            playlist_name = st.text_input("Enter playlist name")
            description = st.text_input("Enter description")
            submit = st.form_submit_button("Create")

        if submit:
            create_playlist(playlist_name, description)

    # View Playlist page
    elif page == "View Playlists":
        st.header("View Playlists")
        playlists = get_playlist_names()
        selected = st.selectbox("Choose Playlist", playlists)

        if selected:
            songs = get_song_details(selected)
            column_names = ["Song Title", "Artists", "Album", "Release Year", "Genre", "Language"]
            
            songs_df = pd.DataFrame(songs, columns=column_names)
            songs_df = songs_df.applymap(lambda x: x.title() if isinstance(x, str) else x)
            songs_df.index = range(1, len(songs_df)+1)
            
            st.table(songs_df)

    # Add songs page
    elif page == "Add Songs":
        st.header("Add Songs")
        with st.form("add_song_form"):
            playlist = st.selectbox("Choose Playlist", get_playlist_names())
            song_title = st.text_input("Enter song title")
            artists = st.text_input("Enter artists")
            album = st.text_input("Enter album")
            release_year = st.text_input("Enter release year")
            genre = st.text_input("Enter genre")
            language = st.text_input("Enter language")
            submit = st.form_submit_button("Add Song")

        if submit:
            add_song_to_playlist(playlist, song_title, artists, album, release_year, genre, language)

    # Edit song details page
    elif page == "Edit Song Details":
        st.header("Edit Song Details")
        playlists = get_playlist_names()
        selected_playlist = st.selectbox("Choose Playlist", playlists)

        if selected_playlist:
            songs = get_song_details(selected_playlist)
            column_names = ["Song Title", "Artists", "Album", "Release Year", "Genre", "Language"]
            
            songs_df = pd.DataFrame(songs, columns=column_names)
            songs_df = songs_df.applymap(lambda x: x.title() if isinstance(x, str) else x)
            songs_df.index = range(1, len(songs_df)+1)
            
            st.table(songs_df)

            selected_song = st.selectbox("Select Song to Edit", songs_df["Song Title"])
            new_title = st.text_input("New Song Title", selected_song)
            new_artists = st.text_input("New Artists", songs_df[songs_df["Song Title"] == selected_song]["Artists"].values[0])
            new_album = st.text_input("New Album", songs_df[songs_df["Song Title"] == selected_song]["Album"].values[0])
            new_release_year = st.text_input("New Release Year", songs_df[songs_df["Song Title"] == selected_song]["Release Year"].values[0])
            new_genre = st.text_input("New Genre", songs_df[songs_df["Song Title"] == selected_song]["Genre"].values[0])
            new_language = st.text_input("New Language", songs_df[songs_df["Song Title"] == selected_song]["Language"].values[0])

            if st.button("Apply Changes"):
                update_song_details(selected_playlist, selected_song, new_title, new_artists, new_album, new_release_year, new_genre, new_language)
                st.success("Song details updated successfully!")
    
    # Delete playlist page
    elif page == "Delete Playlist":
        st.subheader("Delete Playlist")
        selected = st.selectbox("Choose Playlist", get_playlist_names())
        if st.button("Delete"):
            delete_playlist(selected)

if __name__ == '__main__':
    main()