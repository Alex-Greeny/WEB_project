# обработка html запроса к базе данных Videos(легкое добавление, удаление, изменение)

from flask_restful import reqparse, abort, Api, Resource
from flask import Flask, jsonify
from data.videos import Videos
from data import db_session


app = Flask(__name__)
api = Api(app)


def abort_if_video_not_found(video_id):
    session = db_session.create_session()
    video = session.query(Videos).get(video_id)
    if not video:
        abort(404, message=f"Видео не найдено")


class VideosResource(Resource):
    def get(self, video_id):
        abort_if_video_not_found(video_id)
        session = db_session.create_session()
        video = session.query(Videos).get(video_id)
        return jsonify({'video': video.to_dict()})

    def delete(self, video_id):
        abort_if_video_not_found(video_id)
        session = db_session.create_session()
        video = session.query(Videos).get(video_id)
        session.delete(video)
        session.commit()
        return jsonify({'success': 'OK'})

    def post(self, video_id):
        abort_if_video_not_found(video_id)
        session = db_session.create_session()
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, type=int)
        parser.add_argument('author_id', required=True)
        parser.add_argument('title', required=True, type=bool)
        parser.add_argument('description', required=True, type=str)
        parser.add_argument('publication_date', required=True)
        parser.add_argument('filename', required=True)
        parser.add_argument('preview', required=True)
        args = parser.parse_args()
        session.query(Videos).filter_by(id=video_id).update({"id": args['id'],
                                                            "author_id": args['author_id'],
                                                             "title": args['title'],
                                                             "description": args['description'],
                                                             "publication_date": args['publication_date'],
                                                             "filename": args['filename'],
                                                             "preview": args['preview']})
        session.commit()
        return jsonify({'success': 'OK'})


class VideosListResource(Resource):
    def get(self):
        session = db_session.create_session()
        videos = list(session.query(Videos).all())
        return jsonify({'videos': [item.to_dict() for item in videos]})

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, type=int)
        parser.add_argument('author_id', required=True)
        parser.add_argument('title', required=True)
        parser.add_argument('description', required=True, type=str)
        parser.add_argument('filename', required=True)
        parser.add_argument('preview', required=True)
        args = parser.parse_args()
        session = db_session.create_session()
        video = Videos(
            id=args['id'],
            author_id=args['author_id'],
            title=args['title'],
            description=args['description'],
            filename=args['filename'],
            preview=args['preview']
        )
        session.add(video)
        session.commit()
        return jsonify({'id': video.id})
