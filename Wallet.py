from flask import Flask, request, jsonify
from pymongo import MongoClient
import pyqrcode
import base64
import png
from solders.keypair import Keypair
from solders.message import MessageV0
from solders.instruction import Instruction
from solders.hash import Hash
from solders.transaction import VersionedTransaction
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solana.rpc.async_api import AsyncClient
from datetime import datetime
import asyncio

app = Flask(__name__, static_folder='static')
client = MongoClient('mongodb://localhost:27017/')
db = client['Wallet_db']
transactions_collection = db['Previous_Transactions']
solana_client = AsyncClient("https://api.devnet.solana.com")

@app.route('/generate_wallet', methods=['GET'])
def generate_wallet():
    secret_key = bytes([
        174, 47, 154, 16, 202, 193, 206, 113,
        199, 190, 53, 133, 169, 175, 31, 56,
        222, 53, 138, 189, 224, 216, 117, 173,
        10, 149, 53, 45, 73, 251, 237, 246,
        15, 185, 186, 82, 177, 240, 148, 69,
        241, 227, 167, 80, 141, 89, 240, 121,
        121, 35, 172, 247, 68, 251, 226, 218,
        48, 63, 176, 109, 168, 89, 238, 135,
    ])

    keypair = Keypair.from_bytes(secret_key)
    print(f"Created Keypair with public key: {keypair.pubkey()}")

    b58_string = "5MaiiCavjCmn9Hs1o3eznqDEhRwxo7pXiAYez7keQUviUkauRiTMD8DrESdrNjN8zd9mTmVhRvBJeg5vhyvgrAhG"
    keypair_b58 = Keypair.from_base58_string(b58_string)
    print(f"Created Keypair with public key: {keypair_b58.pubkey()}")

    public_key = Pubkey.from_string("24PNhTaNtomHhoy3fTRaMhAFCRj4uHqhZEEoWrKDbR5p")

    assert str(keypair.pubkey()) == str(public_key), "Public keys do not match"
    
    # Save the keypair to the database
    transactions_collection.insert_one({
        'public_key': str(public_key),
        'secret_key': base64.b64encode(secret_key).decode('utf-8'),
        'timestamp': datetime.utcnow()
    })

    # Generate QR code
    qr = pyqrcode.create(str(public_key))
    qr_code_path = f'static/{public_key}.png'
    qr.png(qr_code_path, scale=6)

    return jsonify({'public_key': str(public_key), 'qr_code': qr_code_path, 'secret_key': base64.b64encode(secret_key).decode('utf-8')})


@app.route('/send', methods=['POST'])
async def send():
    data = request.get_json()
    sender_secret_key_b64 = data.get('sender')

    # Fix base64 padding
    missing_padding = len(sender_secret_key_b64) % 4
    if missing_padding:
        sender_secret_key_b64 += '=' * (4 - missing_padding)

    try:
        sender_secret_key = base64.b64decode(sender_secret_key_b64)
    except Exception as e:
        return jsonify({'error': f'Failed to decode base64: {str(e)}'}), 400

    if len(sender_secret_key) != 64:
        return jsonify({'error': 'Invalid secret key length', 'decoded_length': len(sender_secret_key)}), 400

    try:
        sender_keypair = Keypair.from_bytes(sender_secret_key)
    except Exception as e:
        return jsonify({'error': f'Failed to create Keypair: {str(e)}'}), 400

    receiver_pubkey = Pubkey.from_string(data['receiver'])
    lamports = int(data['lamports'])

    # Get the latest blockhash
    response = await solana_client.get_latest_blockhash()
    blockhash = Hash.from_string(response.value.blockhash)

    # Create transfer instruction
    ix = transfer(
        TransferParams(
            from_pubkey=sender_keypair.pubkey(),
            to_pubkey=receiver_pubkey,
            lamports=lamports
        )
    )

    # Compile the message
    msg = MessageV0.try_compile(
        payer=sender_keypair.pubkey(),
        instructions=[ix],
        address_lookup_table_accounts=[],
        recent_blockhash=blockhash,
    )

    # Create and sign the transaction
    tx = VersionedTransaction(msg, [sender_keypair])
    tx.sign([sender_keypair])

    # Send the transaction
    raw_tx = tx.serialize()
    response = await solana_client.send_raw_transaction(raw_tx)

    # Save the transaction details to the database
    transactions_collection.insert_one({
        'sender': str(sender_keypair.pubkey()),
        'receiver': str(receiver_pubkey),
        'lamports': lamports,
        'signature': response.result,
        'timestamp': datetime.utcnow()
    })

    return jsonify({'signature': response.result})


@app.route('/balance', methods=['GET'])
async def balance():
    public_key = request.args.get('public_key')
    pubkey = Pubkey.from_string(public_key)
    response = await solana_client.get_balance(pubkey)
    balance = response['result']['value'] / 1e9  # converting lamports to SOL

    return jsonify({'public_key': public_key, 'balance': balance})

if __name__ == '__main__':
    asyncio.run(app.run(debug=True))
