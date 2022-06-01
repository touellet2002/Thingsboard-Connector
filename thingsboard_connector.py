import time
import requests
import json
import paho.mqtt.client as mqtt
from threading import Thread

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKORANGE = '\033[93m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Http_Connector():
    def __init__(self, host, port, access_token, debug=False):
        """
        Initialize the HTTP connector.
        
        Takes the following arguments:
        host: The hostname of the ThingsBoard server.
        port: The port of the ThingsBoard server.
        access_token: The access token of the gateway.
        debug: If debug mode is enable.

        Returns the following:
        A Http_Connector object.
        """

        # Validate data
        if type(host) is not str:
            raise ValueError(f'{bcolors.FAIL}Host must be a string.{bcolors.ENDC}')

        if type(port) is not str:
            raise ValueError(f'{bcolors.FAIL}Port must be a string.{bcolors.ENDC}')

        if type(access_token) is not str:
            raise ValueError(f'{bcolors.FAIL}Access token must be a string.{bcolors.ENDC}')

        # Initialize Http connector
        self.debug = debug
        self.data = {}
        self.host = host
        self.port = port
        self.access_token = access_token
        self.headers = {'Content-Type': 'application/json'}

    def enable_debug(self):
        """
        Enable debug mode.
        Enabling debug mode allow the connector to print debug messages.
        """
        self.debug = True

    def disable_debug(self):
        """
        Disable debug mode.
        Disabling debug mode prevent the connector to print debug messages except if an exception occurs.
        """
        self.debug = False
    
    def send_telemetry(self):
        """
        Send data to the ThingsBoard server to the device using predefined access token.
        
        Takes the following arguments:
        None.

        Returns the following:
        None.
        """
        # Start new thread to send data
        thread = Thread(target=self._send_telemetry_thread, args=(self.host, self.port, self.access_token, self.headers, self.data, bcolors, self.debug))
        thread.start()
        return thread
    
    def _send_telemetry_thread(self, host, port, access_token, headers, data, bcolors, debug=False):
        """
        Thread to send data to the host.
        
        Takes the following arguments:
        host: The hostname of the host.
        port: The port of the host.
        access_token: The access token of the gateway.

        Returns the following:
        thread: the thread that send data to the host.
        """
        url = 'http://' + host + ':' + port + '/api/v1/' + access_token + '/telemetry'
        try:
            if debug:
                print("\n")
                print(f'{bcolors.OKBLUE}== Sending telemetry (HTTP) =={bcolors.ENDC}')
                print("Sending data (", str(data), ")\nto host", host, "\non port", port, "\nwith access token", access_token)
            
            response = requests.post(url, headers=headers, json=data)
            
            if debug:
                print("Response:", response.status_code)
                if(response.status_code == 200):
                    print(f'{bcolors.OKGREEN}== Successfully sent telemetry (HTTP) =={bcolors.ENDC}')
                else:
                    print(f"Error :{bcolors.FAIL}:", response.status_code, f"{bcolors.ENDC}")
                print("\n")
        except requests.exceptions.RequestException as e:
            print(e)


    def set_single_data(self, key, value):
        """
        Set data to be sent to the ThingsBoard server.
        The data is used in the send_data() method.

        Takes the following arguments:
        key: The key of the data.
        value: The value of the data.

        Returns the following:
        None.
        """
        self.data[key] = value

    def set_multiple_data(self, data):
        """
        Set data to be sent to the ThingsBoard server.
        The data is used in the send_data() method.

        Takes the following arguments:
        data: The data to be sent (dictionnary of key/value).

        Returns the following:
        None.
        """
        self.data = data

class Mqtt_Connector():
    def __init__(self, host, port, access_token, debug=False):
        """
        __init__ initializes the Mqtt_Connector class.
        It connects to the broker and sets the on_connect and on_message functions.
        It also sets the data to an empty dictionary.

        Takes the following arguments:
        host: host of the broker
        port: port of the broker
        access_token: access token of the device (used as the username in the MQTT broker)
        debug: if debug mode is enabled

        Returns the following:
        A Mqtt_Connector object
        """

        # Validate data format
        if type(host) is not str:
            raise ValueError('host must be a string')

        if type(port) is not int:
            raise ValueError('port must be an integer')

        if type(access_token) is not str:
            raise ValueError('access_token must be a string')

        # Initialize MQTT Connector
        self.debug = debug
        self.data = {}
        self.gateway_data = {}
        self.host = host
        self.port = port
        self.username = access_token
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(access_token, None)

        try:
            if debug:
                print("\n")
                print(f"{bcolors.OKORANGE}== Connection to host (MQTT) == {bcolors.ENDC}")
                print("Connecting to host", self.host, "\non port", self.port, "\nwith access token", self.username)

            response = self.client.connect(self.host, self.port, 60)

            if debug:
                # Response code meanings based on documentation: https://www.vtscada.com/help/Content/D_Tags/D_MQTT_ErrMsg.htm
                if response == 0:
                    print(f"{bcolors.OKGREEN}== Successfully connected to host (MQTT) == {bcolors.ENDC}")
                elif response == 1:
                    print(f"{bcolors.FAIL}Connection refused{bcolors.ENDC} - incorrect protocol version ")
                elif response == 2:
                    print(f"{bcolors.FAIL}Connection refused{bcolors.ENDC} - invalid client identifier")
                elif response == 3:
                    print(f"{bcolors.FAIL}Connection refused{bcolors.ENDC} - server unavailable")
                elif response == 4:
                    print(f"{bcolors.FAIL}Connection refused{bcolors.ENDC} - bad username or password")
                elif response == 5:
                    print(f"{bcolors.FAIL}Connection refused{bcolors.ENDC} - not authorised")
                else :
                    print(f"{bcolors.FAIL}Connection refused or failed{bcolors.ENDC} - see {bcolors.OKCYAN}https://www.vtscada.com/help/Content/D_Tags/D_MQTT_ErrMsg.htm{bcolors.ENDC} for more information on error codes\nERROR CODE :", response)
        except Exception as e:
            print(f"{bcolors.FAIL} Connection failed{bcolors.ENDC} - \n", e)

    def enable_debug(self):
        """
        Activate debug mode.
        It will print debug messages in the console.

        Takes the following arguments:
        None.

        Returns the following:
        None.
        """
        self.debug = True

    def disable_debug(self):
        """
        Disable debug mode.
        Disabling debug mode will prevent debug messages from being printed in the console except for exceptions.

        Takes the following arguments:
        None.

        Returns the following:
        None.
        """
        self.debug = False


    def on_connect(self, client, userdata, flags, rc):
        """
        on_connect function is called when the client connects to the broker

        Takes the following arguments:
        client: client object
        userdata: userdata object
        flags: flags object
        rc: return code

        Returns the following:
        None
        """
        print("Connected with result code " + str(rc))

    def on_message(self, client, userdata, msg):
        """
        on_message function is called when a message is received

        Takes the following arguments:
        client: client object
        userdata: userdata object
        msg: message object

        Returns the following:
        None
        """
        print(msg.topic + " " + str(msg.payload))
    
    def send_telemetry(self):
        """
        send_telemetry send the data added to the connector using the add_data function.
        It sends the data to Thingsboard using the v1/devices/me/telemtry topic.
        
        Takes the following arguments:
        None

        Returns the following:
        thread : the thread that is used to send the data
        """

        # Send data to Thingsboard in thread
        thread = Thread(target=self._send_telemetry_thread, args=(self.client, self.data, self.debug))
        thread.start()
        return thread


    def _send_telemetry_thread(self, client, data, debug):
        """
        _send_telemetry_thread is a thread that sends the data added to the connector using the add_data function.
        It sends the data to Thingsboard using the v1/devices/me/telemtry topic.
        
        Takes the following arguments:
        client: client object
        data: data object
        debug: debug object

        Returns the following:
        None
        """
        # Send data to Thingsboard
        try: 
            if debug:
                print("\n")
                print(f"{bcolors.OKORANGE}== Sending telemetry (MQTT) =={bcolors.ENDC}")
                print("Sending data (", str(data), ")\nto host ", self.host, "\non port", self.port, "\nwith access token", self.username)

            response = client.publish('v1/devices/me/telemetry', json.dumps({ "ts": int(time.time()), "values": data }))

            if debug:
                if response[0] == mqtt.MQTT_ERR_SUCCESS:
                    print(f'{bcolors.OKGREEN}== Successfully sent telemetry (MQTT) =={bcolors.ENDC}')
                elif response[0] == mqtt.MQTT_ERR_NO_CONN:
                    print(f"{bcolors.FAIL}Data not sent{bcolors.ENDC} - no connection to broker")
                elif response[0] == mqtt.MQTT__ERR_QUEUE_SIZE:
                    print(f"{bcolors.FAIL}Data not sent{bcolors.ENDC} - queue size exceeded")
                else:
                    print(f"{bcolors.FAIL}Data not sent{bcolors.ENDC} - unknown error\nERROR CODE :", response[0])
                    print("\n")
        except Exception as e:
            print(f"{bcolors.FAIL}Sending data failed{bcolors.FAIL} - \nERROR : ", e)

    def set_single_data(self, key, value):
        """
        set_single_data adds the data to the connector.
        This data is used in the send_telemetry function.
        
        Takes the following arguments:
        key: key of the data
        value: value of the data

        Returns the following:
        None
        """

        # Validate data format
        if type(key) is not str:
            raise ValueError('key must be a string')

        if type(value) is not int and type(value) is not float and type(value) is not str and type(value) is not bool:
            raise ValueError('value must be an int, float, string or boolean')

        # Add data to gateway_data
        self.data[key] = value

    def set_multiple_data(self, data):
        """
        set_multiple_data adds data to the specified device.
        This data is used in the send_telemetry function.

        Takes the following arguments:
        data: data to add to the device (dictionary of key-value pairs) 

        Returns the following:
        None
        """

        # Validate data format
        if type(data) is not dict:
            raise ValueError('data must be a dictionary')
        
        for key in data:
            if type(key) is not str:
                raise ValueError('key must be a string')
            
            if type(data[key]) is not int and type(data[key]) is not float and type(data[key]) is not str and type(data[key]) is not bool:
                raise ValueError('value must be an int, float, string or boolean')

        # Add data to gateway_data
        self.data = data

    def remove_data(self, key):
        """
        remove_data removes the data from the connector.
        This data removed will no longer be sent to Thingsboard using the send_telemetry function.

        Takes the following arguments:
        key: key of the data

        Returns the following:
        None
        """

        # Validate data format
        if type(key) is not str:
            raise ValueError('key must be a string')

        # Remove data from data
        del self.data[key]

    def remove_all_data(self, data):
        """
        remove_all_data removes all the data from the connector.
        This data removed will no longer be sent to Thingsboard using the send_telemetry function.

        Takes the following arguments:
        None

        Returns the following:
        None
        """

        # Remove data from data
        self.data = {}


    # ======= GATEWAY FUNCTIONS =======
    # def connect_device_to_gateway(self, device_name, group_name = ""):
    #     """
    #     *** This function only works if the device is considered as a gateway in Thingsboard. ***
    #     connect_device_to_gateway connects the specified device to the gateway.
    #     Doing so will allow the gateway to send telemetry in behalf of the device.

    #     Takes the following arguments:
    #     device_name: name of the device to connect to the gateway

    #     Returns the following:
    #     None
    #     """
    #     # Start thread
    #     thread = Thread(target=self.connect_device_to_gateway_thread, args=(self.client, device_name, group_name, self.debug))
    #     thread.start()

    # def _connect_device_to_gateway_thread(self, client, device_name, group_name = "", debug = False):
    #     """
    #     *** This function only works if the device is considered as a gateway in Thingsboard. ***
    #     _connect_device_to_gateway connects the specified device to the gateway.
    #     Doing so will allow the gateway to send telemetry in behalf of the device.

    #     Takes the following arguments:
    #     device_name: name of the device to connect to the gateway

    #     Returns the following:
    #     None
    #     """

    #     # Validate data format
    #     if type(device_name) is not str:
    #         raise ValueError('device_id must be a string')

    #     try:
    #         # Add data to gateway_data
    #         if debug:
    #             print("\n")
    #             print(f"{bcolors.OKORANGE}== Connecting device to gateway (MQTT) =={bcolors.ENDC}")
    #             print("Connecting device", device_name, "to gateway")

    #         response = client.publish('v1/gateway/connect', json.dumps({'device': device_name, 'group': group_name}))

    #         if debug:
    #             if response[0] == mqtt.MQTT_ERR_SUCCESS:
    #                 print(f'{bcolors.OKGREEN}== Successfully connected device to gateway (MQTT) =={bcolors.ENDC}')
    #             elif response[0] == mqtt.MQTT_ERR_NO_CONN:
    #                 print(f"{bcolors.FAIL}Data not sent{bcolors.ENDC} - no connection to broker")
    #             elif response[0] == mqtt.MQTT__ERR_QUEUE_SIZE:
    #                 print(f"{bcolors.FAIL}Data not sent{bcolors.ENDC} - queue size exceeded")
    #             else:
    #                 print(f"{bcolors.FAIL}Data not sent{bcolors.ENDC} - unknown error\nERROR CODE :", response[0])
    #     except Exception as e:
    #         print(f"{bcolors.FAIL}Connecting device failed{bcolors.FAIL} - \nERROR : ", e)


    # def discconnect_device_from_gateway(self, device_name):
    #     """
    #     *** This function only works if the device is considered as a gateway in Thingsboard. ***
    #     discconnect_device_from_gateway disconnects the specified device from the gateway.
    #     Doing so will prevent the gateway from sending telemetry in behalf of the device.

    #     Takes the following arguments:
    #     device_name: name of the device to disconnect from the gateway

    #     Returns the following:
    #     thread: thread that is used to send the data
    #     """
    #     # Start thread
    #     thread = Thread(target=self._disconnect_device_from_gateway_thread, args=(self.client, device_name, self.debug))
    #     thread.start()
    #     return thread

    # def _discconnect_device_from_gateway_thread(self, client, device_name, debug = False):
    #     """
    #     *** This function only works if the device is considered as a gateway in Thingsboard. ***
    #     discconnect_device_from_gateway disconnects the specified device from the gateway.
    #     Doing so will prevent the gateway from sending telemetry in behalf of the device.

    #     Takes the following arguments:
    #     device_name: name of the device to disconnect from the gateway

    #     Returns the following:
    #     None
    #     """

    #     # Validate data format
    #     if type(device_name) is not str:
    #         raise ValueError('device_id must be a string')

    #     try:
    #         # Remove data from gateway_data
    #         if debug:
    #             print("\n")
    #             print(f"{bcolors.OKORANGE}== Disconnecting device from gateway (MQTT) =={bcolors.ENDC}")
    #             print("Disconnecting device", device_name, "from gateway")

    #         response = client.publish('v1/gateway/disconnect', json.dumps({'device': device_name}))

    #         if debug:
    #             if response[0] == mqtt.MQTT_ERR_SUCCESS:
    #                 print(f'{bcolors.OKGREEN}== Successfully disconnected device from gateway (MQTT) =={bcolors.ENDC}')
    #             elif response[0] == mqtt.MQTT_ERR_NO_CONN:
    #                 print(f"{bcolors.FAIL}Data not sent{bcolors.ENDC} - no connection to broker")
    #             elif response[0] == mqtt.MQTT__ERR_QUEUE_SIZE:
    #                 print(f"{bcolors.FAIL}Data not sent{bcolors.ENDC} - queue size exceeded")
    #             else:
    #                 print(f"{bcolors.FAIL}Data not sent{bcolors.ENDC} - unknown error\nERROR CODE :", response[0])
    #     except Exception as e:
    #         print(f"{bcolors.FAIL}Disconnecting device failed{bcolors.FAIL} - \nERROR : ", e)
    
    # def set_single_device_data(self, device_name, key, value):
    #     """
    #     *** This function only works if the device is considered as a gateway in Thingsboard. ***
    #     set_single_device_data adds data to the specified device.
    #     This data will be sent to the device using the send_telemetry_as_gateway function.

    #     Takes the following arguments:
    #     device_name: name of the device to add data to
    #     key: key of the data (string)
    #     value: value of the data (string, int, float or boolean)

    #     Returns the following:
    #     None
    #     """

    #     # Validate the data
    #     if type(device_name) is not str:
    #         raise TypeError('device_name must be a string')
        
    #     if type(key) is not str:
    #         raise TypeError('key must be a string')
        
    #     if type(value) is not str and type(value) is not int and type(value) is not float and type(value) is not bool:
    #         raise TypeError('value must be a string, int, float or boolean')

    #     # Add the data to the gateway
    #     if device_name in self.gateway_data:
    #         # Get current array from device
    #         device_data = self.gateway_data[device_name][0]

    #         # Set ts
    #         device_data["ts"] = int(time.time() * 1000)

    #         # Add the data to the array
    #         device_data["values"][key] = value

    #         # Update the array in the gateway
    #         self.gateway_data[device_name] = [device_data]
    #     else:
    #         self.gateway_data[device_name] = [{ "ts": int(time.time()), "values": { key: value } }]


    # def set_multiple_device_data(self, device_name, data):
    #     """
    #     *** This function only works if the device is considered as a gateway in Thingsboard. ***
    #     set_multiple_device_data adds data to the specified device.
    #     This data will be sent to the device using the send_telemetry_as_gateway function.

    #     Takes the following arguments:
    #     device_id: id of the device to add the data to (access token of the device)
    #     data: data to add to the device (dictionnary of key/value pairs)

    #     Returns the following:
    #     None
    #     """
        
    #     # Validate data format
    #     if type(device_name) is not str:
    #         raise ValueError('device_name must be a string')

    #     if type(data) is not dict:
    #         raise ValueError('Data must be a dictionary')
    #     for key in data:
    #         if type(key) is not str:
    #             raise ValueError('Data keys must be strings')

    #         if type(data[key]) is not str and type(data[key]) is not int and type(data[key]) is not float and type(data[key]) is not bool:
    #             raise ValueError('Data values must be strings, int, float or boolean')

    #     # Add data to gateway_data
    #     if(device_name in self.gateway_data):
    #         # Get current array from device
    #         device_data = self.gateway_data[device_name][0]

    #         device_data["values"] = data
    #         # Set timestamp
    #         device_data["ts"] = int(time.time() * 1000)

    #         # Update the array in the gateway
    #         self.gateway_data[device_name] = [device_data]
    #     else:
    #         self.gateway_data[device_name] = [{"ts": int(time.time()), "values": data}]
    
    # def remove_device_data(self, device_name, key):
    #     """
    #     *** This function only works if the device is considered as a gateway in Thingsboard. ***
    #     remove_device_data removes the data from the specified device.
    #     This data will no longer be sent to the device using the send_telemetry_as_gateway function.

    #     Takes the following arguments:
    #     device_name: name of the device to remove the data from
    #     key: key of the data (string)

    #     Returns the following:
    #     None
    #     """

    #     # Validate data format
    #     if type(key) is not str:
    #         raise ValueError('Key must be a string')
    #     else: 
    #         # String with every special character in it
    #         specialCharacters = '!@#$%^&*()[]{};:,./<>?\|`~-=_+'
    #         # Replace every special character with an underscore
    #         for char in specialCharacters:
    #             device_name = device_name.replace(char, '_')

    #     # Remove data from gateway_data
    #     if device_name in self.gateway_data:
    #         del self.gateway_data[device_name]["values"][key]
    #     else:
    #         raise ValueError('Device not found')

    # def remove_all_device_data(self, device_name):
    #     """
    #     *** This function only works if the device is considered as a gateway in Thingsboard. ***
    #     remove_all_device_data removes all data from the specified device.
    #     This data will no longer be sent to the device using the send_telemetry_as_gateway function.

    #     Takes the following arguments:
    #     device_name: name of the device to remove all data from

    #     Returns the following:
    #     None
    #     """
    #     # Validate data format
    #     if type(device_name) is not str:
    #         raise ValueError('device_name must be a string')

    #     # Remove data from gateway_data
    #     if device_name in self.gateway_data:
    #         del self.gateway_data[device_name]
    #     else:
    #         raise ValueError('Device not found')
       
    # async def send_telemetry_as_gateway(self):
    #     """
    #     *** This function only works if the device is considered as a gateway in Thingsboard. ***
    #     send_telemetry_as_gateway sends the data to the gateway.
    #     This data will be sent to the device using the set_device_data function.

    #     Takes the following arguments:
    #     None

    #     Returns the following:
    #     None
    #     """

    #     try:
    #         # Send data to gateway
    #         print("\n")
    #         print(f"{bcolors.OKORANGE}== Sending data to gateway (MQTT) =={bcolors.ENDC}")
    #         print("Send data", self.gateway_data, "to gateway")
    #         response = self.client.publish('v1/gateway/telemetry', json.dumps(self.gateway_data))
    #         if response[0] == mqtt.MQTT_ERR_SUCCESS:
    #             print(f"{bcolors.OKGREEN}== Data sent to gateway (MQTT) =={bcolors.ENDC}")
    #         elif response[0] == mqtt.MQTT_ERR_NO_CONN:
    #             print(f"{bcolors.FAIL}Data not sent{bcolors.ENDC} - No connection to broker")
    #         elif response[0] == mqtt.MQTT_ERR_QUEUE_SIZE:
    #             print(f"{bcolors.FAIL}Data not sent{bcolors.ENDC} - queue size exceeded")
    #         else:
    #             print(f"{bcolors.FAIL}Data not sent{bcolors.ENDC} - unknown error")
    #     except Exception as e:
    #         print(f"{bcolors.FAIL}Sending telemetry failed{bcolors.ENDC} -\nError :", e)


    

    



