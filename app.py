import os
from datetime import datetime

from flask import Flask, request, jsonify, make_response, abort

from Utilities import *
from data import db_session
from data.assigned_order import AssignedOrder
from data.completed_orders import CompletedOrder
from data.couriers import *
from data.orders import Order
from waitress import serve

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)



def create_couriers(data) -> Courier:
    courier = Courier()
    courier.courier_id = data['courier_id']
    courier.courier_type = data['courier_type']
    courier.working_hours = convert_to_str(data['working_hours'])
    courier.regions = convert_to_str(data['regions'])
    return courier


def create_order(data) -> Order:
    order = Order()
    order.order_id = data["order_id"]
    order.weight = data["weight"]
    order.region = data["region"]
    order.delivery_hours = convert_to_str(data["delivery_hours"])
    return order


@app.route("/")
def main():
    return "Hello!"


@app.route('/couriers', methods=['POST'])
def add_couriers():
    data = request.get_json()
    if not data:
        return abort(401)
    not_valid = []
    valid = []
    for i in data['data']:

        if not all([key in i for key in ['courier_id', 'courier_type', 'regions', 'working_hours']]):
            not_valid.append({'id': i['courier_id']})
            continue
        valid.append({'id': i['courier_id']})
        session = db_session.create_session()
        courier = create_couriers(i)
        session.add(courier)
        session.commit()

    if not_valid:
        return {'validation_error': {"couriers": not_valid}}, 400
    return {'couriers': valid}, 201


@app.route("/couriers/<int:id>", methods=["PATCH"])
def patch_couriers(id: int):
    try:
        data = request.get_json()
        db_sess = db_session.create_session()
        curr_cour = db_sess.query(Courier).filter(Courier.courier_id == id).first()
        for command in data.items():
            if command[0] == "regions":
                curr_cour.regions = convert_to_str(command[1])
            elif command[0] == "courier_type":
                curr_cour.courier_type = command[1]
            elif command[0] == "working_hours":
                curr_cour.working_hours = convert_to_str(command[1])
            elif command[0] == "courier_id":
                curr_cour.courier_id = command[1]
        db_sess.commit()
        return curr_cour.to_dict(), 200
    except Exception as ex:
        print(ex)
        return abort(400)


@app.route("/orders", methods=["POST"])
def add_orders():
    data = request.get_json()

    not_valid = []
    valid = []
    for i in data['data']:
        if not all([key in i for key in ['order_id', 'weight', 'region', 'delivery_hours']]):
            not_valid.append({'id': i['order_id']})
            continue
        valid.append({'id': i['order_id']})
        session = db_session.create_session()
        order = create_order(i)
        session.add(order)
        session.commit()

    if not_valid:
        return {'validation_error': {"orders": not_valid}}, 400
    return {'orders': valid}, 201


@app.route("/orders/assign", methods=["POST"])
def assign():
    courier_id = request.get_json()["courier_id"]
    session = db_session.create_session()
    try:
        courier = session.query(Courier).get(courier_id)
    except Exception as ex:
        print(ex)
        return abort(400)
    orders = session.query(Order).all()
    ready_for = {"orders": []}
    for order in orders:
        time_now = datetime.now().time()
        courier_ranges = [
            list(range((k := datetime.strptime(t.split("-")[0], "%H:%M").time()).hour * 60 + k.minute,
                       (k := datetime.strptime(t.split("-")[1], "%H:%M").time()).hour * 60 + k.minute)) for
            t in courier.working_hours.split(";")]
        courier_ranges = {k for i in courier_ranges for k in i}
        order_ranges = [
            list(range((k := datetime.strptime(t.split("-")[0], "%H:%M").time()).hour * 60 + k.minute,
                       (k := datetime.strptime(t.split("-")[1], "%H:%M").time()).hour * 60 + k.minute))
            for t in order.delivery_hours.split(";")]
        order_ranges = {k for i in order_ranges for k in i}
        ranges = courier_ranges.intersection(order_ranges)
        if order.weight <= weight_by_type(courier.courier_type) \
                and ranges \
                and order.region in convert_to_list(courier.regions):
            ready_for["orders"].append({"id": order.order_id})
            assigned_order = AssignedOrder()
            assigned_order.order_id = order.order_id
            assigned_order.weight = order.weight
            assigned_order.region = order.region
            assigned_order.delivery_hours = order.delivery_hours
            assigned_order.courier_id = courier_id
            timet = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            assigned_order.assigned_time = timet
            session.add(assigned_order)
            session.delete(order)
            session.commit()
            ready_for["assign_time"] = timet
    return ready_for, 200


@app.route('/orders/complete', methods=["POST"])
def complete_order():
    try:
        courier_id = request.get_json()["courier_id"]
        order_id = request.get_json()["order_id"]
        complete_time = request.get_json()["complete_time"]
    except Exception as ex:
        print(ex)
        return abort(400)
    session = db_session.create_session()
    orders = session.query(AssignedOrder).all()
    if order_id not in [order.order_id for order in orders] or courier_id != session.query(AssignedOrder).get(
            order_id).courier_id:
        return abort(400)
    completed_order = CompletedOrder()
    order = session.query(AssignedOrder).get(order_id)
    completed_order.order_id = order.order_id
    completed_order.weight = order.weight
    completed_order.region = order.region
    completed_order.assigned_time = order.assigned_time
    completed_order.end_time = complete_time
    completed_order.courier_id = order.courier_id
    session.add(completed_order)
    session.delete(order)
    session.commit()
    return {"order_id": order_id}


@app.route('/couriers/<int:courier_id>', methods=['GET'])
def get_info(courier_id):
    sess = db_session.create_session()
    courier = sess.query(Courier).get(courier_id)
    orders = sess.query(CompletedOrder).filter(CompletedOrder.courier_id == Courier.courier_id).all()
    regions = convert_to_list(courier.regions)
    c = {'foot': 2, 'bike': 5, 'car': 9}
    if orders:
        convert = datetime.strptime
        t = {i: [0, 0] for i in regions}
        for ind, val in enumerate(orders):
            print(val.end_time)
            deliver_time = (convert(val.end_time, '%Y-%m-%dT%H:%M:%S.%fZ') - convert(val.assigned_time,
                                                                                     '%Y-%m-%dT%H:%M:%S.%fZ') if ind == 0
                            else convert(orders[ind].end_time, '%Y-%m-%dT%H:%M:%S.%fZ') - convert(
                orders[ind - 1].end_time,
                '%Y-%m-%dT%H:%M:%S.%fZ')).seconds
            t[val.region][0] += deliver_time
            t[val.region][1] += 1
        t = {i: val[0] / val[1] for i, val in t.items() if val[1] != 0}
        t = min(t) if t else 0
        rating = round((60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5, 2)
    else:
        rating = 0
    result = {
        "courier_id": courier_id,
        "courier_type": courier.courier_type,
        "regions": regions,
        "working_hours": courier.working_hours.split(';'),
        "rating": rating,
        "earning": (c[courier.courier_type] * 500 * len(orders)),
    }
    return result, 201


if __name__ == '__main__':
    db_session.global_init("db/service.db")
    serve(app, port=1234, host="127.0.0.1")
