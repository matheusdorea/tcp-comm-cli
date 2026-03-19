import socket
import threading
import curses

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

def main(stdscr = curses.initscr()):
    global rodando
    
    curses.curs_set(1)
    stdscr.clear()
    
    altura, largura = stdscr.getmaxyx()
    
    painel_msgs = curses.newwin(altura - 2, largura, 0, 0)
    painel_msgs.scrollok(True)
    
    separador = curses.newwin(1, largura, altura-2, 0)
    separador.addstr(0, 0, "-" * (largura - 1))
    separador.refresh()
    
    painel_input = curses.newwin(1, largura, altura - 1, 0)
    
    def adicionar_mensagem(msg):
        with lock:
            painel_msgs.addstr(f"{msg}\n")
            painel_msgs.refresh()

            
    prompt = cliente.recv(BUFFERSIZE).decode()
    adicionar_mensagem(prompt)
    
    #iniciando cliente
    painel_input.clear()
    painel_input.addstr("Apelido: ")
    painel_input.refresh()
    curses.echo()
    apelido = painel_input.getstr().decode()
    curses.noecho()
    cliente.send(apelido.encode())
    
    boas_vindas = cliente.recv(BUFFERSIZE).decode()
    adicionar_mensagem(boas_vindas)
    
    def receber_mensagens():
        global rodando
        while rodando:
            try:
                msg = cliente.recv(BUFFERSIZE).decode()
                if msg:
                    adicionar_mensagem(msg)
            except:
                break
            
    thread_receber = threading.Thread(target=receber_mensagens)
    thread_receber.start()
    
    while rodando:
        painel_input.clear()
        painel_input.addstr("Você: ")
        painel_input.refresh()
        
        curses.echo()
        try:
            msg = painel_input.getstr().decode()
        except:
            pass
        curses.noecho()
        
        if msg == "/sair":
            with lock:
                rodando = False
            break
        
        cliente.send(msg.encode())
        painel_msgs.addstr(f"Você ({apelido}): {msg}\n")
        painel_msgs.refresh()
        
    cliente.close()
                
curses.wrapper(main)

print("Cliente encerrado...")