from sqlalchemy import Column, String, Integer, Float, orm, ForeignKey
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class CompletedOrder(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "completedOrder"

    order_id = Column(Integer, primary_key=True)
    weight = Column(Float, nullable=False)
    region = Column(Integer, nullable=False)
    assigned_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    courier_id = Column(Integer, ForeignKey("courier.courier_id"))
    courier = orm.relation("Courier")

    def get_values(self):
        return self.order_id, self.weight, self.region, self.delivery_hours
