import base64
import os
import ecdsa
import hashlib
import json
from flask import Flask, request, jsonify, render_template, send_file
import qrcode
import io

app = Flask(__name__)
balance = 1000.0
wallet_receive_address = 'TCLJkxGdkxEVXJMk2bynz9Kbrq5e8myzED'  # Replace this with the actual wallet address

def generate_private_key():
    return os.urandom(32)

def private_key_to_public_key(private_key):
    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    return b'\04' + vk.to_string()

def public_key_to_address(public_key):
    sha256_1 = hashlib.sha256(public_key).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_1)
    return ripemd160.hexdigest()

def create_transaction(sender, recipient, amount):
    return {
        'sender': sender,
        'recipient': recipient,
        'amount': amount
    }

def sign_transaction(transaction, private_key):
    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    transaction_bytes = json.dumps(transaction, sort_keys=True).encode()
    return sk.sign(transaction_bytes).hex()

def send_transaction_to_network(transaction, signature):
    # Replace this with actual network interaction code
    print("Sending transaction to the network...")
    print("Transaction:", transaction)
    print("Signature:", signature)
    # Mock response
    return {"status": "success", "transaction_id": "mock_tx_id"}

@app.route('/index')
def index():
    return render_template('index.html', balance=balance)

@app.route('/send_transaction', methods=['GET', 'POST'])
def send_transaction_route():
    global balance
    try:
        data = request.json
        wallet_address = data.get('wallet_address')
        amount = data.get('amount')
        private_key = data.get('private_key')

        if not wallet_address or not amount or not private_key:
            return jsonify({'message': 'All fields are required'}), 400

        # Validate that private_key is a valid hexadecimal string
        try:
            bytes.fromhex(private_key)  # Attempt to convert to bytes
        except ValueError:
            return jsonify({'message': 'Invalid private key format'}), 400

        # Placeholder for private key verification (replace with actual verification logic)
        if private_key != "correct_private_key":
            return jsonify({'message': 'Invalid private key'}), 401

        # Deduct the amount from the current balance
        amount = float(amount)
        if amount > balance:
            return jsonify({'message': 'Insufficient funds'}), 400

        balance -= amount

        # Create and sign the transaction
        public_key = private_key_to_public_key(bytes.fromhex(private_key))
        sender_address = public_key_to_address(public_key)
        transaction = create_transaction(sender_address, wallet_address, amount)
        signature = sign_transaction(transaction, bytes.fromhex(private_key))

        # Process the transaction with the blockchain (placeholder)
        response = send_transaction_to_network(transaction, signature)

        return jsonify({'message': f'Successfully sent {amount} USD to {wallet_address}', 'new_balance': balance, 'transaction_id': response['transaction_id']})
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@app.route('/receive', methods=['GET'])
def receive_transaction():
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(wallet_receive_address)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)

    img_data = buf.getvalue()
    img_base64 = base64.b64encode(img_data).decode('utf-8')

    return render_template('receive.html', wallet_address=wallet_receive_address, qr_code=img_base64)

if __name__ == '__main__':
    app.run(debug=True)














































# from flask import Flask, jsonify, render_template, request, redirect, url_for, send_file
# import qrcode
# import io

# app = Flask(__name__)

# # Initialize a balance
# balance = 1000

# @app.route('/')
# def index():
#     return render_template('index.html', balance=balance)

# @app.route('/send_transaction', methods=['GET', 'POST'])
# def send_transaction():
#     global balance
#     if request.method == 'POST':
#         wallet_address = request.form['wallet_address']
#         amount = request.form['amount']
#         private_key = request.form['private_key']

#         # Placeholder for private key verification (replace with actual verification logic)
#         if private_key != "correct_private_key":
#             return render_template('send_transaction.html', balance=balance, message='Invalid private key')

#         # Deduct the amount from the current balance
#         amount = float(amount)
#         if amount > balance:
#             return render_template('send_transaction.html', balance=balance, message='Insufficient funds')

#         balance -= amount

#         # Process the transaction with the blockchain (placeholder)

#         return render_template('send_transaction.html', balance=balance, message=f'Successfully sent {amount} USD to {wallet_address}')
#     else:
#         return render_template('send_transaction.html', balance=balance)

# @app.route('/receive')
# def receive_transaction():
#     # Generate QR code
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data('wallet-receive-address')  # Replace this with the actual wallet address
#     qr.make(fit=True)

#     img = qr.make_image(fill='black', back_color='white')
#     buf = io.BytesIO()
#     img.save(buf)
#     buf.seek(0)

#     return send_file(buf, mimetype='image/png')

# if __name__ == '__main__':
#     app.run(debug=True)








































# import os
# import ecdsa
# import hashlib
# import json
# import requests

# def generate_private_key():
#     return os.urandom(32)

# def private_key_to_public_key(private_key):
#     sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
#     vk = sk.get_verifying_key()
#     return b'\04' + vk.to_string()

# def public_key_to_address(public_key):
#     sha256_1 = hashlib.sha256(public_key).digest()
#     ripemd160 = hashlib.new('ripemd160')
#     ripemd160.update(sha256_1)
#     return ripemd160.hexdigest()

# def create_transaction(sender, recipient, amount):
#     return {
#         'sender': sender,
#         'recipient': recipient,
#         'amount': amount
#     }

# def sign_transaction(transaction, private_key):
#     sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
#     transaction_bytes = json.dumps(transaction, sort_keys=True).encode()
#     return sk.sign(transaction_bytes).hex()

# def send_transaction(transaction, signature):
#     # Replace this with actual network interaction code
#     print("Sending transaction to the network...")
#     print("Transaction:", transaction)
#     print("Signature:", signature)
#     # Mock response
#     return {"status": "success", "transaction_id": "mock_tx_id"}

# private_key = generate_private_key()
# public_key = private_key_to_public_key(private_key)
# address = public_key_to_address(public_key)

# print("Private Key:", private_key.hex())
# print("Public Key:", public_key.hex())
# print("Address:", address)

# transaction = create_transaction(address, 'recipient_address_here', 10)
# signature = sign_transaction(transaction, private_key)

# response = send_transaction(transaction, signature)
# print("Response:", response)
