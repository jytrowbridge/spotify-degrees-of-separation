import base64
from dotenv import load_dotenv
import json
import os
from request_funcs import get_request
from spotify_get_bearer_token import get_bearer_token

load_dotenv()
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
BEARER_TOKEN = get_bearer_token()


def get_artist_id(artist_name):
    # Return spotify link to given track, if found; False otherwise
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    params = {
        'q': f'artist:{artist_name}',
        'type': 'artist',
        'limit': '1'
    }
    url = 'https://api.spotify.com/v1/search'

    r_raw = get_request(url, headers=headers, params=params)
    r_artist = r_raw.json()['artists']['items'][0]
    if artist_name.upper() == r_artist['name'].upper():
        return r_artist['id']
    else:
        return False


def get_related_artists(artist_name='', artist_id=False, depth=0):
    artist_id = artist_id or get_artist_id(artist_name)
    if artist_id:
        headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
        url = f'https://api.spotify.com/v1/artists/{artist_id}/related-artists'

        r_raw = get_request(url, headers=headers)
        if not r_raw:
            return False
        artists = []
        for artist in r_raw.json()['artists']:
            image_url = ''
            max_size = 0
            for image in artist['images']:
                if int(image['height']) > max_size:
                    image_url = image['url']
                    max_size = int(image['height'])

            artists.append({
                'type': 'artist',
                'name': artist['name'],
                'id': artist['id'],
                'image_url': image_url,
                'parent_id': artist_id,
                'parent_name': artist_name,
                'depth':depth
            })

        return artists


def find_path_bw_artists(artist1, artist2):
    '''
    algorithm:
        append artists1 to empty list 'artists'
        loop through artists
            if in seen, skip
            add to seen
            find related artists
            if any artists are target, return
            else, add children to artists

        the calls to api are taking forever...
        efficiency idea:
            instead of calling 'get_related_artists' every time, just add a placeholder
            when get to placeholder, then call get_related_artists
        
        problem is that each artist has 20 related artists
            so, depth 1 is looking at 20 artists
            depth 2, 20*20 = 400 artists
            depth 3, 20*20*20 = 8000 artists...
        My api calls are limited
    '''
    artists = get_related_artists(artist1, depth=1)
    seen = {}
    parents = {}
    while len(artists) > 0:
        artist = artists.pop(0)

        if artist['type'] == 'placeholder':
            print(f'Depth: {artist["depth"]} | Calling get_related_artists for {artist["name"]}')
            related_artists = get_related_artists(
                                    artist_name=artist['name'],
                                    artist_id=artist['id'],
                                    depth=artist['depth'] + 1
                                )
            if not related_artists:
                return "Something went wrong in api call"
            artists = related_artists + artists
            continue

        if artist['id'] in seen:
            continue

        seen[artist['id']] = True
        parents[artist['id']] = {
                                    'id': artist['parent_id'],
                                    'name': artist['parent_name']
                                }

        if artist['name'].upper() == artist2.upper():
            print('path found!!!')
            path = [artist['name']]
            artist_id = artist['id']
            artist_name = artist['name']
            while artist_name.upper() != artist1.upper():
                print(artist_name)
                parent = parents[artist_id]
                path += [parent['name']]
                artist_id = parent['id']
                artist_name = parent['name']
                return path

        artists += [{
            'type': 'placeholder',
            'id': artist['id'],
            'name': artist['name'],
            'depth': artist['depth']
        }]



if __name__ == "__main__":
    # print(get_artist_id('obituary'))
    # print(get_related_artists('obituary'))
    print(find_path_bw_artists('jack johnson', 'jack white'))
