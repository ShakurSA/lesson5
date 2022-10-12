import json
import psycopg2

# читаем файл с фильмами
with open("films.json", "r") as f:
    films = json.load(f)

# подключаемся к БД
con = psycopg2.connect(
    dbname="lesson5",
    user="postgres",
    password="0202020202",
    host="localhost",
    port=5432
)

#  создаем экземпляр курсора, который непосредственно выполняет запросы
cur = con.cursor()

# выполняем создание таблицы
cur.execute("CREATE TABLE films(id serial, name varchar, rating float, country varchar)")

# коммитим изменения в БД, чтобы они сохранились
con.commit()

# подготавливаем inserts для создания записей о фильмах
inserts = ''
for film in films:
    inserts += f"INSERT INTO films values ({film['id']}, '{film['name']}', {film['rating']}, '{film['country']}');\n"

# выполняем inserts
cur.execute(inserts)
# коммитим изменения
con.commit()

# закрываем подключение к БД
cur.close()
con.close()
