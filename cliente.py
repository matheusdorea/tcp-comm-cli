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
rodando = True
lock = threading.Lock()

# 2. Conecta ao servidor
cliente.connect((HOST, PORT))

def iniciar_cliente():
    cliente.recv(BUFFERSIZE)
    msg = input("Apelido: ")
    cliente.send(msg.encode())
    print(cliente.recv(BUFFERSIZE))
    
def enviar_mensagens():
    global rodando
    while rodando:
        msg = input("Você: ")

        if msg == "/logout":
            with lock:
                rodando = False
            break

        cliente.send(msg.encode())
        
    cliente.close()
    
def receber_mensagens():
    global rodando
    while rodando:
        print(cliente.recv(BUFFERSIZE).decode())


iniciar_cliente()

thread_enviar = threading.Thread(target=enviar_mensagens)
thread_receber = threading.Thread(target=receber_mensagens)

thread_enviar.start()
thread_receber.start()

thread_enviar.join()
thread_receber.join()

print("Cliente encerrado...")