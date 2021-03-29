from sqlalchemy import Column, String, Integer, ForeignKey, orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Courier(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "courier"

    courier_id = Column(Integer, primary_key=True)
    courier_type = Column(String, nullable=False)
    regions = Column(String, nullable=False)  # 12;10;1
    working_hours = Column(String, nullable=False)  # 12:30-24:00;
    orders = orm.relation("AssignedOrder", back_populates="courier")
