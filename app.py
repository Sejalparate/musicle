import streamlit as st
import pandas as pd
from queries import *

# Streamlit app
def main():
    st.set_page_config(layout = "wide")
    st.title("Musicle")

    page = st.sidebar.radio("Navigation", ["Create Playlist", "View Playlists", "Add Songs", 
                                           "Edit Song Details", "Delete Song", "Delete Playlist"])

    # Create playlist page
    if page == "Create Playlist":
        st.header("Create Playlist")
        with st.form("create_playlist_form"):
            playlist_name = st.text_input("Enter playlist name")
            description = st.text_input("Enter description")
            submit = st.form_submit_button("Create")

        if submit:
            create_playlist(playlist_name, description)
            st.success("Playlist created successfully!")
        st.session_state.playlist_created = True

    # View Playlist page
    elif page == "View Playlists":
        st.header("View Playlists")
        playlists = get_playlist_names()
        selected = st.selectbox("Choose Playlist", playlists)

        if selected:
            songs = get_song_details(selected)
            column_names = ["Song Title", "Artists", "Album", "Release Year", "Genre", "Language", "Youtube Link"]
            songs_df = pd.DataFrame(songs, columns = column_names)
            songs_df.iloc[:, :-1] = songs_df.iloc[:, :-1].applymap(lambda x: x.title() if isinstance(x, str) else x)
            songs_df.index = range(1, len(songs_df) + 1)

            songs_df["Song Title"] = songs_df.apply(lambda row: f'<a href = "{row["Youtube Link"]}" target = "_blank">{row["Song Title"]}</a>', axis = 1)
            songs_df.drop(columns = ["Youtube Link"], inplace = True)

            table_html = songs_df.to_html(escape = False)
            table_html = table_html.replace('<th>', '<th style = "text-align: left;">')
            
            st.markdown(table_html, unsafe_allow_html = True)

    # Add songs page
    elif page == "Add Songs":
        st.header("Add Songs")
        playlists = get_playlist_names()
        playlist_name = st.selectbox("Choose Playlist", playlists)
        
        song_title = st.text_input("Enter song title")
        artists = st.text_input("Enter artists")
        album = st.text_input("Enter album (optional)")
        release_year = st.text_input("Enter release year (optional)")
        genre = st.text_input("Enter genre")
        language = st.text_input("Enter language (optional)")
        
        if st.button("Add Song"):
            youtube_link = get_youtube_link(song_title, artists)
            if youtube_link:
                add_song_to_playlist(playlist_name, song_title, artists, album, release_year, genre, language, youtube_link)
                st.success("Song added successfully!")
            else:
                st.error("Failed to fetch YouTube link. Please check the song details and try again.")

    # Edit song details page
    elif page == "Edit Song Details":
        st.header("Edit Song Details")
        playlists = get_playlist_names()
        selected_playlist = st.selectbox("Choose Playlist", playlists)

        if selected_playlist:
            songs = get_song_details(selected_playlist)
            column_names = ["Song Title", "Artists", "Album", "Release Year", "Genre", "Language", "YouTube Link"]
            songs_df = pd.DataFrame(songs, columns = column_names)
            songs_df.iloc[:, :-1] = songs_df.iloc[:, :-1].applymap(lambda x: x.title() if isinstance(x, str) else x)
            songs_df.index = range(1, len(songs_df) + 1)
            songs_df.drop(columns = ["YouTube Link"], inplace = True)

            # Convert dataframe to HTML format
            table_html = songs_df.to_html(escape = False)
            table_html = table_html.replace('<th>', '<th style = "text-align: left;">')
            st.markdown(table_html, unsafe_allow_html = True)

            # Find the corresponding song details
            selected_song_title = st.selectbox("Select Song to Edit", songs_df["Song Title"])
            selected_song = songs_df[songs_df["Song Title"] == selected_song_title]

            new_title = st.text_input("New Song Title", selected_song["Song Title"].values[0])
            new_artists = st.text_input("New Artists", selected_song["Artists"].values[0])
            new_album = st.text_input("New Album", selected_song["Album"].values[0])
            new_release_year = st.text_input("New Release Year", selected_song["Release Year"].values[0])
            new_genre = st.text_input("New Genre", selected_song["Genre"].values[0])
            new_language = st.text_input("New Language", selected_song["Language"].values[0])

            if st.button("Apply Changes"):
                update_song_details(selected_playlist, selected_song["Song Title"].values[0], new_title, new_artists, new_album, new_release_year, new_genre, new_language)
                
                # Retrieve the new YouTube link for the updated song title
                new_youtube_link = get_youtube_link(new_title, new_artists)
                
                if new_youtube_link:
                    # Update the YouTube link in the database
                    if update_youtube_link(new_title, new_artists, new_youtube_link):
                        st.error("Failed to update YouTube link. Please check the song details and try again.")
                    else:
                        st.success("Song details updated successfully!")
                        
            st.write("Note: To see the reflected changes, kindly visit the 'View playlists' page.")
            
    # Delete song page
    elif page == "Delete Song":
        st.subheader("Delete Song")
        selected_playlist = st.selectbox("Choose Playlist", get_playlist_names())

        if selected_playlist:
            songs = get_song_details(selected_playlist)
            song_titles = [song[0] for song in songs]
            selected_song_title = st.selectbox("Select Song to Delete", song_titles)

            if st.button("Delete"):
                delete_song(selected_playlist, selected_song_title)
                st.success("Song deleted successfully!")

    # Delete playlist page
    elif page == "Delete Playlist":
        st.subheader("Delete Playlist")
        selected = st.selectbox("Choose Playlist", get_playlist_names())

        if st.button("Delete"):
            delete_playlist(selected)
            st.success("Playlist deleted successfully!")

if __name__ == '__main__':
    main()