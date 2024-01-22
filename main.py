from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()


def validate_spotify():
    spotify_id = os.getenv('spotify_id')
    spotify_secret = os.getenv('spotify_secret')
    redirect_url = os.getenv('redirect_url')

    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_id,
                                                     client_secret=spotify_secret,
                                                     redirect_uri=redirect_url,
                                                     scope="playlist-modify-public playlist-modify-private"))


def get_song_list(url: str) -> list:
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    songs = soup.findAll(name='h3', id='title-of-a-story', class_='a-font-primary-bold-s')[2:]

    song_list = []
    for song in songs:
        song_list.append(song.string.strip())

    return song_list


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


def create_top_100_playlist(spotify_uris: list, user_id: str, visibility: bool, date: str, spotify_endpoint) -> str:
    playlist_name = f'{date} Billboard Top 100'
    response = spotify_endpoint.user_playlist_create(user=user_id,
                                                     name=playlist_name,
                                                     public=visibility,
                                                     description='Playlist created automatically using Spotipy')
    playlist_id = response['id']
    spotify_endpoint.user_playlist_add_tracks(user=user_id,
                                              playlist_id=playlist_id,
                                              tracks=spotify_uris,
                                              position=None)

    return playlist_id


date_to_travel = input('Which year would you like to travel to? Type in YYY-MM-DD format: ')
print(f'(1/5) Starting the scraping process for top 100 songs of {date_to_travel}')
billboard_url = f'https://www.billboard.com/charts/hot-100/{date_to_travel}'
top_100_songs = get_song_list(billboard_url)
year = date_to_travel[:4]

print('(2/5) Validating your spotify account through OAuth')
sp = validate_spotify()
spotify_userid = sp.current_user()['id']

print('(3/5) Finding Spotify ID of the top 100 song')
spotify_uri_list = convert_song_list_to_spotify_uri(top_100_songs, year, sp)

print('(4/5) Creating a Spotify playlist and adding the songs')
playlist_visibility = input("Enter Y if you would like the playlist to be public: ")
if playlist_visibility.upper() == 'Y':
    playlist_visibility = True
else:
    playlist_visibility = False
playlist = create_top_100_playlist(spotify_uri_list, spotify_userid, playlist_visibility, date_to_travel, sp)
playlist_url = f'https://open.spotify.com/playlist/{playlist}'

print(f'(5/5) Completed! Open link {playlist_url} for the Playlist in Spotify')