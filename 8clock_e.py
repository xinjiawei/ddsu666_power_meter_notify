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
import requests


import json
import paho.mqtt.client as mqtt

iyuu_token_list = ["IYUU12866T4e6deff2fadf58093a791e00****************", "IYUU57875T9072c55a05289988442e0a05****************"]
old8_e = 0.0
new8_e = 0.0
power_22c_e = 0.0 

# 获取上次早8点的电表值.
old8_output_file = '8v.json'
try:
    # 打开文件读取内容
    with open(old8_output_file, 'r') as file:
        # 读取并转换为浮点数
        old8_e = float(file.read().strip())

except FileNotFoundError:
    print(old8_output_file + "文件未找到，请确保文件路径正确。")
except ValueError:
    print(old8_output_file + "文件内容无法转换为浮点数，请检查文件内容。")

print("================================")

new8_output_file = "8v.json"

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

# Create a dictionary to hold the external variable
userdata = {'new8_e': ""}

def on_connect(mqttc, userdata, flags, reason_code, properties):
    print("reason_code: " + str(reason_code))


def on_message(mqttc, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    try:
        # 尝试将消息解析为 JSON
        payload = msg.payload.decode()
        data = json.loads(payload)
        
        # 检查是否包含 'total_e' 键
        if 'total_e' in data:
            global new8_e
            new8_e = float(data['total_e'])
            # obj.append(new8_e)
            print(f"Total Energy (total_e): " + str(new8_e))

            # 保存到文件
            with open(new8_output_file, "w") as f:
                f.write(f"{new8_e}\n")
        else:
            print(f"JSON received, but 'total_e' not found: {data}")
    except json.JSONDecodeError:
        # 如果不是 JSON 格式
        print(f"Non-JSON message received: {msg.payload.decode()}")
    mqttc.disconnect()

def on_subscribe(mqttc, userdata, mid, reason_code_list, properties):
    print("Subscribed: " + str(mid) + " " + str(reason_code_list))

def on_log(mqttc, userdata, level, string):
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
# mqttc.on_log = on_log

print("Connecting to "+args.host+" port: "+str(port))
mqttc.connect(args.host, port, args.keepalive)

print("Publishing: "+args.message)
infot = mqttc.publish(args.topic, args.message, qos=args.qos)
infot.wait_for_publish()

time.sleep(args.delay)

# mqttc.loop_start()
mqttc.subscribe("esp32_response")
# mqttc.loop_stop()
mqttc.loop_forever()


print("================================")

# 读取22点的数据
power_22c_output_file = '22v.json'

try:
    # 打开文件读取内容
    with open(power_22c_output_file, 'r') as file:
        # 读取并转换为浮点数
        power_22c_e = float(file.read().strip())

except FileNotFoundError:
    print(power_22c_output_file + "文件未找到，请确保文件路径正确。")
except ValueError:
    print(power_22c_output_file + "文件内容无法转换为浮点数，请检查文件内容。")

# 昨天的峰值电

high_e = format(power_22c_e - old8_e, ".2f")
low_e = format(new8_e - power_22c_e, ".2f")

high_money = format((power_22c_e - old8_e) * 0.55, ".2f")
low_money = format((new8_e - power_22c_e) * 0.3, ".2f")

print(str(old8_e))
print(str(power_22c_e))
print(str(new8_e))

print("h:" + str(high_e) + ", l:" + str(low_e))

print("================================")

for token in iyuu_token_list :
    # Replace with your actual API endpoint
    print("token: " + token)
    url = "https://iyuu.cn/" + token + ".send"

    # Data to send in the POST request
    data = {
        "text": "昨日电费计量",
        "desp": "昨天白天耗电" + str(high_e) + "度, 费用" + str(high_money) + "元, 晚上耗电" + str(low_e) + "度, 费用" + str(low_money) + "元"
    }

    # Sending the POST request
    response = requests.post(url, json=data, headers={"Content-Type": "application/json; charset=UTF-8"})

    # Print the response from the server
    print(response.text)
    time.sleep(args.delay)
