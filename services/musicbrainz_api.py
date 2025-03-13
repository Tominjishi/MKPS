import musicbrainzngs as m
import requests
import json

m.set_useragent('MKPS(Uni project)', '0.3.0', 'https://github.com/Tominjishi/MKPS')
MB_URL = 'https://musicbrainz.org/ws/2/'
STATUS_CODE_MAPPING = {
    400: 'Invalid MBID',
    404: 'Not Found',
    500: 'Internal Server Error',
}


def _musicbrainzngs_api_call(api_function, *args):
    try:
        return api_function(*args)
    except m.MusicBrainzError as e:
        print("musicbrainzngs error: ", e)
        return None


def search_artists(query, limit=None, offset=None):
    return _musicbrainzngs_api_call(
        m.search_artists, query, limit, offset)

def search_release_groups(query='', limit=None, offset=None, strict=False):
    return _musicbrainzngs_api_call(
        m.search_release_groups, query, limit, offset, strict)


def browse_release_groups(artist=None, release=None, release_type=[], includes=[], limit=None, offset=None):
    return _musicbrainzngs_api_call(
        m.browse_release_groups, artist, release, release_type, includes, limit, offset)


def get_release_group_by_id(mbid, includes=[], release_status=[], release_type=[]):
    return _musicbrainzngs_api_call(
        m.get_release_group_by_id, mbid, includes, release_status, release_type)


def browse_releases(artist=None, track_artist=None, label=None, recording=None, release_group=None, release_status=[],
                    release_type=[], includes=[], limit=None, offset=None):
    return _musicbrainzngs_api_call(
        m.browse_releases, artist, track_artist, label, recording, release_group, release_status, release_type,
        includes, limit, offset)


def lookup_release_group_dict(mbid, inc=''):
    url = MB_URL + 'release-group/' + mbid + '?'
    if inc:
        url += 'inc=' + inc + '&'
    url += 'fmt=json'

    try:
        response = requests.get(url)
        status_code = response.status_code
        if status_code == 200:
            return_content = json.loads(response.content)
        else:
            return_content = STATUS_CODE_MAPPING.get(status_code, f"Error {status_code}")

        return status_code, return_content
    except requests.RequestException as e:
        print(e)
        return 502, f"Request Failed: {e}"

def get_formats_and_tracks(release_group_mbid):
    formats = set()
    tracks = []

    releases_per_request = 100

    result = browse_releases(
        release_group=release_group_mbid,
        limit=releases_per_request,
        includes=['media', 'recordings']
    )

    release_list = result.get('release-list', [])
    release_count = result.get('release-count')

    if release_count > releases_per_request:
        for offset in range(releases_per_request, release_count, releases_per_request):
            result = browse_releases(
                release_group=release_group_mbid,
                limit=releases_per_request,
                offset=offset,
                includes='media'
            )
        release_list.extend(result.get('release-list', []))

    for release in release_list:
        for medium in release.get('medium-list', []):
            media_format = medium.get('format')
            if media_format:
                formats.add(media_format)

            if not tracks:
                track_list = medium.get('track-list', [])
                for track in track_list:
                    recording = track.get('recording', {})
                    if recording:
                        tracks.append(
                            {
                                'number': track.get('number'),
                                'title': recording.get('title'),
                                'length': int(recording.get('length', 0))
                            }
                        )
    return formats, tracks
