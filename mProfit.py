from flask import Flask, request, jsonify
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
import ssl
import json
import subprocess
import logging
import time
import threading


# SETTINGS
magi_rpc_user = 'user'
magi_rpc_password = 'pass'
magi_rpc_ip = 'localhost'
magi_rpc_port = '8232'

host_ip = '0.0.0.0'
host_port = 443
allowed_origins = '*'
pem_file_location = 'file.pem'
key_file_location = 'file.key'

periodic_reset_timing = 60
time_between_requests = 3


# CODE
server_flag = False
reset_flag = False
periodic_reset_flag = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/calculate/*": {"origins": allowed_origins, "methods": ["OPTIONS", "POST"]}})

context = None
server = None

old_request = time.time()

def spam():
    global old_request
    new_request = time.time()
    spam_time = new_request - old_request

    return spam_time

def call_magi_rpc(method, params=[]):
    rpc_url = f'http://{magi_rpc_user}:{magi_rpc_password}@{magi_rpc_ip}:{magi_rpc_port}/'
    request_payload = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": method, "params": params})
    response = subprocess.run(['curl', '-s', '-H', 'Content-Type: application/json', '--data', request_payload, rpc_url], capture_output=True, text=True)

    return json.loads(response.stdout)

def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def start_server():
    global context
    global server
    global server_flag
    global reset_flag
    global periodic_reset_flag

    if server_flag == False:
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.load_cert_chain(certfile=pem_file_location, keyfile=key_file_location)
            server = WSGIServer((host_ip, host_port), app, ssl_context=context)
            server_flag = True
            periodic_reset_flag = False
            reset_flag = False
            logger.info("Success")
            server.serve_forever()
        except:
            server_flag = False
            periodic_reset_flag = False
            reset_flag = False
            logger.info("Fixing error...")
            fix_error()
    else:
        logger.info("Fixing error...")
        fix_error()

def fix_error():
    global context
    global server
    global server_flag
    global reset_flag
    global periodic_reset_flag

    try:
        server.close()
    finally:
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.load_cert_chain(certfile=pem_file_location, keyfile=key_file_location)
            server = WSGIServer((host_ip, host_port), app, ssl_context=context)
            server_flag = True
            periodic_reset_flag = False
            reset_flag = False
            logger.info("Error fixed")
            server.serve_forever()
        except:
            server_flag = False
            periodic_reset_flag = False
            reset_flag = False
            logger.info("Fixing error...")

def reset_state():
    global server_flag
    global reset_flag
    global periodic_reset_flag

    time.sleep(0.5)
    logger.info("Resetting state...")
    periodic_reset_flag = False
    if server_flag == True and reset_flag == False:
        try:
            server.close()
        except:
            logger.info("Fixing error...")
            fix_error()
        else:
            server_flag = False
            reset_flag = True
            start_server()
    else:
        logger.info("Fixing error...")
        fix_error()

def async_reset_state():
    thread = threading.Thread(target=reset_state)
    thread.start()

def periodic_reset():
    global server_flag
    global periodic_reset_flag

    while True:
        time.sleep(periodic_reset_timing)
        if periodic_reset_flag == False:
            periodic_reset_flag = True
            async_reset_state()
        else:
            logger.info("Fixing error...")
            fix_error()

@app.route('/calculate/mining', methods=['POST'])
def calculate_mining():
    global old_request
    spam_time = spam()
    if spam_time >= time_between_requests:
        old_request = time.time()

        logger.info("Request received for mPoW calculation")

        start_time = time.time()

        data = request.json
        hashrate = data.get('hashrate')

        hashrate = hashrate.replace(',', '.')

        if not is_number(hashrate):
            return jsonify({"error": "Invalid hashrate value. Must be a number."}), 400

        hashrate = float(hashrate)

        mining_response = call_magi_rpc('getminingbykhps', [round(hashrate, 3)])
        mining_constant = mining_response['result']['mining (XMG)']['1 day']

        h_m = round(mining_constant / 24, 2)
        d_m = round(mining_constant, 2)
        w_m = round(mining_constant * 7, 2)
        m_m = round(mining_constant * 30, 2)
        y_m = round(mining_constant * 365, 2)

        info_response = call_magi_rpc('getmininginfo')
        pow = info_response['result']['difficulty']['proof-of-work']
        pos = info_response['result']['difficulty']['proof-of-stake']
        blval = info_response['result']['blockvalue']['blockvalue']
        netweight = info_response['result']['netstakeweight']
        stakeint = info_response['result']['stakeinterest']
        nethash = info_response['result']['networkhashps']

        m_a = round(pow, 5)
        m_b = round(blval, 2)
        m_c = round(nethash / 1000, 3)
        s_a = round(pos, 5)
        s_b = round(stakeint * 100, 2)
        s_c = round(netweight)

        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Request finished for mPoW calculation in: {elapsed_time:.2f}s")

        response = jsonify({
            'h_m': f"{h_m} XMG",
            'd_m': f"{d_m} XMG",
            'w_m': f"{w_m} XMG",
            'm_m': f"{m_m} XMG",
            'y_m': f"{y_m} XMG",
            'm_a': m_a,
            'm_b': f"{m_b} XMG",
            'm_c': f"{m_c} kH/s",
            's_a': s_a,
            's_b': f"{s_b} %",
            's_c': s_c
        })

        async_reset_state()

        return response

    else:
        logger.warning("Spam detected")
        return jsonify({"error": "Too many requests. Please wait a moment."}), 429

@app.route('/calculate/staking', methods=['POST'])
def calculate_staking():
    global old_request
    spam_time = spam()
    if spam_time >= time_between_requests:
        old_request = time.time()

        logger.info("Request received for mPoS calculation")

        start_time = time.time()

        data = request.json
        balance = data.get('balance')

        balance = balance.replace(',', '.')

        if not is_number(balance):
            return jsonify({"error": "Invalid balance value. Must be a number."}), 400

        stakeval = float(balance)

        info_response = call_magi_rpc('getmininginfo')
        pow = info_response['result']['difficulty']['proof-of-work']
        pos = info_response['result']['difficulty']['proof-of-stake']
        blval = info_response['result']['blockvalue']['blockvalue']
        netweight = info_response['result']['netstakeweight']
        stakeint = info_response['result']['stakeinterest']
        nethash = info_response['result']['networkhashps']

        staking_constant = stakeint * stakeval

        h_s = round(staking_constant / 8760, 5)
        d_s = round(staking_constant / 365, 4)
        w_s = round(staking_constant / 52, 3)
        m_s = round(staking_constant / 12, 2)
        y_s = round(staking_constant, 2)

        m_a = round(pow, 5)
        m_b = round(blval, 2)
        m_c = round(nethash / 1000, 3)
        s_a = round(pos, 5)
        s_b = round(stakeint * 100, 2)
        s_c = round(netweight)

        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Request finished for mPoS calculation in: {elapsed_time:.2f}s")

        response = jsonify({
            'h_s': f"{h_s} XMG",
            'd_s': f"{d_s} XMG",
            'w_s': f"{w_s} XMG",
            'm_s': f"{m_s} XMG",
            'y_s': f"{y_s} XMG",
            'm_a': m_a,
            'm_b': f"{m_b} XMG",
            'm_c': f"{m_c} kH/s",
            's_a': s_a,
            's_b': f"{s_b} %",
            's_c': s_c
        })

        async_reset_state()

        return response
    else:
        logger.warning("Spam detected")
        return jsonify({"error": "Too many requests. Please wait a moment."}), 429

if __name__ == '__main__':
    reset_thread = threading.Thread(target=periodic_reset)
    reset_thread.start()

    logger.info(f"Starting server on https://{host_ip}:{host_port}...")

    start_server()