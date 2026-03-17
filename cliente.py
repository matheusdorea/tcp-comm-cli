import socket

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