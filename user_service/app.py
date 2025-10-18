from flask import Flask, request, jsonify
import os
import jwt


app = Flask(__name__)
SECRET = os.getenv('JWT_SECRET', 'supersecret123')
ALGO = os.getenv('JWT_ALGORITHM', 'HS256')


# demo user data (id -> profile)
PROFILES = {
1: {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
2: {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
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


@app.route('/profile', methods=['GET'])
def profile():
    payload, err = verify_token_from_header()
    if err:
        return jsonify({'error': err[0]}), err[1]
    user_id = payload.get('sub')
    profile = PROFILES.get(user_id)
    if not profile:
        return jsonify({'error': 'profile not found'}), 404
    return jsonify({'profile': profile})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('USER_PORT', 5001)), debug=True)