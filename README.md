# Block-Chain Wallet
# OverView of Blockchain Wallet Application:
The Blockchain Wallet Application is a web-based platform designed to facilitate secure and convenient interactions with Solana cryptocurrency wallets. Built with Flask for the backend, MongoDB for data storage, and various libraries for blockchain interactions, this application offers users a seamless experience in managing their digital assets on the Solana blockchain. The key features of the application include wallet generation, transaction processing, balance checking, and QR code generation.

# KeyFeatures: 
## Generate Wallet
    1- Allows users to generate a new Solana cryptocurrency wallet.
    2- Creates a keypair with a public and secret key.
    3- Saves the public key, secret key (base64 encoded), and timestamp of creation in MongoDB.
    4- Generates a QR code for easy scanning of the public key.
    
 ## Send Transaction
    1- Facilitates sending cryptocurrency transactions on the Solana blockchain.
    2- Validates and decodes the sender's base64 encoded secret key.
    3- Constructs a transfer instruction specifying the sender, receiver, and amount (lamports).
    4- Signs the transaction using the sender's keypair.
    5- Sends the signed transaction to the Solana blockchain using asynchronous API calls.
    6- Logs transaction details including sender, receiver, lamports, signature, and timestamp in MongoDB.
    
## Check Balance

    1- Retrieves the current balance of a specified Solana wallet (public key).
    2- Converts the balance from lamports to SOL (Solana's cryptocurrency unit).
    3- Displays the wallet's public key and its corresponding balance.
    4- QR Code Generation

Generates QR codes for Solana wallet public keys.
QR codes are saved as PNG images in the 'static' folder for easy sharing and scanning.
These features collectively allow users to create Solana wallets, send transactions securely, check wallet balances, and utilize QR codes for convenient wallet address handling.
