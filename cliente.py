import socket
import threading

# 1. Cria socket TCP
cliente = socket.socket(
socket.AF_INET,
socket.SOCK_STREAM
)

HOST = 'localhost'
PORT = 12345
BUFFERSIZE = 1024

# 2. Conecta ao servidor
cliente.connect((HOST, PORT))

def enviar_mensagem():
    cliente.recv(BUFFERSIZE)
    msg = input("Apelido: ")
    cliente.send(msg.encode())
    print(cliente.recv(BUFFERSIZE))

    while True:
        msg = input("Você: ")

        if msg == "/sair":
            break

        cliente.send(msg.encode())

        resposta = cliente.recv(BUFFERSIZE)
        print(f"Resposta: {resposta.decode()}")
        
    cliente.close()

def receber_mensagem():
    print(cliente.recv(BUFFERSIZE))

thread_escutando = threading.Thread(target=receber_mensagem)
thread_enviar = threading.Thread(target=enviar_mensagem)

thread_escutando.start()
thread_enviar.start()