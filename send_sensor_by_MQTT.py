"""
import libraries
"""
# for DHT22 sensor
import Adafruit_DHT
# for MQTT, AWS IoT
import argparse
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
from uuid import uuid4
import json

# setting for DHT22 sensor
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4 # GPIO4
POS = "TH01"

# get argument for MQTT and AWS_IoT
# set path of cert as set before 
#     for detial: https://dongwon18.github.io/categories/#aws_iot
parser = argparse.ArgumentParser(description="Send and receive messages through and MQTT connection.")
parser.add_argument('--endpoint', required=True, help="Your AWS IoT custom endpoint, not including a port. " +
                                                      "Ex: \"abcd123456wxyz-ats.iot.us-east-1.amazonaws.com\"")
parser.add_argument('--port', default = 8883, type = int, help="Specify port. AWS IoT supports 443 and 8883.")
parser.add_argument('--client-id', default="test-" + str(uuid4()), help="Client ID for MQTT connection.")
parser.add_argument('--topic', default="test/topic", help="Topic to subscribe to, and publish messages to.")
parser.add_argument('--use-websocket', default=False, action='store_true',
    help="To use a websocket instead of raw mqtt. If you " +
    "specify this option you must specify a region for signing.")
parser.add_argument('--root', default= '/home/pi/certs/Amazon-root-CA-1.pem', help="Root ca path")
parser.add_argument('--cert', default= '/home/pi/certs/device.pem.crt', help="cert path")
parser.add_argument('--key', default= '/home/pi/certs/private.pem.key', help="private key path")
parser.add_argument('--proxy-host', help="Hostname of proxy to connect to.")
parser.add_argument('--proxy-port', type=int, default=8080, help="Port of proxy to connect to.")
parser.add_argument('--verbosity', choices=[x.name for x in io.LogLevel], default=io.LogLevel.NoLogs.name,
    help='Logging level')

# Using globals to simplify sample code
args = parser.parse_args()

io.init_logging(getattr(io.LogLevel, args.verbosity), 'stderr')


# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))

# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)

def on_resubscribe_complete(resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))


if __name__ == '__main__':
    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    proxy_options = None
    if (args.proxy_host):
        proxy_options = http.HttpProxyOptions(host_name=args.proxy_host, port=args.proxy_port)

    if args.use_websocket == True:
        credentials_provider = auth.AwsCredentialsProvider.new_default_chain(client_bootstrap)
        mqtt_connection = mqtt_connection_builder.websockets_with_default_aws_signing(
            endpoint=args.endpoint,
            client_bootstrap=client_bootstrap,
            region='ap-northeast-2',
            credentials_provider=credentials_provider,
            http_proxy_options=proxy_options,
            ca_filepath= args.root,
            on_connection_interrupted=on_connection_interrupted,
            on_connection_resumed=on_connection_resumed,
            client_id=args.client_id,
            clean_session=False,
            keep_alive_secs=30)

    else:
        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=args.endpoint,
            port=args.port,
            cert_filepath= args.cert,
            pri_key_filepath= args.key,
            client_bootstrap=client_bootstrap,
            ca_filepath= args.root,
            on_connection_interrupted=on_connection_interrupted,
            on_connection_resumed=on_connection_resumed,
            client_id=args.client_id,
            clean_session=False,
            keep_alive_secs=30,
            http_proxy_options=proxy_options)

    print("Connecting to {} with client ID '{}'...".format(
        args.endpoint, args.client_id))

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    print("Subscribing to topic '{}'...".format(args.topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=args.topic,
        qos=mqtt.QoS.AT_MOST_ONCE
        #callback=on_message_received
        )

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))
    
    try:
        # Publish message to server every 5 second.
        # This step loops 5 times until user enter KeyboardInterrupt
        # If you want to get the value all the time, change while statement
        # If you want to get the value more often, change sleep time
        
        i = 0
        while(i < 5):
             # read data from sensor
            humidity, temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            if(humidity == None or temp == None):
                print("Reading DHT failed")
            else:
                print("{}C {}%".format(temp, humidity))
            
            # change data to json form
            payload = {"temperature":temp, "humidity":humidity}        
            print("Publishing message to topic '{}': temperature: {}, humidity: {}".format(args.topic, temp, humidity))

            # publish the message
            mqtt_connection.publish(
                    topic=args.topic,
                    payload=json.dumps(payload),
                    qos=mqtt.QoS.AT_LEAST_ONCE)
            i += 1
            time.sleep(5)

    # when KeyboardInterrupt, disconnect the device            
    except KeyboardInterrupt:        
        # Disconnect
        print("Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")
