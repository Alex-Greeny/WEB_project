from flask import *
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from data import db_session
from data.db_session import *
from data.users import User
from data.videos import Videos
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

def main():
    db_session.global_init("db/videohosting.db")
    # app.register_blueprint(jobs_api.blueprint)

    app.run()

    # Создание видео и пользователя

    # video = Videos()
    # video.title = 'test_video'
    # video.description = 'first_test_video'
    # video.filename = 'video1.webm'
    # video.author_id = 1
    # video.publication_date = None
    # video.filename = 'video1.webm'

    # user = User()
    # user.login = 'test_login'
    # user.nickname = 'test'
    # user.email = 'test@yandex.ru'
    # user.modified_date = None


    # db_sess = db_session.create_session()
    # db_sess.add(user)
    #
    # db_sess.commit()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

@app.route('/')
def index():
    db_sess = create_session()
    videos = db_sess.query(Videos).all()
    return render_template('index.html', videos=videos)


@app.route('/video/<int:video_id>')
def video(video_id):
    db_sess = create_session()
    videos = db_sess.query(Videos).all()
    video = [v for v in videos if v.id == video_id]
    print(video)
    return render_template('video.html', video=video[0])


@app.route('/videos/<path:filename>')
def send_video(filename):
    return send_from_directory('videos', filename)


if __name__ == '__main__':
    main()
