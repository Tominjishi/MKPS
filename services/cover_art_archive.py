import requests

# Constants
THUMBNAIL_PIXELS = {'s': '-250', 'm': '-500', 'l': '-1200'}
STATUS_CODE_MAPPING = {
    200: 'Image Retrieved Successfully',
    400: 'Invalid MBID',
    404: 'No Image',
}

def get_release_group_front_cover_data(mbid, thumbnail_size=''):
    url = f"https://coverartarchive.org/release-group/{mbid}/front{THUMBNAIL_PIXELS.get(thumbnail_size,'')}"
    try:
        response = requests.get(url)
        status_code = response.status_code
        content = STATUS_CODE_MAPPING.get(status_code, f"Error {status_code}")

        if status_code == 200:
            content = response.content

        return status_code, content
    except requests.RequestException as e:
        return 502, f"Request Failed: {e}"
