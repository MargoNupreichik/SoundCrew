from sqlalchemy import create_engine, text

engine = create_engine("mysql+mysqlconnector://root:password@localhost:3306/soundcrew", echo=True)
    
class Manager():
    
    # Сведения о группе (год образования, страна)
    @staticmethod
    def get_group_info(group_name):
        
        with engine.connect() as connection:
            query_text = "SELECT :group_name AS group_name, name, country, founded_in , hit_parade_position FROM bands WHERE name = :group;"
            params = {"group": group_name}
            result = connection.execute(text(query_text), params).fetchone()
        
        if result:
            result = list(result)
        else:
            result = None
        
        return result
    
    # # Репертуар наиболее популярной группы
    @staticmethod
    def most_popular_band_repertoire(band):
        
        with engine.connect() as connection:
            
            band_id_query = "SELECT id_band \
                        FROM bands \
                        WHERE hit_parade_position = (SELECT MIN(hit_parade_position) FROM bands) LIMIT 1;"
            band_id = connection.execute(text(band_id_query)).fetchone()[0]
            
            band_name_query = "SELECT name FROM bands WHERE id_band=:id"
            params = {"id": band_id}
            band = connection.execute(text(band_name_query), params).fetchone()[0]
            
            query = "SELECT title FROM soundcrew.songs WHERE m_id_band = :band_id"
            params = {'band_id': band_id}              
            
            result = connection.execute(text(query), params).fetchall()
            if result:
                result = list(result)
            else:
                return None        
        
        for row in result:
            result.append(row[0])
        return result.insert(0, band)
    
    # Посмотреть сведения о песне (автор текса, композитор, дата создания)
    @staticmethod
    def get_song_info(song):
        
        with engine.connect() as connection:
            
            query = "SELECT songs.title, songs.create_date, m_1.fio AS composer, m_2.fio AS textwritter, songs.m_id_band\
                    FROM songs \
                    JOIN musicians AS m_1 ON m_1.id_musician = songs.composer \
                    JOIN musicians AS m_2 ON m_2.id_musician = songs.textwriter \
                    WHERE title = :song_name;"
            params = {'song_name': song}              
            
            result = connection.execute(text(query), params).fetchone()
            if result:
                result = list(result)
            else:
                return None
            
            band_name_query = "SELECT name FROM bands WHERE id_band = :id"
            band_id = result.pop(-1) 
            params = {'id': band_id} 
        
            result.insert(0,connection.execute(text(band_name_query), params).fetchone()[0])
        
        return result
        
    # Сведения о группе (место и продолжительность гастролей)
    @staticmethod
    def get_tour_info(band):
        
        with engine.connect() as connection:
            
            query = "SELECT :group_name as group_name, name, DATEDIFF(end_date, begin_date) AS duration_in_days, place \
                    FROM soundcrew.tours \
                    WHERE t_id_band = (SELECT id_band FROM soundcrew.bands WHERE name = :group_name);"
            params = {'group_name': band}              
            
            result = connection.execute(text(query), params).fetchone()
            if result:
                result = list(result)
            else:
                result = None
        
        return result
    
    # 'Сведения о группе (цена билета на концерт)'
    @staticmethod
    def get_ticket_price(band):
        
        with engine.connect() as connection:
            query_text = "SELECT :group_name AS group_name, name, place, ticket_price \
                        FROM tours \
                        WHERE t_id_band = (SELECT id_band FROM bands WHERE name = :group_name) \
                        ORDER BY end_date \
                        LIMIT 1;"
            params = {"group_name": band}
            result = connection.execute(text(query_text), params).fetchone()
        
        if result:
            result = list(result)
        else:
            result = None
        
        return result
        
    # 'Сведения о группе (состав исполнителей, их возраст и амплуа)'
    @staticmethod
    def get_members_info(band):
        
        with engine.connect() as connection:
            query_text = "SELECT fio, age, role \
                        FROM musicians \
                        WHERE m_id_band = (SELECT id_band FROM bands WHERE name = :group_name);"
            params = {"group_name": band}
            result = connection.execute(text(query_text), params).fetchall()
            
            if result:
                description = list()
                description.append(band)
                for row in result:
                    description.append(list(row))
            else:
                return None
        
        return description
    