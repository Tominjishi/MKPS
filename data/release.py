from PySide6.QtSql import QSqlDatabase, QSqlQuery


# Class for handling data to display on release card and storing in DB
class Release:

    def __init__(self, mbid, release_type, title, artist_credit_phrase,  # strings
                 artists, # list
                 tracks = None, genres = None, cover = None, release_date = None, release_format=None, added_at = None, collection_entry_id = None):  # optional
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
        self.collection_entry_id = collection_entry_id

    def insert(self, chosen_format):
        db = QSqlDatabase.database()
        if db.open():
            db.transaction()
            try:
                query = QSqlQuery()
                # Insert collection_entry record
                query.prepare(
                    """INSERT INTO collection_entry(
                        release_group_mbid,
                        type,
                        title,
                        release_date,
                        format,
                        artist_credit_phrase,
                        cover
                    )
                    VALUES(
                        :release_group_mbid,
                        :type,
                        :title,
                        :release_date,
                        :format,
                        :artist_credit_phrase, 
                        :cover
                    )"""
                )
                query.bindValue(':release_group_mbid', self.mbid)
                query.bindValue(':type', self.type)
                query.bindValue(':title', self.title)
                query.bindValue(':release_date', self.release_date)
                query.bindValue(':format', chosen_format)
                query.bindValue(':artist_credit_phrase', self.artist_credit_phrase)
                query.bindValue(':cover', self.cover)
                if not query.exec():
                    raise Exception('Insert collection entry failed: ' + query.lastError().text())
                collection_entry_id = query.lastInsertId()

                for artist in self.artists:
                    # Insert artist if not already in database
                    query.prepare(
                        """INSERT OR IGNORE INTO artist (mbid, type, name)
                        VALUES (:mbid, :type, :name)"""
                    )
                    query.bindValue(':mbid', artist['id'])
                    query.bindValue(':type', artist['type'])
                    query.bindValue(':name', artist['name'])
                    if not query.exec():
                        raise Exception('Insert artist failed: ' + query.lastError().text())

                    # Link genres to artist if artist wasn't in database
                    if query.lastInsertId():
                        for genre in artist.get('genres', []):
                            # Insert genre record if not already in database
                            query.prepare(
                                """INSERT OR IGNORE INTO genre (mbid, name)
                                VALUES (:mbid, :name)"""
                            )
                            query.bindValue(':mbid', genre['id'])
                            query.bindValue(':name', genre['name'])
                            if not query.exec():
                                raise Exception('Insert genre failed: ' + query.lastError().text())

                            # Insert genre link to artist
                            query.prepare(
                                """INSERT INTO genre_link (genre_mbid, vote_count, artist_mbid)
                                VALUES (:genre_mbid, :vote_count, :artist_mbid)"""
                            )
                            query.bindValue(':genre_mbid', genre['id'])
                            query.bindValue(':vote_count', genre['count'])
                            query.bindValue(':artist_mbid', artist['id'])
                            if not query.exec():
                                raise Exception('Insert genre_link failed: ' + query.lastError().text())

                    # Insert artist link to collection entry
                    query.prepare(
                        """INSERT INTO artist_entry_link (collection_entry_id, artist_mbid)
                        VALUES (:collection_entry_id, :artist_mbid)"""
                    )
                    query.bindValue(':collection_entry_id', collection_entry_id)
                    query.bindValue(':artist_mbid', artist['id'])
                    if not query.exec():
                        raise Exception('Insert artist_entry_link failed: ' + query.lastError().text())

                for genre in self.genres:
                    # Insert genre if not already in database
                    query.prepare(
                        """INSERT OR IGNORE INTO genre (mbid, name)
                        VALUES (:mbid, :name)"""
                    )
                    query.bindValue(':mbid', genre['id'])
                    query.bindValue(':name', genre['name'])
                    if not query.exec():
                        raise Exception('Insert genre failed: ' + query.lastError().text())
                    # Insert genre link to collection entry
                    query.prepare(
                        """INSERT INTO genre_link (genre_mbid, vote_count, collection_entry_id)
                        VALUES (:genre_mbid, :vote_count, :collection_entry_id)"""
                    )
                    query.bindValue(':genre_mbid', genre['id'])
                    query.bindValue(':vote_count', genre['count'])
                    query.bindValue(':collection_entry_id', collection_entry_id)
                    if not query.exec():
                        raise Exception('Insert genre_link failed: ' + query.lastError().text())

                # Insert track records
                for track in self.tracks:
                    query.prepare(
                        """INSERT INTO track (number, title, length, collection_entry_id)
                        VALUES (:number, :title, :length, :collection_entry_id)"""
                    )
                    query.bindValue(':number', track['number'])
                    query.bindValue(':title', track['title'])
                    query.bindValue(':length', track['length'])
                    query.bindValue(':collection_entry_id', collection_entry_id)
                    if not query.exec():
                        raise Exception('Insert track failed: ' + query.lastError().text())

                db.commit()
                print('Album inserted')
            except Exception as e:
                print('Error:', e)
                db.rollback()
            finally:
                db.close()
        else:
            print("Failed to open database: ", db.lastError().text())

    def fill_tracks(self):
        db = QSqlDatabase.database()
        if db.open():
            try:
                query = QSqlQuery()
                query.prepare(
                    """SELECT number, title, length
                    FROM track
                    WHERE collection_entry_id = :id"""
                )
                query.bindValue(':id', self.collection_entry_id)
                if not query.exec():
                    raise Exception(
                        'Track fetch failed: ' + query.lastError().text()
                    )
                self.tracks = []
                while query.next():
                    self.tracks.append(
                        {
                            'number': query.value('number'),
                            'title': query.value('title'),
                            'length': query.value('length')
                        }
                    )
            except Exception as e:
                print('Error:', e)
        else:
            print("Failed to open database: ", db.lastError().text())

    @classmethod
    def get_all(cls):
        db = QSqlDatabase.database()
        if db.open():
            try:
                query = QSqlQuery(
                    """SELECT
                        collection_entry.id,
                        collection_entry.type,
                        collection_entry.title,
                        collection_entry.artist_credit_phrase,
                        collection_entry.cover,
                        collection_entry.release_date,
                        collection_entry.added_at,
                        collection_entry.release_group_mbid,
                        collection_entry.format,
                        GROUP_CONCAT(DISTINCT artist.name) AS artist_names,
                        COALESCE(GROUP_CONCAT(DISTINCT genre.name), 'Unknown') AS genre_names
                    FROM collection_entry
                    JOIN artist_entry_link ON artist_entry_link.collection_entry_id = collection_entry.id
                    JOIN artist ON artist_entry_link.artist_mbid = artist.mbid
                    LEFT JOIN genre_link ON genre_link.collection_entry_id = collection_entry.id
                    LEFT JOIN genre ON genre_link.genre_mbid = genre.mbid
                    JOIN track ON track.collection_entry_id = collection_entry.id
                    GROUP BY collection_entry.id
                    ORDER BY added_at DESC"""
                )
                if not query.exec():
                    raise Exception(
                        'Collection entry fetch failed: ' + query.lastError().text()
                    )
                releases = []
                while query.next():
                    release = Release(
                        query.value('collection_entry.release_group_mbid'),
                        query.value('collection_entry.type'),
                        query.value('collection_entry.title'),
                        query.value('collection_entry.artist_credit_phrase'),
                        query.value('artist_names').split(','),
                        genres=query.value('genre_names').split(','),
                        cover=query.value('collection_entry.cover'),
                        release_format=query.value('collection_entry.format'),
                        release_date=query.value('collection_entry.release_date'),
                        added_at=query.value('collection_entry.added_at'),
                        collection_entry_id=query.value('collection_entry.id')
                    )
                    releases.append(release)
                return releases

            except Exception as e:
                print('Error:', e)
        else:
            print("Failed to open database: ", db.lastError().text())

        return None

    @classmethod
    def exists_format(cls, release_mbid, format):
        db = QSqlDatabase.database()
        if db.open():
            try:
                query = QSqlQuery()
                query.prepare(
                    """SELECT COUNT(*) FROM collection_entry
                    WHERE release_group_mbid = :mbid AND format = :format"""
                )
                query.bindValue(':mbid', release_mbid)
                query.bindValue(':format', format)
                if not query.exec():
                    raise Exception(
                        'Check format failed: ' + query.lastError().text()
                    )
                query.next()

                return query.value(0) != 0
            except Exception as e:
                print('Error:', e)
        else:
            print("Failed to open database: ", db.lastError().text())