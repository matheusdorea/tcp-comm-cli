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

def broadcast():
    pass

def handle_cliente(conn: socket.socket, addr):
    
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

        print(f"Mensagem recebida de {addr}: {msg.decode()}")
        conn.send(msg.upper())

    with lock:
        conexoes_ativas.remove(conn)
    conn.close()

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

def admin():
    global rodando
    while rodando:

        msg = input()
        
        if msg == "/desligar":
            rodando = False
            print("Fechando conexões e saindo...")
            
            for conn in conexoes_ativas.keys():
                print(f"Desconectando {conexoes_ativas[conn]}...")
                conn.close()
                
            servidor.close()
            break
            
        if msg == "/online":
            with lock: 
                lista = ", ".join(conexoes_ativas.values())
                print(lista)
        
thread_connect = threading.Thread(target=aceitar_conexoes)
thread_admin = threading.Thread(target=admin)

thread_connect.start()
thread_admin.start()

thread_connect.join()
thread_admin.join()

print("Servidor Encerrado")