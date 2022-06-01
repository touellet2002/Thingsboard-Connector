import unittest
import asyncio
import thingsboard_connector

class TestHTTPConnector(unittest.TestCase):

    def test_set_single_data(self):
        Http_Connector = thingsboard_connector.Http_Connector('thingsboard.cloud', '80', 'test_c2t3')
        Http_Connector.set_single_data("powerFactor", 0.75)
        self.assertEqual(Http_Connector.data, {'powerFactor': 0.75})

    def test_set_multiple_data(self):
        Http_Connector = thingsboard_connector.Http_Connector('thingsboard.cloud', "80", 'test_c2t3')
        Http_Connector.set_multiple_data({"powerFactor": 0.75, "voltage": 220})
        self.assertEqual(Http_Connector.data, {'powerFactor': 0.75, 'voltage': 220})

    def test_send_telemetry(self):
        Http_Connector = thingsboard_connector.Http_Connector('thingsboard.cloud', '80', 'test_c2t3')
        Http_Connector.enable_debug()
        Http_Connector.set_multiple_data({"powerFactor": 0.75, "voltage": 220})
        thread = Http_Connector.send_telemetry()
        thread.join() # wait for thread to finish


class TestMQTTConnector(unittest.TestCase):

    def test_set_single_data(self):
        Mqtt_Connector = thingsboard_connector.Mqtt_Connector("thingsboard.cloud", 1883, "test_c2t3")
        Mqtt_Connector.set_single_data("powerFactor", 0.75)
        self.assertEqual(Mqtt_Connector.data, {'powerFactor': 0.75})

    def test_set_multiple_data(self):
        Mqtt_Connector = thingsboard_connector.Mqtt_Connector("thingsboard.cloud", 1883, "test_c2t3")
        Mqtt_Connector.set_multiple_data({"powerFactor": 0.75, "voltage": 220})
        self.assertEqual(Mqtt_Connector.data, {'powerFactor': 0.75, 'voltage': 220})

    def test_send_telemetry(self):
        Mqtt_Connector = thingsboard_connector.Mqtt_Connector("thingsboard.cloud", 1883, "test_c2t3")
        Mqtt_Connector.enable_debug()
        Mqtt_Connector.set_multiple_data({"powerFactor": 0.75, "voltage": 220})
        thread = Mqtt_Connector.send_telemetry()
        thread.join() # wait for thread to finish
        
if __name__ == '__main__':
    unittest.main()