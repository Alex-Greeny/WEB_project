from flask import *
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from data import db_session
from data.db_session import *
from data.users import User
from data.videos import Videos
from requests import get, post, delete
import os
from flask_restful import reqparse, abort, Api, Resource
import users_rest
import video_rest

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)




@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

@app.route('/')
def index():
    videos = get('http://localhost:5000//api/videos').json()
    return render_template('index.html', videos=videos['videos'])


@app.route('/video/<int:video_id>')
def video(video_id):
    video = get(f'http://localhost:5000//api/videos/{video_id}').json()
    return render_template('video.html', video=video['video'])


@app.route('/videos/<path:filename>')
def send_video(filename):
    return send_from_directory('videos', filename)


# Авторизация не работает, надо потом доделать.
@app.route('/login', methods=['GET', 'POST'])
def auth():
    error = None
    password = 0
    if password == 'password':  # Пример: простой ввод
        return redirect(url_for('/index'))  # Перенаправить на главную страницу
    else:
        error = 'Неверное имя пользователя или пароль'

    return render_template('login.html', error=error)



def main():
    db_session.global_init("db/videohosting.db")

    # для списка объектов
    api.add_resource(users_rest.UsersListResource, '/api/users')
    api.add_resource(video_rest.VideosListResource, '/api/videos')
    # для одного объекта
    api.add_resource(users_rest.UsersResource, '/api/users/<int:user_id>')
    api.add_resource(video_rest.VideosResource, '/api/videos/<int:video_id>')

    app.run()


if __name__ == '__main__':
    main()
