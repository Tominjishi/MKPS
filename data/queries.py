from PySide6.QtSql import QSqlDatabase, QSqlQuery


# Retrieves titles of five releases associated with given artist id and no other artists
def get_five_solo_artist_release_titles(artist_id):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return None
    try:
        query = QSqlQuery()
        query.prepare(
            """SELECT title FROM 'release'
                WHERE id IN (
                    SELECT release_id FROM artist_release
                    GROUP BY release_id
                    HAVING COUNT(artist_id) = 1
                )
                AND EXISTS (
                    SELECT 1 FROM artist_release
                    WHERE release_id = 'release'.id AND artist_id = :id
                )
                LIMIT 5;"""
        )
        query.bindValue(':id', artist_id)
        if not query.exec():
            raise Exception('Check format failed: ' + query.lastError().text())
        release_titles = []
        while query.next():
            release_titles.append(query.value('title'))
        return release_titles
    except Exception as e:
        print('Error:', e)
        return None


# Delete artist by id
def delete_artist(artist_id):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return
    try:
        query = QSqlQuery()
        query.prepare('DELETE FROM artist WHERE id = :id')
        query.bindValue(':id', artist_id)
        if not query.exec():
            raise Exception('Artist deletion failed: ' + query.lastError().text())
        # Delete releases with no artist
        if not query.exec('DELETE FROM "release" WHERE id NOT IN (SELECT release_id FROM artist_release)'):
            raise Exception('Orphaned release cleanup failed: ' + query.lastError().text())
        print('Artist deleted')
    except Exception as e:
        print('Error:', e)


# Get list of artist dicts: [{id, name},...]
def get_artists():
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return None
    try:
        query = QSqlQuery('SELECT id, name FROM artist ORDER BY lower(name)')
        if not query.exec():
            raise Exception('Artist fetch failed: ' + query.lastError().text())
        artists = []
        while query.next():
            artists.append({'id': query.value('id'), 'name': query.value('name')})
        return artists
    except Exception as e:
        print('Error:', e)
        return None


# Check if artist of given name and type exists
def exists_artist(name, artist_type):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return False
    try:
        query = QSqlQuery()
        query.prepare('SELECT * from artist WHERE name = :name AND type = :type')
        query.bindValue(':name', name)
        query.bindValue(':type', artist_type)
        if not query.exec():
            raise Exception('Check artist existence failed: ' + query.lastError().text())
        return query.next()
    except Exception as e:
        print('Error:', e)
        return False


# Insert new artist, return id
def insert_artist(name, artist_type):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return None
    try:
        query = QSqlQuery()
        query.prepare('INSERT INTO artist (name, type) VALUES(:name, :type)')
        query.bindValue(':name', name)
        query.bindValue(':type', artist_type)
        if not query.exec():
            raise Exception('Insert artist failed: ' + query.lastError().text())
        print('Artist inserted')
        return query.lastInsertId()
    except Exception as e:
        print('Error:', e)
        return None


# Get list of genre dicts: [{id, name},...]
def get_genres():
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return None
    try:
        query = QSqlQuery('SELECT id, name FROM genre')
        if not query.exec():
            raise Exception('Genre fetch failed: ' + query.lastError().text())
        genres = []
        while query.next():
            genres.append({'id': query.value('id'), 'name': query.value('name')})
        return genres
    except Exception as e:
        print('Error:', e)
        return None


# Delete genre by id
def delete_genre(genre_id):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return
    try:
        query = QSqlQuery()
        query.prepare('DELETE FROM genre WHERE id = :id')
        query.bindValue(':id', genre_id)
        if not query.exec():
            raise Exception('Genre deletion failed: ' + query.lastError().text())
        print('Genre deleted')
    except Exception as e:
        print('Error:', e)


# Check if genre of given name exists
def exists_genre(name):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return False
    try:
        query = QSqlQuery()
        query.prepare('SELECT * from genre WHERE name = :name')
        query.bindValue(':name', name.lower())
        if not query.exec():
            raise Exception('Check genre existence failed: ' + query.lastError().text())
        return query.next()
    except Exception as e:
        print('Error:', e)
        return False


def insert_genre(name):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return None
    try:
        query = QSqlQuery()
        query.prepare('INSERT INTO genre (name) VALUES(:name)')
        query.bindValue(':name', name)
        if not query.exec():
            raise Exception('Insert genre failed: ' + query.lastError().text())
        print('Genre inserted')
        return query.lastInsertId()
    except Exception as e:
        print('Error:', e)
        return None


# Get list of release_type dicts: [{id, name},...]
def get_release_types():
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return None
    try:
        query = QSqlQuery('SELECT id, name FROM release_type ORDER BY lower(name)')
        if not query.exec():
            raise Exception('Release type fetch failed: ' + query.lastError().text())
        types = []
        while query.next():
            types.append({'id': query.value('id'), 'name': query.value('name')})
        return types
    except Exception as e:
        print('Error:', e)
        return None


# Get five releases with specific type_id
# Returns list of tuples [(artist_credit_phrase, title),...]
def get_five_releases_of_type(type_id):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return None
    try:
        query = QSqlQuery()
        query.prepare('SELECT artist_credit_phrase, title FROM "release" WHERE type_id = :type LIMIT 5')
        query.bindValue(':type', type_id)
        if not query.exec():
            raise Exception('Release of type fetch failed: ' + query.lastError().text())
        releases = []
        while query.next():
            values = (query.value('artist_credit_phrase'), query.value('title'))
            releases.append(values)
        return releases
    except Exception as e:
        print('Error:', e)
        return None


# Get list of all types except the one with the provided ID
def get_types_but_one(type_id):
    types = get_release_types()
    for rel_type in types:
        if rel_type['id'] == type_id:
            types.remove(rel_type)
            break
    return types


# Delete release type by id.
# If a replacement type id is provided, update all releases with the deleted type id to the replacement type ID
def delete_release_type(delete_type_id, replace_type_id=None):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return
    try:
        query = QSqlQuery()
        if replace_type_id:
            query.prepare('UPDATE "release" SET type_id = :replace WHERE type_id = :delete')
            query.bindValue(':replace', replace_type_id)
            query.bindValue(':delete', delete_type_id)
            if not query.exec():
                raise Exception('Release type reassignment failed: ' + query.lastError().text())
        query.prepare('DELETE FROM release_type WHERE id = :delete')
        query.bindValue(':delete', delete_type_id)
        if not query.exec():
            raise Exception('Release type deletion failed: ' + query.lastError().text())
        print('Release type deleted.')
    except Exception as e:
        print('Error:', e)


# Check if release type of given name exists
# Return id if found
def exists_release_type(name):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return None
    try:
        query = QSqlQuery()
        query.prepare('SELECT id from release_type WHERE lower(name) = :name')
        query.bindValue(':name', name.lower())
        if not query.exec():
            raise Exception('Check release type existence failed: ' + query.lastError().text())
        if query.next():
            return query.value('id')
        return False
    except Exception as e:
        print('Error:', e)
        return None


def insert_release_type(name):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return None
    try:
        query = QSqlQuery()
        query.prepare('INSERT INTO release_type (name) VALUES(:name)')
        query.bindValue(':name', name)
        if not query.exec():
            raise Exception('Insert release type failed: ' + query.lastError().text())
        print('Release type inserted')
        return query.lastInsertId()
    except Exception as e:
        print('Error:', e)
        return None


# Get 5 releases of specified format_id
# Returns list of tuples [(artist_credit_phrase, title),...]
def get_five_releases_of_format(format_id):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return None
    try:
        query = QSqlQuery()
        query.prepare('SELECT artist_credit_phrase, title FROM "release" WHERE format_id = :format LIMIT 5')
        query.bindValue(':format', format_id)
        if not query.exec():
            raise Exception('Release of format fetch failed: ' + query.lastError().text())
        releases = []
        while query.next():
            values = (query.value('artist_credit_phrase'), query.value('title'))
            releases.append(values)
        return releases
    except Exception as e:
        print('Error:', e)
        return None


# Delete format by id and all releases associated with it
def delete_format(format_id):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return
    try:
        query = QSqlQuery()
        query.prepare('DELETE FROM "release" WHERE format_id = :format')
        query.bindValue(':format', format_id)
        if not query.exec():
            raise Exception('Release deletion by format failed: ' + query.lastError().text())
        query.prepare('DELETE FROM format WHERE id = :format')
        query.bindValue(':format', format_id)
        if not query.exec():
            raise Exception('Format deletion failed: ' + query.lastError().text())
        print('Format deleted')
    except Exception as e:
        print('Error:', e)


# Get list of format dicts: [{id, name},...]
def get_formats():
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return None
    try:
        query = QSqlQuery('SELECT id, name FROM format ORDER BY lower(name)')
        if not query.exec():
            raise Exception('Format fetch failed: ' + query.lastError().text())
        formats = []
        while query.next():
            formats.append({'id': query.value('id'), 'name': query.value('name')})
        return formats
    except Exception as e:
        print('Error:', e)
        return None


# Check if format of given name exists
# Return id if found
def exists_format(name):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return None
    try:
        query = QSqlQuery()
        query.prepare('SELECT id from format WHERE lower(name) = :name')
        query.bindValue(':name', name.lower())
        if not query.exec():
            raise Exception('Check format existence failed: ' + query.lastError().text())
        if query.next():
            return query.value('id')
        return False
    except Exception as e:
        print('Error:', e)
        return None


def insert_format(name):
    db = QSqlDatabase.database()
    if not db.isOpen():
        print('Database connection is closed')
        return None
    try:
        query = QSqlQuery()
        query.prepare('INSERT INTO format (name) VALUES(:name)')
        query.bindValue(':name', name)
        if not query.exec():
            raise Exception('Insert format failed: ' + query.lastError().text())
        print('Format inserted')
        return query.lastInsertId()
    except Exception as e:
        print('Error:', e)
        return None
