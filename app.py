import json
import os
import random
import re
import string

import redis
from flask import Flask, request, redirect, abort, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
r = redis.Redis(host=os.getenv('REDIS_HOST', 'redis'), port=os.getenv('REDIS_PORT', 6379), decode_responses=True)
invalid_chars = ['_', '/', '\\', '?']


def documentation(code=400):
    try:
        with open('sample.http', 'r') as file:
            content = file.read()
        return content, code, {'Content-Type': 'text/plain'}
    except FileNotFoundError:
        return "sample.http file not found", 404


def generate_random_keys(length=5):
    while True:
        new_key = ''.join(random.choices(string.ascii_letters + string.digits, k=length))

        if not r.exists(new_key):
            return new_key
        else:
            collision_key = "randomkey_generate_collision_count"
            collision_count = r.incr(collision_key)

            if collision_count == 1:
                r.expire(collision_key, 60 * 60 * 24)


def get_key(key):
    return jsonify({"key": key, "data": r.hgetall(key), "ttl": r.ttl(key)})

def sanitize_key(key):
    if not re.match(r'^[a-zA-Z0-9\-]+$', key):
        raise ValueError("Invalid key format.")
    return key

@app.route('/<key>')
def shortlink(key):
    try:
        key = sanitize_key(key)
    except ValueError as e:
        return documentation(code=400)

    data = get_key(key)

    if not data or not isinstance(data.json, dict):
        return documentation(code=404)

    target = data.json.get('data', {}).get('target')
    if target:
        return redirect(target, code=302)
    else:
        return abort(404)


@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent', '').lower()
    common_browsers = ['chrome', 'firefox', 'safari', 'edge', 'opera', 'vivaldi', 'brave', 'internet explorer',
                       'uc browser', 'yandex']
    redirect_url = os.getenv('INDEX_REDIRECT_URL')

    if any(browser in user_agent for browser in common_browsers) and redirect_url:
        return redirect(redirect_url)
    else:
        return documentation(code=200)


@app.route('/_set', methods=['GET', 'POST', 'DELETE'])
def set_shortlink():
    try:
        key = sanitize_key(request.json.get('key'))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    target = request.json.get('target')
    password = request.json.get('password')

    max_valid_time = os.getenv('MAX_VALID_TIME', None)
    max_valid_time = int(max_valid_time) if max_valid_time is not None else None
    valid_time = request.json.get('valid_time', max_valid_time if max_valid_time is not None else 60 * 60 * 24)

    if max_valid_time is not None and valid_time > max_valid_time:
        return jsonify({
            "error": f"The server sets a maximum number of seconds: {max_valid_time}"}
        ), 400

    if request.method == 'GET':
        if r.exists(key) and key is not None:
            return get_key(key)
        elif key is None:
            return documentation(code=400)
        else:
            abort(404)
    elif request.method == 'POST' and target is not None:
        if key is not None and any(char in key for char in invalid_chars):
            return jsonify({"error": "Key cannot contain '_', '/', '\\', '?'."}), 400
        key = key if key is not None else generate_random_keys()
        if not r.exists(key):
            r.hset(key, mapping={'target': target, 'password': password})
            r.expire(key, valid_time)
            return get_key(key), 201
        else:
            return jsonify({"error": "This shortlink already exists. Please delete before creating."}), 409
    elif request.method == 'DELETE':
        if r.exists(key) and key is not None:
            stored_password = r.hget(key, 'password')
            if stored_password is not None:
                input_password = request.json.get('password', None)
                if input_password != stored_password:
                    return jsonify({"error": "Password is incorrect."}), 403
            if r.delete(key):
                return f"Shortlink {key} deleted", 200
            else:
                return f"Failed to delete shortlink {key}.", 404
        else:
            return documentation(code=400)
    else:
        return documentation(), 403


@app.route('/_list', methods=['GET'])
def list_shortlinks():
    per_page = request.args.get('per_page', 100, type=int)
    per_page = min(per_page, 512)  # Limit per_page to a maximum of 512
    page = request.args.get('page', 1, type=int)

    start = (page - 1) * per_page
    end = start + per_page

    all_keys = r.keys('*')
    total_keys = len(all_keys)

    paginated_keys = all_keys[start:end]

    shortlinks = {key: {k: v for k, v in get_key(key).json.items() if k != 'password'} for key in paginated_keys}

    return {
        'shortlinks': shortlinks,
        'total': total_keys,
        'page': page,
        'per_page': per_page,
        'pages': (total_keys + per_page - 1) // per_page  # Total number of pages
    }


if __name__ == '__main__':
    app.run()
