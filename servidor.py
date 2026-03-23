import socket
import threading
import curses


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
em_conversa = set()
conversas = {}

painel_logs = None

def log(msg):
    with lock:
        if painel_logs:
            painel_logs.addstr(f"{msg}\n")
            painel_logs.refresh()

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
            msg = conn.recv(BUFFERSIZE).decode()

            if not msg:
                log(f"Cliente {addr} desconectou")
                break

            if msg == "/online":
                with lock: 
                    lista = "\n".join(conexoes_ativas.values())
                conn.send(f"Lista de usuários online: \n{lista}".encode())
                continue

            if msg.startswith("/connect "):
                nome = msg[9:]
                destino = next(k for k, v in conexoes_ativas.items() if v == nome)
                conversas[conn] = destino
                em_conversa.add(conn)
                continue

            broadcast(f"{conexoes_ativas[conn]}: {msg}", conn)

    except Exception as e:
        log(f"Erro com {addr}: {type(e).__name__}: {e}")
    finally:
        remover_conexao(conn)

def aceitar_conexoes():
    while rodando:
        try:
            log("Servidor Aguardando")
            conn, addr = servidor.accept()

            log(f"Conectado por: {addr}")
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
        log(f"[SERVIDOR] {user} se desconectou...")
        conn.close()
            
def main(stdscr = curses.initscr()):
    global rodando, painel_logs
    
    curses.curs_set(1)
    stdscr.clear()
    
    altura, largura = stdscr.getmaxyx()
    
    painel_logs = curses.newwin(altura - 2, largura, 0, 0)
    painel_logs.scrollok(True)
    painel_logs.addstr("=== Servidor iniciado ===\n")
    painel_logs.addstr("Comandos: /online | /all <msg> | /desligar\n\n")
    painel_logs.refresh()

    # Separador
    separador = curses.newwin(1, largura, altura - 2, 0)
    separador.addstr(0, 0, "─" * (largura - 1))
    separador.refresh()
    
    painel_input = curses.newwin(1, largura, altura - 1, 0)
    
    thread_connect = threading.Thread(target=aceitar_conexoes)
    thread_connect.start()
            
    while rodando:
        try:
            painel_input.clear()
            painel_input.addstr("Admin: ")
            painel_input.refresh()
            
            curses.echo()
            try:
                comando = painel_input.getstr().decode()
            except:
                continue
            curses.noecho()
            
            if comando == "/desligar":
                rodando = False
                log("Fechando conexões e saindo...")
                
                for conn in conexoes_ativas.keys():
                    try:
                        conn.close()
                    except (ConnectionAbortedError):
                        log(f"Conexão abortada com {conexoes_ativas[conn]}")
                    
                servidor.close()
                break
                
            if comando == "/online":
                with lock: 
                    lista = "\n".join(conexoes_ativas.values())
                log(lista)
                    
            if comando.startswith("/all "):
                msg = comando[5:]
                broadcast(f"[Servidor]: {msg}")

            painel_logs.addstr(f"Admin: {comando}\n")
            painel_logs.refresh()
            
        except(ConnectionAbortedError):
            pass
            
    

curses.wrapper(main)

print("Servidor Encerrado")