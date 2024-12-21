#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (c) 2010-2013 Roger Light <roger@atchoo.org>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution.
#
# The Eclipse Distribution License is available at
#   http://www.eclipse.org/org/documents/edl-v10.php.
#
# Contributors:
#    Roger Light - initial implementation
# Copyright (c) 2010,2011 Roger Light <roger@atchoo.org>
# All rights reserved.

# This shows a simple example of an MQTT subscriber.

# import context  # Ensures paho is in PYTHONPATH
import argparse
import os
import ssl
import time

import json
import paho.mqtt.client as mqtt

output_file = "22v.json"

parser = argparse.ArgumentParser()

parser.add_argument('-H', '--host', required=True, default="act.jiawei.xin")
parser.add_argument('-t', '--topic', required=True, default="sysop-get")
parser.add_argument('-m', '--message', required=True, default="info-power")
parser.add_argument('-q', '--qos', required=False, type=int,default=0)
parser.add_argument('-c', '--clientid', required=True, default="cron-client")
parser.add_argument('-u', '--username', required=True, default="admin")
parser.add_argument('-d', '--disable-clean-session', action='store_true', help="disable 'clean session' (sub + msgs not cleared when client disconnects)")
parser.add_argument('-p', '--password', required=True, default="12345678")
parser.add_argument('-P', '--port', required=False, type=int, default="1883", help='Defaults to 8883 for TLS or 1883 for non-TLS')
parser.add_argument('-S', '--delay', required=False, type=float, default=1, help='number of seconds to sleep between msgs')
parser.add_argument('-k', '--keepalive', required=False, type=int, default=55)
parser.add_argument('-s', '--use-tls', action='store_true')
parser.add_argument('--insecure', action='store_true')
parser.add_argument('-F', '--cacerts', required=False, default=None)
parser.add_argument('--tls-version', required=False, default=None, help='TLS protocol version, can be one of tlsv1.2 tlsv1.1 or tlsv1\n')
parser.add_argument('-D', '--debug', action='store_true')

args, unknown = parser.parse_known_args()


def on_log(mqttc, obj, level, string):
    print(string)

usetls = args.use_tls

if args.cacerts:
    usetls = True

port = args.port
if port is None:
    if usetls:
        port = 18831
    else:
        port = 18830


def on_connect(mqttc, obj, flags, reason_code, properties):
    print("reason_code: " + str(reason_code))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    try:
        # 尝试将消息解析为 JSON
        payload = msg.payload.decode()
        data = json.loads(payload)
        
        # 检查是否包含 'total_e' 键
        if 'total_e' in data:
            print(f"Total Energy (total_e): {data['total_e']}")
            # 保存到文件
            with open(output_file, "w") as f:
                f.write(f"{data['total_e']}\n")
        else:
            print(f"JSON received, but 'total_e' not found: {data}")
    except json.JSONDecodeError:
        # 如果不是 JSON 格式
        print(f"Non-JSON message received: {msg.payload.decode()}")
    mqttc.disconnect()

def on_subscribe(mqttc, obj, mid, reason_code_list, properties):
    print("Subscribed: " + str(mid) + " " + str(reason_code_list))

def on_log(mqttc, obj, level, string):
    print(string)


# If you want to use a specific client id, use
# mqttc = mqtt.Client("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

if usetls:
    if args.tls_version == "tlsv1.2":
       tlsVersion = ssl.PROTOCOL_TLSv1_2
    elif args.tls_version == "tlsv1.1":
       tlsVersion = ssl.PROTOCOL_TLSv1_1
    elif args.tls_version == "tlsv1":
       tlsVersion = ssl.PROTOCOL_TLSv1
    elif args.tls_version is None:
       tlsVersion = None
    else:
       print ("Unknown TLS version - ignoring")
       tlsVersion = None

    if not args.insecure:
        cert_required = ssl.CERT_REQUIRED
    else:
        cert_required = ssl.CERT_NONE

    mqttc.tls_set(ca_certs=args.cacerts, certfile=None, keyfile=None, cert_reqs=cert_required, tls_version=tlsVersion)

    if args.insecure:
        mqttc.tls_insecure_set(True)


# 设置账号和密码
if args.username or args.password:
    mqttc.username_pw_set(args.username, args.password)


mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
mqttc.on_log = on_log

print("Connecting to "+args.host+" port: "+str(port))
mqttc.connect(args.host, port, args.keepalive)

print("Publishing: "+args.message)
infot = mqttc.publish(args.topic, args.message, qos=args.qos)
infot.wait_for_publish()

time.sleep(args.delay)

#mqttc.loop_start()
mqttc.subscribe("esp32_response")
#mqttc.loop_stop()
mqttc.loop_forever()