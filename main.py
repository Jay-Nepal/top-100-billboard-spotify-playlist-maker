from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv


load_dotenv()


# Returns a list of top 100 billboard songs from input date
def get_song_list(date: str) -> list:
    response = requests.get(f'https://www.billboard.com/charts/hot-100/{date}')

    soup = BeautifulSoup(response.text, 'html.parser')
    songs = soup.findAll(name='h3', id='title-of-a-story', class_='a-font-primary-bold-s')[2:]

    song_list = []
    for song in songs:
        song_list.append(song.string.strip())

    return song_list


# Returns a list of URI from spotify that relates to the song user wants
def convert_song_list_to_spotify_uri(top_100_song: list, year_of_list: str, spotify_endpoint) -> list:
    current_user = spotify_endpoint.current_user()
    current_user_id = current_user['id']

    spotify_uri_list = []
    for song in top_100_song:
        spotify_song_data = spotify_endpoint.search(q=f'track: {song} year: {year_of_list}',
                                                    limit=1,
                                                    offset=0,
                                                    type='track')
        try:
            song_uri = spotify_song_data['tracks']['items'][0]['uri']
            spotify_uri_list.append(song_uri)
        except IndexError:
            print(f'No song "{song}" exists in Spotify')

    return spotify_uri_list


# Creates a Spotify playlist with input details and outputs the playlist ID
def create_top_100_playlist(spotify_uris: list, playlist_name: str, description: str, user_id: str, visibility: bool, date: str, spotify_endpoint) -> str:
    response = spotify_endpoint.user_playlist_create(user=user_id,
                                                     name=playlist_name,
                                                     public=visibility,
                                                     description=description)
    playlist_id = response['id']
    spotify_endpoint.user_playlist_add_tracks(user=user_id,
                                              playlist_id=playlist_id,
                                              tracks=spotify_uris,
                                              position=None)

    return playlist_id
