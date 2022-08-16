import ujson


def convert_twenty_four_to_twelve_hour(hour):
    if hour <= 12:
        return hour
    elif hour == 13:
        return 1
    elif hour == 14:
        return 2
    elif hour == 15:
        return 3
    elif hour == 16:
        return 4
    elif hour == 17:
        return 5
    elif hour == 18:
        return 6
    elif hour == 19:
        return 7
    elif hour == 20:
        return 8
    elif hour == 21:
        return 9
    elif hour == 22:
        return 10
    elif hour == 23:
        return 11


def convert_celsius_to_temperature(temp):
    return (temp * 1.8) + 32


def read_json_file(filename):
    with open(filename) as json_file:
        data = ujson.loads(json_file.read())
        return data


def write_json_file(filename, json_dict):
    json_string = ujson.dumps(json_dict)
    with open(filename, "w") as json_file:
        json_file.write(json_string)
