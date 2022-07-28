import unittest
from unittest.mock import MagicMock
from nextbus import BusHandler

class TestBusHandlerMethods(unittest.TestCase):
    route_mock = [
      {
        "route_id": "901",
        "agency_id": 0,
        "route_label": "METRO Blue Line"
      },
      {
        "route_id": "991",
        "agency_id": 0,
        "route_label": "Blue Line Bus"
      },
      {
        "route_id": "902",
        "agency_id": 0,
        "route_label": "METRO Green Line"
      }
    ]

    direction_mock = [
      {
        "direction_id": 0,
        "direction_name": "Eastbound"
      },
      {
        "direction_id": 1,
        "direction_name": "Westbound"
      }
    ]

    stop_mock = [
      {
        "place_code": "USBA",
        "description": "U.S. Bank Stadium Station"
      },
      {
        "place_code": "GOVT",
        "description": "Government Plaza Station"
      },
      {
        "place_code": "5SNI",
        "description": "Nicollet Mall Station"
      },
      {
        "place_code": "WARE",
        "description": "Warehouse District/ Hennepin Ave Station"
      },
      {
        "place_code": "TF1",
        "description": "Target Field Station Platform 1"
      }
    ]

    time_mock = {
      "stops": [
        {
          "stop_id": 56332,
          "latitude": 44.980177,
          "longitude": -93.273202,
          "description": "Warehouse Hennepin Ave Station"
        }
      ],
      "alerts": [],
      "departures": [
        {
          "actual": True,
          "trip_id": "21225913-JUN22-RAIL-Weekday-02",
          "stop_id": 56332,
          "departure_text": "4 Min",
          "departure_time": 1659014280,
          "description": "to Mpls-Target Field",
          "route_id": "902",
          "route_short_name": "Green",
          "direction_id": 1,
          "direction_text": "WB",
          "schedule_relationship": "Scheduled"
        },
        {
          "actual": True,
          "trip_id": "21225914-JUN22-RAIL-Weekday-02",
          "stop_id": 56332,
          "departure_text": "18 Min",
          "departure_time": 1659015120,
          "description": "to Mpls-Target Field",
          "route_id": "902",
          "route_short_name": "Green",
          "direction_id": 1,
          "direction_text": "WB",
          "schedule_relationship": "Scheduled"
        },
        {
          "actual": False,
          "trip_id": "21226058-JUN22-RAIL-Weekday-02",
          "stop_id": 56332,
          "departure_text": "8:37",
          "departure_time": 1659015420,
          "description": "to Mpls-Target Field",
          "route_id": "902",
          "route_short_name": "Green",
          "direction_id": 1,
          "direction_text": "WB",
          "schedule_relationship": "Scheduled"
        }
      ]
    }


    def test_get_route(self):
        BusHandler.__https_conn__ = MagicMock(return_value=self.route_mock)
        bus_handler = BusHandler("METRO Green Line", 'Warehouse District/ Hennepin Ave Station', 'West')

        self.assertEqual(bus_handler.__get_route__(), "902")


    def test_get_direction(self):
        BusHandler.__https_conn__ = MagicMock(return_value=self.direction_mock)
        bus_handler = BusHandler("METRO Green Line", 'Warehouse District/ Hennepin Ave Station', 'West')

        self.assertEqual(bus_handler.__get_direction__("902"), 1)
        BusHandler.__https_conn__.assert_called_with('/nextripv2/directions/902?format=json')


    def test_get_stop(self):
        BusHandler.__https_conn__ = MagicMock(return_value=self.stop_mock)
        bus_handler = BusHandler("METRO Green Line", 'Warehouse District/ Hennepin Ave Station', 'West')

        self.assertEqual(bus_handler.__get_stop__("902", 1), "WARE")
        BusHandler.__https_conn__.assert_called_with('/nextripv2/stops/902/1?format=json')


    def test_get_time(self):
        BusHandler.__https_conn__ = MagicMock(return_value=self.time_mock)
        bus_handler = BusHandler("METRO Green Line", 'Warehouse District/ Hennepin Ave Station', 'West')

        self.assertEqual(bus_handler.__get_time__("902", 1, "WARE"), "4 Min")
        BusHandler.__https_conn__.assert_called_with('/nextripv2/902/1/WARE?format=json')

    def test_run(self):
        def side_effect_func(url):
            path_count = len(url.split('/'))
            if path_count == 3:
                return self.route_mock
            elif path_count == 4:
                return self.direction_mock
            elif path_count == 5:
                if 'stop' in url:
                    return self.stop_mock
                else:
                    return self.time_mock

        BusHandler.__https_conn__ = MagicMock(side_effect=side_effect_func)
        bus_handler = BusHandler("METRO Green Line", 'Warehouse District/ Hennepin Ave Station', 'West')

        self.assertEqual(bus_handler.run(), "4 Min")

if __name__ == '__main__':
    unittest.main()
