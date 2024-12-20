import musicbrainzngs as m
import time

m.set_useragent('MKPS(Uni project)','0.2.0','burvistoms@gmail.com')

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