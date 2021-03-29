from sqlalchemy import Column, String, Integer, Float, orm, ForeignKey
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Order(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "order"

    order_id = Column(Integer, primary_key=True)
    weight = Column(Float, nullable=False)
    region = Column(Integer, nullable=False)
    delivery_hours = Column(String, nullable=False)

    def get_values(self):
        return self.order_id, self.weight, self.region, self.delivery_hours
