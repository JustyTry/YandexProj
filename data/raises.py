from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Raise(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "raise"

    courier_id = Column(Integer, ForeignKey("courier.courier_id"), primary_key=True)
    rating = Column(Float, nullable=False, default=0)
    earnings = Column(Integer, nullable=False, default=0)
