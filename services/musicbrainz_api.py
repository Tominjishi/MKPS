import musicbrainzngs as m
import requests
import json

m.set_useragent('MKPS(Uni project)','0.2.3','burvistoms@gmail.com')
MB_URL = 'https://musicbrainz.org/ws/2/'

def searchArtists(query, limit=None, offset=None):
    result = m.search_artists(query, limit, offset)
    return result

def browseReleaseGroups(artist=None, release=None, release_type=[], includes=[], limit=None, offset=None):
    result = m.browse_release_groups(artist, release, release_type, includes, limit, offset)
    return result

def getReleaseGroupByID(id, includes=[], release_status=[], release_type=[]):
    result = m.get_release_group_by_id(id, includes, release_status, release_type)
    return result

def browseReleases(artist=None, track_artist=None, label=None, recording=None, release_group=None, release_status=[], release_type=[], includes=[], limit=None, offset=None):
    result = m.browse_releases(artist, track_artist, label, recording, release_group, release_status, release_type, includes, limit, offset)
    return result

def lookupReleaseGroupDict(id, inc=''):
    url = MB_URL + 'release-group/' + id + '?'
    if inc:
        url += 'inc=' + inc + '&'
    url += 'fmt=json'

    try:
        statusCodeMapping = {
            400: 'Invalid MBID'
        }

        response = requests.get(url)
        statusCode = response.status_code
        if statusCode == 200:
            returnContent = json.loads(response.content)
        else:
            returnContent = statusCodeMapping.get(statusCode, f"Error {statusCode}")

        return (statusCode, returnContent)
    
    except requests.RequestException as e:
        print(e)
        return (502, e)

