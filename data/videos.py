import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Videos(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'videos'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    publication_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    filename = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    #comments = orm.relationship("Comments", back_populates='video')

    #user = orm.relationship('User')
