from flask import Flask, request, jsonify
import os
import jwt


app = Flask(__name__)
SECRET = os.getenv('JWT_SECRET', 'supersecret123')
ALGO = os.getenv('JWT_ALGORITHM', 'HS256')


PRODUCTS = {
1: {'id': 1, 'name': 'Keyboard', 'price': 250000},
2: {'id': 2, 'name': 'Mouse', 'price': 150000}
}


def verify_token_from_header():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None, ('Missing or invalid Authorization header', 401)
    token = auth.split(' ', 1)[1]
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, ('Token expired', 401)
    except Exception:
        return None, ('Token invalid', 401)


@app.route('/products', methods=['GET'])
def products():
    payload, err = verify_token_from_header()
    if err:
        return jsonify({'error': err[0]}), err[1]
    return jsonify({'products': list(PRODUCTS.values())})


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    payload, err = verify_token_from_header()
    if err:
        return jsonify({'error': err[0]}), err[1]
    p = PRODUCTS.get(product_id)
    if not p:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'product': p})

@app.route('/products', methods=['POST'])
def add_product():
    payload, err = verify_token_from_header()
    if err:
        return jsonify({'error': err[0]}), err[1]

    data = request.get_json() or {}
    name = data.get('name')
    price = data.get('price')

    if not name or not price:
        return jsonify({'error': 'Name and price required'}), 400

    new_id = max(PRODUCTS.keys()) + 1 if PRODUCTS else 1
    PRODUCTS[new_id] = {'id': new_id, 'name': name, 'price': price}
    return jsonify({'message': 'Product added', 'product': PRODUCTS[new_id]}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PRODUCT_PORT', 5002)), debug=True)