import requests


# Constants
CAA_URL = 'https://coverartarchive.org/'
THUMBNAIL_PIXELS = {'s': '-250', 'm': '-500', 'l': '-1200'}
STATUS_CODE_MAPPING = {
    200: 'Image Retrieved Successfully',
    400: 'Invalid MBID',
    404: 'No Image',
}

def get_release_group_front_cover_data(mbid, thumbnail_size=''):
    url = CAA_URL + f'release-group/{mbid}/front{THUMBNAIL_PIXELS.get(thumbnail_size,'')}'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.content

    except requests.exceptions.Timeout:
        print('Timeout error')
    except requests.exceptions.ConnectionError:
        print('Failed to connect to musicbrainz')
    except requests.exceptions.HTTPError as e:
        print(e)
    except requests.exceptions.RequestException as e:
        print(e)
    except ValueError:
        print('Failed to parse JSON response')

    return None
