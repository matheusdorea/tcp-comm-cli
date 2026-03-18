import socket
import threading


servidor = socket.socket(
socket.AF_INET,
socket.SOCK_STREAM
)

HOST = 'localhost'
PORT = 12345
BUFFERSIZE = 1024

servidor.bind((HOST, PORT))
servidor.listen(5)

lock = threading.Lock()
conexoes_ativas = {}
rodando = True

def broadcast(msg, remetente = None):
    with lock:
        for conn in conexoes_ativas.keys():
            if conn != remetente:
                conn.send(msg.encode())

def handle_cliente(conn: socket.socket, addr):
    try:
        conn.send("Digite o seu nome de usuário".encode())
        user = conn.recv(BUFFERSIZE).decode()
        
        with lock:
            conexoes_ativas[conn] = user
        
        conn.send(f"Seje bevido {conexoes_ativas[conn]}".encode())
            
        while rodando:
            msg = conn.recv(BUFFERSIZE)

            if not msg:
                print(f"Cliente {addr} desconectou")
                break

            broadcast(f"{conexoes_ativas[conn]}: {msg.decode()}", conn)

    except(ConnectionResetError):
        pass
    finally:
        remover_conexao(conn)

def aceitar_conexoes():
    while rodando:
        try:
            print("Servidor Aguardando")
            conn, addr = servidor.accept()

            print(f"Conectado por: {addr}")
            thread_cliente = threading.Thread(target=handle_cliente, args=[conn, addr])
            thread_cliente.daemon = True
            thread_cliente.start()
        except OSError:
            break
        
def remover_conexao(conn):
    if conn in conexoes_ativas:
        user = conexoes_ativas[conn]
        with lock:
            del conexoes_ativas[conn]
        print(f"[SERVIDOR] {user} se desconectou...")
        conn.close()

def admin():
    global rodando
    while rodando:

        comando = input()
        try:
            if comando == "/desligar":
                rodando = False
                print("Fechando conexões e saindo...")
                
                for conn in conexoes_ativas.keys():
                    conn.close()
                    
                servidor.close()
                break
        except(ConnectionAbortedError):
            pass
            
        if comando == "/online":
            with lock: 
                lista = ", ".join(conexoes_ativas.values())
                print(lista)
                
        if comando == "/all":
            msg = input("Mensagem: ")
            broadcast(msg)
        
thread_connect = threading.Thread(target=aceitar_conexoes)
thread_admin = threading.Thread(target=admin)

thread_connect.start()
thread_admin.start()

thread_connect.join()
thread_admin.join()

print("Servidor Encerrado")