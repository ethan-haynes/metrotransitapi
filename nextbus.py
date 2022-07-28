import http.client, json, sys

class BusHandler:
    __metro_host__ = 'svc.metrotransit.org'
    __dirs__ = {
            'SOUTH' : 'Southbound',
            'EAST'  : 'Eastbound',
            'WEST'  : 'Westbound',
            'NORTH' : 'Northbound'
    }

    def __init__(self, route, stop, direction):
        try:
            self.route = route
            self.stop = stop
            self.direction = self.__dirs__[direction.upper()]
        except KeyError:
            print(f'{direction} is not a valid direction. Please choose between [North, South, East, West]')

    def __https_conn__(self, url):
        conn = http.client.HTTPSConnection(self.__metro_host__)
        conn.request("GET", url)
        res = conn.getresponse()
        data = json.loads(res.read())
        return data

    def __get_route__(self):
        data, route = self.__https_conn__('/nextripv2/routes?format=json'), None
        for item in data:
            if self.route == item['route_label']:
                route = item['route_id']
        if not route:
            raise ValueError(f'{self.route} is not a valid Route.\nPlease choose between {[i["Description"] for i in data]}')

        return route

    def __get_direction__(self, route):
        data, direction_id = self.__https_conn__(f'/nextripv2/directions/{route}?format=json'), None
        for item in data:
            if self.direction == item['direction_name']:
                direction_id = item['direction_id']
        if not direction_id:
            raise ValueError(f'{self.direction} is not a valid Direction.\nPlease choose between {[i["direction_name"] for i in data]}')

        return direction_id

    def __get_stop__(self, route, direction):
        data, stop = self.__https_conn__(f'/nextripv2/stops/{route}/{direction}?format=json'), None
        for item in data:
            if self.stop == item['description']:
                stop = item['place_code']
        if not stop:
            raise ValueError(f'{self.stop} is not a valid Stop.\nPlease choose between {[i["Text"] for i in data]}')

        return stop

    def __get_time__(self, route, direction, stop):
        data, time = self.__https_conn__(f'/nextripv2/{route}/{direction}/{stop}?format=json'), None
        departures = data['departures']

        if departures and len(departures):
            return departures[0]['departure_text']

    def run(self):
        route = self.__get_route__()
        direction_id = self.__get_direction__(route)
        stop = self.__get_stop__(route, direction_id)
        time = self.__get_time__(route, direction_id, stop)
        if time:
            return time

if __name__ == '__main__':
    try:
        if len(sys.argv) != 4:
            raise ValueError('Input did not include {Route} {Stop} and {Direction}')
        _, route, stop, direction = sys.argv
        bus_handler = BusHandler(route, stop, direction)
        print(bus_handler.run())
    except ValueError as error:
        print(error)
