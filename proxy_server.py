#!/usr/bin/env python3
from flask import Flask, request, jsonify
import requests
import random
import logging
import urllib3

# ===== DISABLE SSL WARNINGS =====
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

PROXY_TARGET = "https://api.dts.freefireth.com"

features = {
    "headshot_90": False,
    "headshot_50": False,
    "fast_revive": False
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NEO_ENGINE_PRO")

@app.route('/control', methods=['POST'])
def control():
    cmd = request.form.get('cmd', '')
    logger.info(f"📥 Command: {cmd}")
    
    if cmd == "headshot_90_on":
        features["headshot_90"] = True
        logger.info("🎯 Headshot 90% ON")
    elif cmd == "headshot_90_off":
        features["headshot_90"] = False
        logger.info("🎯 Headshot 90% OFF")
    elif cmd == "headshot_50_on":
        features["headshot_50"] = True
        logger.info("🎯 Headshot 50% ON")
    elif cmd == "headshot_50_off":
        features["headshot_50"] = False
        logger.info("🎯 Headshot 50% OFF")
    elif cmd == "fast_revive_on":
        features["fast_revive"] = True
        logger.info("💉 Fast Revive ON")
    elif cmd == "fast_revive_off":
        features["fast_revive"] = False
        logger.info("💉 Fast Revive OFF")
    elif cmd == "init":
        logger.info("🚀 NEO ENGINE PRO Initialized")
    
    return jsonify({"status": "ok", "features": features})

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    url = f"{PROXY_TARGET}/{path}"
    method = request.method
    headers = dict(request.headers)
    headers.pop('Host', None)
    headers['User-Agent'] = 'NEO-ENGINE-PRO/1.0'
    
    try:
        if method == 'GET':
            resp = requests.get(url, headers=headers, params=request.args, verify=False)
        elif method == 'POST':
            data = request.get_data()
            resp = requests.post(url, data=data, headers=headers, verify=False)
        elif method == 'PUT':
            data = request.get_data()
            resp = requests.put(url, data=data, headers=headers, verify=False)
        elif method == 'DELETE':
            resp = requests.delete(url, headers=headers, verify=False)
        else:
            return jsonify({"error": "Method not supported"}), 405
        
        content_type = resp.headers.get('content-type', '')
        if 'application/json' in content_type:
            try:
                response_data = resp.json()
                response_data = apply_features(response_data)
                return jsonify(response_data), resp.status_code
            except:
                pass
        
        return resp.content, resp.status_code, resp.headers.items()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

def apply_features(data):
    if not isinstance(data, dict):
        return data
    
    if features.get("headshot_90", False):
        if "damage" in data:
            original = data.get("damage", 0)
            if original > 0:
                data["damage"] = int(original * 6)
                data["hit_part"] = "head"
                logger.info(f"🎯 Headshot 90%: {original} → {data['damage']}")
    
    if features.get("headshot_50", False):
        if "damage" in data:
            if random.randint(1, 100) <= 50:
                original = data.get("damage", 0)
                if original > 0:
                    data["damage"] = int(original * 6)
                    data["hit_part"] = "head"
                    logger.info(f"🎯 Headshot 50%: {original} → {data['damage']}")
    
    if features.get("fast_revive", False):
        if "revive_time" in data:
            original = data.get("revive_time", 10)
            data["revive_time"] = int(original / 2)
            logger.info(f"💉 Fast Revive: {original} → {data['revive_time']}")
    
    return data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
