from collections import defaultdict
from PySide6.QtSql import QSqlDatabase, QSqlQuery


# Class for handling data to display on release card and storing in DB
class Release:
    def __init__(
            self, release_type, title, artist_credit_phrase,  # strings
            artists, # list
            mbid = None, tracks = [], genres = [], cover = None, release_date = None, release_format=None, added_at = None,  # optional
            db_id = None, type_id = None, format_id = None):  # local only
        self.mbid = mbid
        self.type = release_type
        self.title = title
        self.artist_credit_phrase = artist_credit_phrase
        self.cover = cover
        self.artists = artists
        self.genres = genres
        self.tracks = tracks
        self.format = release_format
        self.release_date = release_date
        self.added_at = added_at
        self.id = db_id
        self.type_id = type_id
        self.format_id = format_id

    # Insert release from MB into the DB using class properties
    def insert_from_mb(self, chosen_format):
        type_inserted = format_inserted = artist_inserted = genre_inserted = False
        db = QSqlDatabase.database()
        if db.isOpen():
            db.transaction()
            try:
                query = QSqlQuery()
                # Get release_type id if in db
                query.prepare('SELECT id FROM release_type WHERE lower(name) = :type')
                query.bindValue(':type', self.type.lower())
                if query.exec():
                    if query.next():
                        self.type_id = query.value('id')
                    else:
                        # Create new release type and get id
                        query.prepare('INSERT INTO release_type (name) VALUES(:type)')
                        query.bindValue(':type', self.type)
                        if not query.exec():
                            raise Exception('Insert release_type failed: ' + query.lastError().text())
                        self.type_id = query.lastInsertId()
                        type_inserted = True
                else:
                    raise Exception('Fetch release_type failed: ' + query.lastError().text())

                # Get format id from db or create new type record
                query.prepare('SELECT id FROM format WHERE lower(name) = :format')
                query.bindValue(':format', chosen_format.lower())
                if query.exec():
                    if query.next():
                        self.format_id = query.value('id')
                    else:
                        query.prepare('INSERT INTO format (name) VALUES(:format)')
                        query.bindValue(':format', chosen_format)
                        if not query.exec():
                            raise Exception('Insert format failed: ' + query.lastError().text())
                        self.format_id = query.lastInsertId()
                        format_inserted = True
                else:
                    raise Exception('Fetch format failed: ' + query.lastError().text())

                # Insert release record itself
                self.insert_release_record()

                # Insert artists
                for artist in self.artists:
                    query.prepare('SELECT id FROM artist WHERE mbid = :mbid OR name = :name')
                    query.bindValue(':mbid', artist['id'])
                    query.bindValue(':name', artist['name'])
                    if query.exec():
                        if query.next():
                            artist_id = query.value('id')
                        else:
                            # Create new artist if not found and get id
                            query.prepare('INSERT INTO artist (mbid, name, type) VALUES (:mbid, :name, :type)')
                            query.bindValue(':mbid', artist['id'])
                            query.bindValue(':name', artist['name'])
                            query.bindValue(':type', artist['type'])
                            if not query.exec():
                                raise Exception('Insert artist failed: ' + query.lastError().text())
                            artist_id = query.lastInsertId()
                            artist_inserted = True
                    else:
                        raise Exception('Fetch artist failed: ' + query.lastError().text())

                    # Insert artist link to release
                    query.prepare('INSERT INTO artist_release (release_id, artist_id) VALUES (:release_id, :artist_id)')
                    query.bindValue(':release_id', self.id)
                    query.bindValue(':artist_id', artist_id)
                    if not query.exec():
                        raise Exception('Insert artist_release failed: ' + query.lastError().text())

                # Insert genre links
                for genre in self.genres:
                    # Get genre id if in db
                    query.prepare('SELECT id FROM genre WHERE mbid = :mbid OR lower(name) = :name')
                    query.bindValue(':mbid', genre['id'])
                    query.bindValue(':name', genre['name'].lower())
                    if query.exec():
                        if query.next():
                            genre_id = query.value('id')
                        else:
                            # Create genre if new and get id
                            query.prepare('INSERT INTO genre (mbid, name) VALUES (:mbid, :name)')
                            query.bindValue(':mbid', genre['id'])
                            query.bindValue(':name', genre['name'])
                            if not query.exec():
                                raise Exception('Insert genre failed: ' + query.lastError().text())
                            genre_id = query.lastInsertId()
                            genre_inserted = True
                    else:
                        raise Exception('Fetch genre failed: ' + query.lastError().text())

                    # Insert genre link to release
                    query.prepare("""INSERT INTO release_genre (genre_id, release_id, vote_count)
                                     VALUES (:genre_id, :release_id, :vote_count)""")
                    query.bindValue(':genre_id', genre_id)
                    query.bindValue(':release_id', self.id)
                    query.bindValue(':vote_count', genre['count'])
                    if not query.exec():
                        raise Exception('Insert release_genre failed: ' + query.lastError().text())

                # Insert tracks
                for i, track in enumerate(self.tracks):
                    query.prepare("""INSERT INTO track (release_id, actual_position, position, title, length)
                                     VALUES (:release_id, :actual_pos, :position, :title, :length)""")
                    query.bindValue(':release_id', self.id)
                    query.bindValue(':actual_pos', i)
                    query.bindValue(':position', track['position'])
                    query.bindValue(':title', track['title'])
                    query.bindValue(':length', track['length'])
                    if not query.exec():
                        raise Exception('Insert track failed: ' + query.lastError().text())
                    self.tracks[i]['id'] = query.lastInsertId()

                db.commit()
                print('Release inserted')
                return type_inserted, format_inserted, artist_inserted, genre_inserted
            except Exception as e:
                print('Error:', e)
                db.rollback()
                return None
        else:
            print('Database connection is closed!')
            return None

    def insert_manual(self, edited_data, tracks):
        db = QSqlDatabase.database()
        if db.isOpen():
            try:
                # Insert release record itself
                self.insert_release_record()

                # Insert artists connections
                self.insert_artist_connections(edited_data['added_artist_ids'])

                # Insert genre links
                self.insert_genre_connections(edited_data['added_genre_ids'])

                # Insert tracks
                if edited_data.get('tracks_edited'):
                    for i, track in enumerate(tracks):
                        tracks[i]['id'] = self.insert_track(i, track)
                    self.tracks = tracks

                print('Release inserted')
            except Exception as e:
                print('Error:', e)
                db.rollback()
        else:
            print('Database connection is closed!')

    def insert_release_record(self):
        query = QSqlQuery()
        query.prepare(
            """INSERT INTO "release"(
                format_id,
                type_id,
                release_group_mbid,
                title,
                release_date,
                artist_credit_phrase,
                cover
            )
               VALUES (
                :format_id,
                :type_id,
                :mbid,
                :title,
                :release_date,
                :artist_credit_phrase,
                :cover
            )"""
        )
        query.bindValue(':format_id', self.format_id)
        query.bindValue(':type_id', self.type_id)
        query.bindValue(':mbid', self.mbid)
        query.bindValue(':title', self.title)
        query.bindValue(':release_date', self.release_date)
        query.bindValue(':artist_credit_phrase', self.artist_credit_phrase)
        query.bindValue(':cover', self.cover)
        if not query.exec():
            raise Exception('Insert release failed: ' + query.lastError().text())
        self.id = query.lastInsertId()

    def fill_tracks(self):
        db = QSqlDatabase.database()
        if db.isOpen():
            try:
                query = QSqlQuery()
                query.prepare(
                    """SELECT id, position, title, length
                       FROM track
                       WHERE release_id = :r_id
                       ORDER BY actual_position"""
                )
                query.bindValue(':r_id', self.id)
                if not query.exec():
                    raise Exception('Track fetch failed: ' + query.lastError().text())
                self.tracks = []
                while query.next():
                    self.tracks.append(
                        {
                            'id': query.value('id'),
                            'position': query.value('position'),
                            'title': query.value('title'),
                            'length': query.value('length')
                        }
                    )
            except Exception as e:
                print('Error:', e)
        else:
            print('Database connection is closed!')

    def delete(self):
        db = QSqlDatabase.database()
        if db.isOpen():
            try:
                query = QSqlQuery()
                query.prepare('DELETE FROM "release" WHERE id = :id')
                query.bindValue(':id', self.id)
                if not query.exec():
                    raise Exception('Release deletion failed: ' + query.lastError().text())
                print('Release deleted')

            except Exception as e:
                print('Error:', e)
        else:
            print('Database connection is closed!')

    def update(self, edited_data, tracks):
        db = QSqlDatabase.database()
        if db.isOpen():
            try:
                query = QSqlQuery()

                # Editable columns of the release record
                release_columns = {'title', 'artist_credit_phrase', 'format_id', 'type_id', 'release_date', 'cover'}
                release_fields_to_update = []  # list to hold which fields to update
                new_values = {}  # map of new value to column name
                for key in edited_data:
                    if key in release_columns:
                        release_fields_to_update.append(f'{key} = :{key}')
                        new_values[key] = edited_data[key]
                if release_fields_to_update:
                    query.prepare(f'UPDATE "release" SET {', '.join(release_fields_to_update)} WHERE id = :rel_id')
                    query.bindValue(':rel_id', self.id)
                    for col, value in new_values.items():
                        query.bindValue(f':{col}', value)
                    if not query.exec():
                        raise Exception('Release update failed: ' + query.lastError().text())

                # Add new artist connections
                if edited_data.get('added_artist_ids'):
                    self.insert_artist_connections(edited_data['added_artist_ids'])

                # Delete artist connections
                if edited_data.get('deleted_artist_ids'):
                    for artist_id in edited_data.get('deleted_artist_ids', []):
                        query.prepare("""DELETE FROM artist_release
                                         WHERE release_id = :rel_id AND artist_id = :artist_id""")
                        query.bindValue(':rel_id', self.id)
                        query.bindValue(':artist_id', artist_id)
                        if not query.exec():
                            raise Exception('Delete artist_release failed: ' + query.lastError().text())

                # Add new genre connections
                if edited_data.get('added_genre_ids'):
                    self.insert_genre_connections(edited_data['added_genre_ids'])

                # Delete genre connections
                if edited_data.get('deleted_genre_ids'):
                    for genre_id in edited_data.get('deleted_genre_ids', []):
                        query.prepare('DELETE FROM release_genre WHERE release_id = :rel_id AND genre_id = :genre_id')
                        query.bindValue(':rel_id', self.id)
                        query.bindValue(':genre_id', genre_id)
                        if not query.exec():
                            raise Exception('Delete genre_release failed: ' + query.lastError().text())

                if edited_data.get('tracks_edited'):
                    # Delete tracks
                    if edited_data.get('deleted_track_ids'):
                        for track_id in edited_data.get('deleted_track_ids', []):
                            query.prepare('DELETE FROM track WHERE id = :track_id')
                            query.bindValue(':track_id', track_id)
                            if not query.exec():
                                raise Exception('Delete track failed: ' + query.lastError().text())
                    for i, track in enumerate(tracks):
                        # Update track info if edited existing track
                        if track['id']:
                            query.prepare(
                                """UPDATE track
                                   SET actual_position = :actual_pos,
                                       position = :pos,
                                       title = :title,
                                       length = :len
                                   WHERE id = :id"""
                            )
                            query.bindValue(':id', track['id'])
                            query.bindValue(':actual_pos', i)
                            query.bindValue(':pos', track['position'])
                            query.bindValue(':title', track['title'])
                            query.bindValue(':len', track['length'])
                            if not query.exec():
                                raise Exception('Update track failed: ' + query.lastError().text())
                        # Insert track if added
                        else:
                            tracks[i]['id'] = self.insert_track(i, track)
                    self.tracks = tracks
            except Exception as e:
                print('Error:', e)
        else:
            print('Database connection is closed!')

    def insert_artist_connections(self, artist_ids):
        query = QSqlQuery()
        for artist_id in artist_ids:
            query.prepare('INSERT INTO artist_release VALUES (:rel_id, :artist_id)')
            query.bindValue(':rel_id', self.id)
            query.bindValue(':artist_id', artist_id)
            if not query.exec():
                raise Exception('Insert artist_release failed: ' + query.lastError().text())

    def insert_genre_connections(self, genre_ids):
        query = QSqlQuery()
        for genre_id in genre_ids:
            query.prepare('INSERT INTO release_genre (release_id, genre_id) VALUES (:rel_id, :genre_id)')
            query.bindValue(':rel_id', self.id)
            query.bindValue(':genre_id', genre_id)
            if not query.exec():
                raise Exception('Insert genre_release failed: ' + query.lastError().text())

    def insert_track(self, act_pos, track):
        query = QSqlQuery()
        query.prepare("""INSERT INTO track (release_id, actual_position, position, title, length)
                         VALUES (:rel_id, :actual_pos, :pos, :title, :length)""")
        query.bindValue(':rel_id', self.id)
        query.bindValue(':actual_pos', act_pos)
        query.bindValue(':pos', track['position'])
        query.bindValue(':title', track['title'])
        query.bindValue(':length', track['length'])
        if not query.exec():
            raise Exception('Insert track failed: ' + query.lastError().text())
        return query.lastInsertId()

    # Release.get_all()
    # Retrieve all releases from databases with associated information for collection page
    # Return list of Release class objects
    # artist_map/genre_map structure {
    #     'release_id1': [
    #         {
    #             'id': artist1_id,
    #             'name': artist1_name
    #         },
    #         {
    #             'id': artist2_id,
    #             'name': artist2_name
    #         }, ...
    #     ],
    #     'release_id2' [...]
    # }
    @staticmethod
    def get_all():
        db = QSqlDatabase.database()
        if db.isOpen():
            try:
                # Get artists connected to releases and map a list of artists dicts to release_id in artist_map
                artist_query = QSqlQuery(
                    """SELECT artist_release.release_id, artist.id, artist.name
                       FROM artist_release
                       JOIN artist ON artist_release.artist_id = artist.id"""
                )
                if not artist_query.exec():
                    raise Exception('Release artists fetch failed: ' + artist_query.lastError().text())
                artist_map = defaultdict(list)
                while artist_query.next():
                    artist_map[artist_query.value('release_id')].append({
                        'id': artist_query.value('id'),
                        'name': artist_query.value('name')
                    })

                # Get genres connected to releases and map a list of genre dicts to release_id in genre_map
                genre_query = QSqlQuery(
                    """SELECT release_genre.release_id, genre.id, genre.name
                       FROM release_genre
                       JOIN genre ON release_genre.genre_id = genre.id"""
                )
                if not genre_query.exec():
                    raise Exception('Release genre fetch failed: ' + artist_query.lastError().text())
                genre_map = defaultdict(list)
                while genre_query.next():
                    genre_map[genre_query.value('release_id')].append({
                        'id': genre_query.value('id'),
                        'name': genre_query.value('name')
                    })

                main_query = QSqlQuery(
                    """SELECT
                           "release".id,
                           "release".format_id,
                           format.name as format_name,
                           "release".type_id,
                           release_type.name as type_name,
                           "release".release_group_mbid,
                           "release".title,
                           "release".release_date,
                           "release".artist_credit_phrase,
                           "release".cover,
                           "release".added_at
                       FROM "release"
                       JOIN format on "release".format_id = format.id
                       JOIN release_type ON "release".type_id = release_type.id
                       ORDER BY added_at DESC"""
                )
                if not main_query.exec():
                    raise Exception('Release fetch failed: ' + main_query.lastError().text())
                releases = []
                while main_query.next():
                    release = Release(
                        release_type=main_query.value('type_name'),
                        title=main_query.value('release.title'),
                        artist_credit_phrase=main_query.value('release.artist_credit_phrase'),
                        mbid=main_query.value('release.release_group_mbid'),
                        cover=main_query.value('release.cover'),
                        release_date=main_query.value('release.release_date'),
                        release_format=main_query.value('format_name'),
                        added_at=main_query.value('release.added_at'),
                        db_id=main_query.value('release.id'),
                        type_id=main_query.value('release.type_id'),
                        format_id=main_query.value('release.format_id'),
                        artists=artist_map.get(main_query.value('release.id')),
                        genres=genre_map.get(main_query.value('release.id'), [{'name': 'Unknown'}])
                    )
                    releases.append(release)
                return releases
            except Exception as e:
                print('Error:', e)
        else:
            print('Database connection is closed!')

        return None

    # Check if release exists in format in specific format
    @staticmethod
    def exists_in_format(title, release_format):
        db = QSqlDatabase.database()
        if db.isOpen():
            try:
                query = QSqlQuery()
                query.prepare("""SELECT * FROM 'release'
                                 WHERE title = :title AND format_id IN (SELECT id FROM format WHERE name = :format)""")
                query.bindValue(':title', title)
                query.bindValue(':format', release_format)
                if not query.exec():
                    raise Exception('Check format failed: ' + query.lastError().text())

                return query.next()

            except Exception as e:
                print('Error:', e)
                return None
        else:
            print("Database connection is closed!")
            return None

    @staticmethod
    def get_oldest_release():
        db = QSqlDatabase.database()
        if db.isOpen():
            try:
                query = QSqlQuery(
                    """SELECT title, release_date
                       FROM 'release'
                       WHERE release_date IS NOT NULL
                       ORDER BY length(release_date) DESC, release_date ASC
                       LIMIT 1"""
                )
                if not query.exec():
                    raise Exception('Fetch oldest release failed: ' + query.lastError().text())
                if query.next():
                    return query.value('release_date'), query.value('title')

            except Exception as e:
                print('Error:', e)
                return None
        else:
            print("Database connection is closed!")
            return None

    @staticmethod
    def get_newest_release():
        db = QSqlDatabase.database()
        if db.isOpen():
            try:
                query = QSqlQuery(
                    """SELECT title, release_date
                       FROM 'release'
                       WHERE release_date IS NOT NULL
                       ORDER BY length(release_date) DESC, release_date DESC
                       LIMIT 1"""
                )
                if not query.exec():
                    raise Exception('Fetch newest release failed: ' + query.lastError().text())
                if query.next():
                    return query.value('release_date'), query.value('title')

            except Exception as e:
                print('Error:', e)
                return None
        else:
            print("Database connection is closed!")
            return None

    @staticmethod
    def get_average_tracks():
        db = QSqlDatabase.database()
        if db.isOpen():
            try:
                query = QSqlQuery(
                    """SELECT AVG(track_count) AS average FROM (
                            SELECT COUNT(*) AS track_count
                            FROM track
                            GROUP BY release_id
                    )"""
                )
                if not query.exec():
                    raise Exception('Get average tracks failed: ' + query.lastError().text())
                if query.next():
                    return query.value('average')

            except Exception as e:
                print('Error:', e)
                return None
        else:
            print("Database connection is closed!")
            return None
