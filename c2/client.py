import socket
import threading
from Blockchain import Blockchain
BlockchainData = Blockchain()

def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(message)
            try:
                msg = message.lower()
                #return balance or balance is right
                if msg.startswith('!balance') and len(msg.split(' ')) == 2:
                    walletAddress = message.split(' ')[1]
                    balance = BlockchainData.AccountBalance(walletAddress)
                    print(balance)
                    client_socket.send(f'!balanceResponce {balance}'.encode('utf-8'))
                    #print(walletAddress)
                #create transaction from x to y and add it to the ledger
                elif msg.startswith('!transaction') and len(msg.split(' ')) == 4:
                    splittedMessage = message.split(' ')
                    From = splittedMessage[1]
                    To = splittedMessage[2]
                    Ammount = splittedMessage[3]
                    responce = BlockchainData.CreateBlock(From, To, float(Ammount))
                    print(responce)
                    print(BlockchainData.ShowBlockchain())
                    client_socket.send(f'!transactionResponce {responce}'.encode('utf-8'))
                elif msg.startswith('!init') and len(msg.split(' ')) == 4:
                    print(f'in')
                    splittedMessage = message.split(' ')
                    From = splittedMessage[1]
                    To = splittedMessage[2]
                    Ammount = splittedMessage[3]
                    if From == '-1' and To == '-1' and Ammount == '-1':
                        print('BLOCKCHAIN LOADED SUSSESSFULLY')
                    else:
                        responce = BlockchainData.CreateBlock(From, To, float(Ammount))
                    
            except Exception:
                pass
        except socket.error:
            break

def main():
    server_host = '127.0.0.1'
    server_port = 8888

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    while True:
        pass
        message = input("You: ")
        # Allow the user to exit the chat
        if message.lower() == 'exit':
            break
        elif message.lower() == 'bc':
            print(BlockchainData.ShowBlockchain())

    # Close the client socket
    client_socket.close()

if __name__ == "__main__":
    main()
