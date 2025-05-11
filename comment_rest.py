from flask_restful import reqparse, abort, Api, Resource
from flask import Flask, jsonify
from data.comments import Comments
from data import db_session


app = Flask(__name__)
api = Api(app)


def abort_if_comment_not_found(comment_id):
    session = db_session.create_session()
    comment = session.query(Comments).get(comment_id)
    if not comment:
        abort(404, message=f"Комментарий не найден")


class CommentsResource(Resource):
    def get(self, comm_id):
        abort_if_comment_not_found(comm_id)
        session = db_session.create_session()
        comment = session.query(comm_id).get(comm_id)
        return jsonify({'comment': comment.to_dict()})

    def delete(self, comm_id):
        abort_if_comment_not_found(comm_id)
        session = db_session.create_session()
        comment = session.query(comm_id).get(comm_id)
        session.delete(comment)
        session.commit()
        return jsonify({'success': 'OK'})

    def post(self, comm_id):
        abort_if_comment_not_found(comm_id)
        session = db_session.create_session()
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, type=int)
        parser.add_argument('video_id', required=True, type=int)
        parser.add_argument('author_id', required=True, type=int)
        parser.add_argument('text', required=True, type=str)
        args = parser.parse_args()
        session.query(Comments).filter_by(id=comm_id).update({"id": args['id'],
                                                              "video_id": args['video_id'],
                                                              "author_id": args['author_id'],
                                                              "text": args['text']})
        session.commit()
        return jsonify({'success': 'OK'})


class CommentsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        comments = session.query(Comments).all()
        return jsonify({'comments': [item.to_dict() for item in comments]})

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, type=int)
        parser.add_argument('video_id', required=True, type=int)
        parser.add_argument('author_id', required=True, type=int)
        parser.add_argument('text', required=True, type=str)

        args = parser.parse_args(strict=False)
        session = db_session.create_session()
        comment = Comments(
            id=args['id'],
            video_id=args['video_id'],
            author_id=args['author_id'],
            text=args['text'],
        )
        session.add(comment)
        session.commit()
        return jsonify({'id': comment.id})