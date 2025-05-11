from flask import *
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from data import db_session
from data.db_session import *
from data.users import User
from data.videos import Videos
import requests
from requests import get, post, delete
import os
from flask_restful import reqparse, abort, Api, Resource
import users_rest
import video_rest
import comment_rest
from forms import LoginForm, RegistrationForm, UploadForm, CommentForm
from werkzeug.security import generate_password_hash, check_password_hash


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


APIURL = "http://localhost:5000"


@app.route('/')
def index():
    videos = get(f'{APIURL}//api/videos').json()
    users = get(f'{APIURL}//api/users').json()
    return render_template('index.html', videos=videos['videos'], users=users['users'], title="VideoPlayer")


@app.route('/video/<int:video_id>', methods=['GET', 'POST'])
def video(video_id):
    # Получение видео по id
    video = get(f'{APIURL}/api/videos/{video_id}').json()['video']
    print(video)

    # Получение автора видео и всех пользователей
    author = list(filter(lambda x: x["id"] == video["author_id"],
                       get(f'{APIURL}/api/users').json()['users']))
    users = list(get(f'{APIURL}/api/users').json()['users'])
    print(author)
    print(users)

    # Получение списка комментариев
    comments = list(filter(lambda x: x["video_id"] == video_id,
                           get(f'{APIURL}/api/comments').json()['comments']))
    print(comments)

    # Форма для написания комментария
    form = CommentForm()
    if form.validate_on_submit():
        text = form.text.data
        if text:
            post(f"{APIURL}//api/comments", json={"id": None,
                                                              "video_id": video_id,
                                                              "author_id": current_user.id,
                                                              "text": form.text.data})
            form.text.data = ''
            return redirect(url_for('video', video_id=video_id))
    return render_template('video.html', video=video, author=author[0], comments=comments, users=users,
                           comms_cnt=len(comments), form=form, title="VideoPlayer")


@app.route('/del_video/<int:video_id>')
def del_video(video_id):
    delete(f'{APIURL}/api/videos/{video_id}')
    return render_template('delete.html', title="Видео удалено")

@app.route('/videos/<path:filename>')
def send_video(filename):
    return send_from_directory('videos', filename)


@app.route('/find', methods=['GET', 'POST'])
def find():
    if request.method == 'POST':
        search_term = request.form['search']
        try:
            videos = list(filter(lambda x: search_term.lower() in x['title'].lower() or search_term.lower() in x['description'].lower(), get(f'{APIURL}/api/videos').json()['videos']))
            if videos[0]:
                return render_template('result.html', videos=videos, search_term=f"Список видео по запросу : {search_term}", title=search_term)
        except:
            return render_template('result.html', videos=[], search_term=f"Не удалось найти видео по запросу: {search_term}", title=search_term)

    videos = get(f'{APIURL}//api/videos').json()
    users = get(f'{APIURL}//api/users').json()
    return render_template('index.html', videos=videos['videos'], users=users['users'], title="VideoPlayer")



@app.route('/videos/<path:filename>')
def send_preview(filename):
    return send_from_directory('static\\previews', filename)


# Авторизация не работает, надо потом доделать.
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               title='Вход',
                               form=form)
    return render_template('login.html', title='Вход', form=form)


# Личный профиль
@app.route('/profile')
def personal_profile():
    videos = list(filter(lambda x: x['author_id'] == current_user.id, get(f'{APIURL}/api/videos').json()['videos']))
    return render_template('personal_profile.html', title="Мой профиль", videos=videos)


# Профиль пользователя
@app.route('/profile/<int:user_id>', methods=['GET'])
def profile(user_id):
    videos = list(filter(lambda x: x['author_id'] == user_id, get(f'{APIURL}/api/videos').json()['videos']))
    print(videos)
    user = list(filter(lambda x: x["id"] == user_id, get(f'{APIURL}/api/users').json()['users']))
    print(user)
    return render_template('profile.html', videos=videos, user=user[0], title=user[0]['nickname'])


@app.route('/registr', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        print(form.password.data)
        if form.password.data == form.secondpassword.data:
            user = get(f"{APIURL}//api/users/{form.login.data}").json()
            print(user)
            if 'login' in user.keys():
                return render_template('registration.html',
                                       message="Пользователь с таким логином уже существует",
                                       title='Регистрация',
                                       form=form)
            post(f"{APIURL}//api/users", json={"id": None,
                                                           "login": form.login.data,
                                                           "nickname": form.username.data,
                                                           "email": form.email.data,
                                                           "hashed_password": form.password.data})
            user = get(f"{APIURL}//api/users").json()['users'][-1]
            user = User(id=user['id'],
                        login=user['login'],
                        nickname=user['nickname'],
                        email=user['email'],
                        hashed_password=user['hashed_password'])
            login_user(user)
            return redirect("/")
        return render_template('registration.html',
                               message="Пароли не совпадают",
                               title='Регистрация', form=form)
    return render_template('registration.html', title='Регистрация', form=form)


# Публикация видео
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.filename.data
        preview = form.preview.data
        if preview:
            if file:
                if file.content_length <= 209715200:  # 200 Mb
                    videofile = file.filename
                    previewfile = preview.filename
                    file.save(os.path.join('videos', videofile))
                    preview.save(os.path.join('static\\previews', previewfile))
                    post(f"{APIURL}//api/videos", json={"id": None,
                                                                    "author_id": current_user.id,
                                                                    "title": form.title.data,
                                                                    "description": form.description.data,
                                                                    "filename": videofile,
                                                                    "preview": previewfile})
                    return redirect("/")
                return render_template('uploading.html',
                                       message="Размер файла слишком велик: max 200 Mb",
                                       title='Публикация', form=form)
            return render_template('uploading.html',
                                   message="Видеофайл не указан",
                                   title='Публикация', form=form)
        return render_template('uploading.html',
                               message="Обложка не указана",
                               title='Публикация', form=form)
    return render_template('uploading.html', title='Публикация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/videohosting.db")

    # для списка объектов
    api.add_resource(users_rest.UsersListResource, '/api/users')
    api.add_resource(video_rest.VideosListResource, '/api/videos')
    api.add_resource(comment_rest.CommentsListResource, '/api/comments')
    # для одного объекта
    api.add_resource(users_rest.UsersResource, '/api/users/<string:login>')
    api.add_resource(video_rest.VideosResource, '/api/videos/<int:video_id>')
    api.add_resource(comment_rest.CommentsResource, '/api/comments/<int:comment_id>')

    app.run()


if __name__ == '__main__':
    main()
