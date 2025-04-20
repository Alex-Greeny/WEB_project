import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Comments(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    video_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("videos.id"), nullable=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    publication_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    video = orm.relationship('Videos')
    user = orm.relationship('User')
