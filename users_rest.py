# обработка html запроса к базе данных Users(легкое добавление, удаление, изменение)

from flask_restful import reqparse, abort, Api, Resource
from flask import Flask, jsonify
from data.users import User
from data import db_session



app = Flask(__name__)
api = Api(app)


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"Пользователь с id  {user_id} не найден")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict()})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def post(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, type=int)
        parser.add_argument('login', required=True)
        parser.add_argument('nickname', required=True)
        parser.add_argument('email', required=True, type=str)
        parser.add_argument('hashed_password', required=True)
        parser.add_argument('modified_date', required=True)
        args = parser.parse_args()
        session.query(User).filter_by(id=user_id).update({"id": args['id'],
                                                            "login": args['login'],
                                                            "nickname": args['nickname'],
                                                            "email": args['email'],
                                                            "hashed_password": args['hashed_password'],
                                                            "modified_date": args['modified_date']})
        session.commit()
        return jsonify({'success': 'OK'})




class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = list(session.query(User).all())
        return jsonify({'users': [item.to_dict() for item in users]})

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, type=int)
        parser.add_argument('login', required=True)
        parser.add_argument('nickname', required=True, type=bool)
        parser.add_argument('email', required=True, type=str)
        parser.add_argument('hashed_password', required=True)
        parser.add_argument('modified_date', required=True)

        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            id = args['id'],
            login = args['login'],
            nickname=args['nickname'],
            email = args['email'],
            hashed_password= args['hashed_password'],
            modified_date = args['modified_date']
        )
        session.add(user)
        session.commit()
        return jsonify({'id': user.id})
