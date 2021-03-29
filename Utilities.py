def convert_to_list(data) -> list:
    return [int(i) for i in data.split(';')]


def convert_to_str(data) -> str:
    return ';'.join([str(i) for i in data])


def weight_by_type(courier_type) -> int:
    if courier_type == "foot":
        return 10
    elif courier_type == "bike":
        return 15
    elif courier_type == "car":
        return 50

