# обработка html запроса к базе данных Users(легкое добавление, удаление, изменение)

from flask_restful import reqparse, abort, Api, Resource
from flask import Flask, jsonify
from data.users import User
from data import db_session
from werkzeug.security import generate_password_hash


app = Flask(__name__)
api = Api(app)


def abort_if_user_not_found(login):
    session = db_session.create_session()
    user = session.query(User).filter(User.login == login).first()
    if not user:
        abort(404, message=f"Пользователь {login} не найден")


class UsersResource(Resource):
    def get(self, login):
        abort_if_user_not_found(login)
        session = db_session.create_session()
        user = session.query(User).filter(User.login == login).first()
        return jsonify({'user': user.to_dict()})

    def delete(self, login):
        abort_if_user_not_found(login)
        session = db_session.create_session()
        user = session.query(User).filter(User.login == login).first()
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def post(self, login):
        abort_if_user_not_found(login)
        session = db_session.create_session()
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, type=int)
        parser.add_argument('login', required=True)
        parser.add_argument('nickname', required=True)
        parser.add_argument('email', required=True, type=str)
        parser.add_argument('hashed_password', required=True)
        args = parser.parse_args()
        session.query(User).filter_by(login=login).update({"id": args['id'],
                                                            "login": args['login'],
                                                            "nickname": args['nickname'],
                                                            "email": args['email']})
        session.commit()
        return jsonify({'success': 'OK'})




class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict() for item in users]})

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, type=int)
        parser.add_argument('login', required=True)
        parser.add_argument('nickname', required=True)
        parser.add_argument('email', required=True, type=str)
        parser.add_argument('hashed_password', required=True)

        args = parser.parse_args(strict=False)
        session = db_session.create_session()
        user = User(
            id = args['id'],
            login = args['login'],
            nickname=args['nickname'],
            email = args['email'],
            hashed_password = args['hashed_password'],
        )
        user.set_password(user.hashed_password)
        session.add(user)
        session.commit()
        return jsonify({'id': user.id})
