from sqlalchemy import create_engine, text
from datetime import date
engine = create_engine("mysql+mysqlconnector://root:password@localhost:3306/soundcrew", echo=True)
    
class Manager():
    
    # Сведения о группе (год образования, страна)
    @staticmethod
    def get_group_info(group_name):
        
        with engine.connect() as connection:
            query_text = "SELECT name, country, founded_in , hit_parade_position FROM bands WHERE name = :group;"
            params = {"group": group_name}
            result = connection.execute(text(query_text), params).fetchone()
        
        if result == None:
            return None
        
        return list(result)
    
    # # Репертуар наиболее популярной группы
    @staticmethod
    def most_popular_band_repertoire():
        
        with engine.connect() as connection:
            
            band_id_query = "SELECT id_band \
                        FROM bands \
                        WHERE hit_parade_position = (SELECT MIN(hit_parade_position) FROM bands WHERE hit_parade_position IS NOT NULL) LIMIT 1;"
            band_id = connection.execute(text(band_id_query)).fetchone()[0]
            
            band_name_query = "SELECT name FROM bands WHERE id_band=:id"
            params = {"id": band_id}
            band = connection.execute(text(band_name_query), params).fetchone()[0]
            
            query = "SELECT title FROM songs WHERE m_id_band = :id"
            
            result = connection.execute(text(query), params).fetchall()
            
            if result == None:
                return None
            
            fixed_result = [band]
            for song in result:
                fixed_result.append(list(song)[0])       
        
        return fixed_result
    
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
            
            if result == None:
                return None
            
            result = list(result)
            
            band_name_query = "SELECT name FROM bands WHERE id_band = :id"
            band_id = result.pop(-1) 
            params = {'id': band_id} 
        
            result.insert(0, connection.execute(text(band_name_query), params).fetchone()[0])
        
        return result
        
    # Сведения о группе (место и продолжительность гастролей)
    @staticmethod
    def get_tour_info(band):
        
        with engine.connect() as connection:
            
            query = "SELECT :group_name as group_name, name, begin_date, DATEDIFF(end_date, begin_date) AS duration_in_days, end_date, place \
                    FROM soundcrew.tours \
                    WHERE t_id_band = (SELECT id_band FROM soundcrew.bands WHERE name = :group_name);"
            params = {'group_name': band}              
            
            result = connection.execute(text(query), params).fetchone()
            if result == None:
                return None
        
        return list(result)
    
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

class HelpInformation:
    
    # 'Справка (лучшие группы в хит параде)'
    @staticmethod
    def best_hit_parade_groups():
        
        with engine.connect() as connection:
            query_text = "SELECT name, hit_parade_position \
                          FROM bands WHERE hit_parade_position IS NOT NULL\
                          ORDER BY hit_parade_position Limit 10;"
            result = connection.execute(text(query_text)).fetchall()
        
        if result:
            group_list = list()
            for row in result:
                group_list.append(list(row))
            return group_list
        else:
            return None
    
    # 'Отчет о гастролях групп'
    @staticmethod
    def tour_report():
        
        with engine.connect() as connection:
            query_text = "SELECT bands.name AS band_name, tours.name AS tour_name, tours.begin_date, tours.end_date, tours.ticket_price \
                        FROM tours JOIN bands ON bands.id_band = tours.t_id_band \
                        ORDER BY tours.end_date DESC;"
            result = connection.execute(text(query_text)).fetchall()
        
        if result:
            for row in result:
                group_list = list()
                group_list.append(group_list)
                for row in result:
                    group_list.append(list(row))
        else:
            return None
        
        return group_list   

class Admin:
    
    # 'Добавить новую группу'
    @staticmethod
    def insert_new_group(group_name, foundation_date, country, members_list, songs_list):
        
        with engine.connect() as connection:
            transaction = connection.begin()
            
            try:
                query_text = "INSERT INTO bands (name, country, founded_in) \
                            VALUES (:group_name, :country, :founded_in);"
                params = {"group_name": group_name, "country": country, "founded_in": foundation_date}
                connection.execute(text(query_text), params)
            
                band_id_query = "SELECT id_band \
                        FROM bands \
                        WHERE name = :group_name;"
                params = {"group_name": group_name}
                band_id = connection.execute(text(band_id_query), params).fetchone()[0]
            
                query_text = "INSERT INTO musicians (fio, age, role, m_id_band) \
                        VALUES (:fio, :age, :role, :m_band_id);"
            
                for member in members_list:
                    params = {"fio": member[0], "age": member[1], "role": member[2], "m_band_id": band_id}
                    connection.execute(text(query_text), params)
            
                query_text = "INSERT INTO songs (title, create_date, composer, textwriter, m_id_band) \
                        VALUES (:title, :create_date, :composer, :textwriter, :m_band_id);"
            
                for song in songs_list:
                
                    inner_query_text = "SELECT id_musician \
                        FROM musicians \
                        WHERE fio = :musician;"
                    params = {"musician": song[2]}
                    composer_id = connection.execute(text(inner_query_text), params).fetchone()[0]
                
                    params = {"musician": song[3]}
                    textwriter_id = connection.execute(text(inner_query_text), params).fetchone()[0]
                
                    params = {"title": song[0], "create_date": song[1], "composer": composer_id, "textwriter": textwriter_id, "m_band_id": band_id}
                    connection.execute(text(query_text), params)
            
                transaction.commit()
                return True
            
            except Exception as E:
                transaction.rollback()
                print(E)
                return False
    
    # 'Изменить положение группы в хит-параде'
    @staticmethod
    def change_group_position_hit_parade(group_name, new_position):
        
        with engine.connect() as connection:
            transaction = connection.begin()
            
            try:
                query_text = "SELECT hit_parade_position FROM bands WHERE name = :group_name;"
                params = {"group_name": group_name}
                old_position = connection.execute(text(query_text), params).fetchone()            

                query_text = "SELECT id_band FROM bands WHERE hit_parade_position = :new_position;"
                params = {"new_position": new_position}
                id_changed_position = connection.execute(text(query_text), params).fetchone()
                   
                query_text = "UPDATE bands SET hit_parade_position = :new_position WHERE name = :group_name;"
                params = {"group_name": group_name, "new_position": new_position}
                connection.execute(text(query_text), params) 

                if id_changed_position != None:
                    query_text = "UPDATE bands SET hit_parade_position = :old_position WHERE id_band = :id_changed_position;"
                    params = {"old_position": old_position[0], "id_changed_position": id_changed_position[0]}
                    connection.execute(text(query_text), params) 
            
                transaction.commit()
                return True
            
            except:
                transaction.rollback()
                return False
    
    # 'Удалить информацию об исполнителе'
    def delete_group(group_name):
        
        with engine.connect() as connection:
            transaction = connection.begin()
            
            try:
                query_text = "DELETE FROM bands WHERE name = :group_name;"
                params = {"group_name": group_name}
                connection.execute(text(query_text), params) 
                transaction.commit()
                return True
            
            except:
                transaction.rollback()
                return False
