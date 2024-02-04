import socket
import threading
from Blockchain import Blockchain
from time import sleep
from flask import Flask, render_template, Response, request, redirect, session, url_for
import os
from db import *
import random


responceData = {'True':0, 'False':0}
responces = 0
lastMessage = ''
BlockchainData = Blockchain()
database = 'data.db'
clients = []

app = Flask(__name__)
app.secret_key = '123456789AZERTYUIOP'

def generate_passphrase(num_words=4, wordlist_file="wordlist.txt"):
    with open(wordlist_file, "r") as file:
        wordlist = [line.strip()[line.strip().index('\t')+1:] for line in file]

    passphrase = " ".join(random.sample(wordlist, num_words))
    return passphrase

def broadCastMessage(message, clients):
    for c in clients:
        try:
            c.send(message.encode('utf-8'))
        except socket.error:
            print(f"Error sending message to {c.getpeername()}")

def handle_client(client_socket, address, clients):
    global responceData, responces
    print(f"Accepted connection from {address}")

    # Broadcast a welcome message to the connected client
    welcome_message = "Welcome to the chat! Type 'exit' to leave."
    client_socket.send(welcome_message.encode('utf-8'))
    sleep(1)

    bc = BlockchainData.ShowBlockchain()
    if len(bc) > 1:
        for block in bc[1:]:
            TransactionData = block['TransactionData']
            From = TransactionData['From']
            To = TransactionData['To']
            Ammount = TransactionData['Ammount']
            msg = f'!init {From} {To} {Ammount}'
            client_socket.send(msg.encode('utf-8'))
            sleep(1)
        msg = f'!init -1 -1 -1'
        client_socket.send(msg.encode('utf-8'))
    else:
        msg = f'!init -1 -1 -1'
        client_socket.send(msg.encode('utf-8'))

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            broadcast_message = f"User {address}: {message}"
            print(broadcast_message)
            if message.startswith('!balanceResponce') and len(message.split(' ')) == 2:
                balance = message.split(' ')[1]
                print(float(balance))
            elif message.startswith('!transactionResponce') and len(message.split(' ')) == 2:
                responce = message.split(' ')[1]
                responceData[responce] += 1
                responces += 1

        except socket.error:
            break

    print(f"Connection from {address} closed.")
    client_socket.close()
    clients.remove(client_socket)

def handleClients(server_socket, clients):
    while True:
        client_socket, address = server_socket.accept()
        clients.append(client_socket)

        # Start a new thread to handle the client
        client_handler = threading.Thread(target=handle_client, args=(client_socket, address, clients))
        client_handler.daemon = True
        client_handler.start()

def handleResponcesCount():
    global responceData, responces, lastMessage, clients
    while True:
        #sleep(1)
        if responces == len(clients) and len(lastMessage) > 0:
            if responceData['True'] >= responceData['False']:
                try:
                    splittedMessage = lastMessage.split(' ')
                    From = splittedMessage[1]
                    To = splittedMessage[2]
                    Ammount = splittedMessage[3]
                    BlockchainData.CreateBlock(From, To, float(Ammount))
                    responceData = {'True':0, 'False':0}
                    responces = 0
                    lastMessage = ''
                except Exception as e:
                    print(e)
                    pass

def webserver():
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if 'id' not in list(session.keys()):
            return render_template('./index.html', loggedIn=False, balance=0)
        else:
            balance = BlockchainData.AccountBalance(session['id'])
            return render_template('./index.html', loggedIn=True, balance=balance)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'id' not in list(session.keys()):
            if request.method == 'POST':
                usernameORemail = request.form.get('usernameORemail')
                passphrase = request.form.get('passphrase')
                userExist = check_user_exists(database, usernameORemail, passphrase)
                if userExist is not None:
                    publicKey = userExist[5]
                    session['id'] = publicKey
                    return redirect(url_for('index'))
                else:
                    return render_template('./signIn.html', usernameORemail=usernameORemail, passphrase=passphrase, erreur="user Not Exist", loggedIn=False, balance=0)
            return render_template('./signIn.html', loggedIn=False, balance=0)
        else:
            return redirect(url_for('index'))
        

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        #zidou flous fel signup
        if 'id' not in list(session.keys()):
            if request.method == 'POST':
                fullName = request.form.get('fullName')
                username = request.form.get('username')
                email = request.form.get('email')
                passphrase = generate_passphrase(12)
                if check_username_exists(database, username) is None and check_email_exists(database, email) is None:
                    if check_passphrase_exists(database, passphrase) is None:
                        publicKey = insert_user(database, fullName, username, email, passphrase)
                        #lastMessage = f'!transaction ZEROCRUCH {publicKey} 100'
                        #broadCastMessage(lastMessage, clients)
                        session['id'] = publicKey
                        return render_template('./verification.html', passphrase=passphrase, loggedIn=True, balance=0)
                    else:
                        while True:
                            passphrase = generate_passphrase(12)
                            if check_passphrase_exists(database, passphrase) is None:
                                publicKey = insert_user(database, fullName, username, email, passphrase)
                                #lastMessage = f'!transaction ZEROCRUCH {publicKey} 100'
                                #broadCastMessage(lastMessage, clients)
                                session['id'] = publicKey
                                return render_template('./verification.html', passphrase=passphrase, loggedIn=True, balance=0)
                else:
                    return render_template('./register.html', fullName=fullName, username=username, email=email, erreur="user Already Exist", loggedIn=False, balance=0)
                #bc = BlockchainData.ShowBlockchain()
            return render_template('./register.html', loggedIn=False, balance=0)
        else:
            return redirect(url_for('index'))
    
    @app.route('/transaction', methods=['GET', 'POST'])
    def transaction():
        global lastMessage
        if 'id' not in list(session.keys()):
            return redirect(url_for('login'))
        else:
            balance = BlockchainData.AccountBalance(session['id'])
            if request.method == 'POST':
                From = session['id']
                To = request.form.get('To')
                if From == To:
                    return render_template('./donate.html', responce=f"Transaction Declined By The Blockchain, You Can't Send To Your Self", color="red", loggedIn=True, balance=balance, wallet=session['id'])
                Ammount = request.form.get('flexRadioDefault')
                try:
                    if To is not None or To != 'None':
                        accBal = BlockchainData.AccountBalance(From)
                        if accBal >= float(Ammount):
                            lastMessage = f'!transaction {From} {To} {float(Ammount)}'
                            broadCastMessage(lastMessage, clients)
                            return render_template('./donate.html', responce="The Transaction Is Beeing Processing By The Blockchain", color="green", loggedIn=True, balance=balance, wallet=session['id'])
                        else:
                            return render_template('./donate.html', responce=f"Transaction Declined By The Blockchain, Current Account Balance : {accBal}TND", color="red", loggedIn=True, balance=balance, wallet=session['id'])
                    else:
                        return render_template('./donate.html', responce=f"Please Enter The Recepient Wallet Address", color="red", loggedIn=True, balance=balance, wallet=session['id'])
                except Exception:
                    return render_template('./donate.html', responce=f"Please Enter The Ammount To Donnate", color="red", loggedIn=True, balance=balance, wallet=session['id'])
            return render_template('./donate.html', loggedIn=True, balance=balance, wallet=session['id'])
    
    @app.route('/buy', methods=['GET', 'POST'])
    def buy():
        global lastMessage
        if 'id' not in list(session.keys()):
            return redirect(url_for('login'))
        else:
            balance = BlockchainData.AccountBalance(session['id'])
            if request.method == 'POST':
                try:
                    Ammount = request.form.get('flexRadioDefault')
                    From = 'ZEROCRUCH'
                    To = session['id']
                    accBal = BlockchainData.AccountBalance(From)
                    if accBal >= float(Ammount):
                        lastMessage = f'!transaction {From} {To} {float(Ammount)}'
                        broadCastMessage(lastMessage, clients)
                        return render_template('./buy.html', responce="The Transaction Is Beeing Processing By The Blockchain", color="green", loggedIn=True, balance=balance, wallet=session['id'])
                    else:
                        return render_template('./buy.html', responce=f"Transaction Declined By The Blockchain, Current Account Balance : {accBal}TND", color="red", loggedIn=True, balance=balance, wallet=session['id'])
                except Exception:
                    return render_template('./buy.html', responce=f"Please Enter The Ammount To Buy", color="red", loggedIn=True, balance=balance)
            return render_template('./buy.html', loggedIn=True, balance=balance, wallet=session['id'])
    
    @app.route('/transactions', methods=['GET', 'POST'])
    def transactions():
        bc = BlockchainData.ShowBlockchain()
        if 'id' not in list(session.keys()):
            return render_template('./transaction-history.html', bc=bc, loggedIn=False, balance=0)
        else:
            balance = BlockchainData.AccountBalance(session['id'])
            return render_template('./transaction-history.html', bc=bc, loggedIn=True, balance=balance, wallet=session['id'])
        
    
    
    @app.route('/logout')
    def logout():
        session.pop('id', None)
        return redirect(url_for('index'))
    app.run(host='0.0.0.0', port=5000)


def main():
    global lastMessage, clients
    server_host = '127.0.0.1'
    server_port = 8888

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_host, server_port))
    server_socket.listen(5)

    print(f"Server listening on {server_host}:{server_port}")

    

    clients_handler = threading.Thread(target=handleClients, args=(server_socket, clients))
    clients_handler.daemon = True
    clients_handler.start()

    checkHandler = threading.Thread(target=handleResponcesCount)
    checkHandler.daemon = True
    checkHandler.start()

    webS = threading.Thread(target=webserver)
    webS.daemon = True
    webS.start()
    sleep(10)
    lastMessage = '!transaction ZEROCRUCH 4e3a13937f5b6118f1e16aa8ce9b1a0630b40dd691b9e2f3662d52dbff6c68a1 100'
    broadCastMessage(lastMessage, clients)
    while True:
        pass
        """message = input('YOU : ')
        broadCastMessage(message, clients)
        lastMessage = message"""
    

if __name__ == "__main__":
    if not os.path.exists(database):
        createDatabase(database)
    main()
    