from flask import Flask, redirect, url_for, render_template, request, make_response, session
import datetime
from db_util import Database

# инициализируем приложение
# из документации:
#     The flask object implements a WSGI application and acts as the central
#     object.  It is passed the name of the module or package of the
#     application.  Once it is created it will act as a central registry for
#     the view functions, the URL rules, template configuration and much more.

app = Flask(__name__, static_folder='./static')

# нужно добавить секретный код - только с ним можно менять данные сессии

app.secret_key = '111'

# необходимо добавлять, чтобы время сессии не ограничивалось закрытием браузера
app.permanent_session_lifetime = datetime.timedelta(days=365)

# инициализация класса с методами для работы с БД
db = Database()


# дальше реализуем методы, которые мы можем выполнить из браузера,
# благодаря указанным относительным путям

# метод для создания куки
@app.route('/add_cookie')
def add_cookie():
    resp = make_response('Add cookie')
    resp.set_cookie('theme', 'value')
    return resp


# метод для удаления куки
@app.route('/delete_cookie')
def delete_cookie():
    resp = make_response('Delete cookie')
    resp.set_cookie('test', 'val', 0)


# реализация визитов
@app.route('/visits')
def visits():
    visit_count = session['visits'] if 'visits' in session.keys() else 0
    session['visits'] = visit_count + 1

    return f"Количество визитов: {session['visits']}"


# удаление данных о посещениях
@app.route("/delete_visits")
def delete_visits():
    session.pop('visits')
    return "ok"


# метод, который возвращает список фильмов по относительному адресу /films
@app.route("/films", methods=['GET', 'POST'])
def films_list():
    if request.method == 'POST':
        db.insert(
            f"INSERT INTO films (id, name, rating, country) VALUES ({request.form.get('id')}, '{request.form.get('name')}', {request.form.get('rating')}, '{request.form.get('country')}')")

    films = db.select(f"SELECT * FROM films")

    # получаем GET-параметр country
    country = request.args.get("country")
    rating = request.args.get("rating")
    if rating:
        films = [i for i in films if float(i['rating']) >= float(rating)]
    # формируем контекст для генерации шаблона
    context = {
        'films': films,
        'title': "FILMS",
        'country': country
    }
    # возвращаем сгенерированный шаблон с нужным нам контекстом
    return render_template("films.html", **context)


# метод, который возвращает конкретный фильмо по id по относительному пути /film/<int:film_id>,
# где film_id - id необходимого фильма
@app.route("/film/<int:film_id>")
def get_film(film_id):
    # используем метод-обертку для выполнения запросов к БД
    film = db.select(f"SELECT * FROM films WHERE id = {film_id}")

    if len(film):
        return render_template("film.html", title=film['name'], film=film)

    # если нужный фильм не найден, возвращаем шаблон с ошибкой
    return render_template("error.html", error="Такого фильма не существует в системе")

@app.route("/change_mode", methods=['GET', "POST"])
def change_mode():
    if request.method == "POST":
        resp = make_response(redirect(url_for('films_list')))
        userInput = request.form.get("userInput")
        if userInput == 'True':
            resp.set_cookie('theme', 'dark')
        else:
            resp.set_cookie('theme', 'light')
        return resp
    return render_template('theme.html')

if __name__ == '__main__':
    app.run(port=5432, debug=True, host='localhost')