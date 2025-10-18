from flask import Flask, request, jsonify
import os
import jwt
import requests


app = Flask(__name__)
SECRET = os.getenv('JWT_SECRET', 'supersecret123')
ALGO = os.getenv('JWT_ALGORITHM', 'HS256')
USER_SERVICE = os.getenv('USER_SERVICE_URL', 'http://localhost:5001')
PRODUCT_SERVICE = os.getenv('PRODUCT_SERVICE_URL', 'http://localhost:5002')


ORDERS = []
NEXT_ID = 1


def verify_token_from_header():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
            return None, ('Missing or invalid Authorization header', 401)
    token = auth.split(' ', 1)[1]
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        return token, payload, None
    except jwt.ExpiredSignatureError:
        return None, None, ('Token expired', 401)
    except Exception:
        return None, None, ('Token invalid', 401)


@app.route('/orders', methods=['POST'])
def create_order():
    global NEXT_ID
    token, payload, err = verify_token_from_header()
    if err:
        return jsonify({'error': err[0]}), err[1]
    user_id = payload.get('sub')
    data = request.json or {}
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'error': 'product_id required'}), 400
    # validate product by calling product service
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f'{PRODUCT_SERVICE}/products/{product_id}', headers=headers)
    if r.status_code != 200:
        return jsonify({'error': 'product not found or unauthorized', 'detail': r.text}), 400
    product = r.json().get('product')
    # optional: get user profile
    r2 = requests.get(f'{USER_SERVICE}/profile', headers=headers)
    if r2.status_code != 200:
        return jsonify({'error': 'user profile not found or unauthorized', 'detail': r2.text}), 400
    order = {'id': NEXT_ID, 'user_id': user_id, 'product': product}
    ORDERS.append(order)
    NEXT_ID += 1
    return jsonify({'order': order}), 201


@app.route('/orders', methods=['GET'])
def list_orders():
    token, payload, err = verify_token_from_header()
    if err:
        return jsonify({'error': err[0]}), err[1]
    # for demo return all
    return jsonify({'orders': ORDERS})
app.run(host='0.0.0.0', port=int(os.getenv('ORDER_PORT', 5003)), debug=True)