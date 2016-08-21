#coding=utf-8
import socket
import io
import sys
import protocol
from threading import Thread
from time import sleep

class ChatServer(socket.socket):  # ChatServer繼承socket類別
    def __init__(self, host, port): # ChatServer建構子
        super().__init__() # 使用socket的建構子
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("###### Socket created ######\n\n")
        try:
            self.sock.bind((host, port)) # 將server綁定在host:port格式下
        except socket.error:
            print("### Server binding fail ###\n")
            sys.exit(0)
        self.sock.listen(5) # 允許最多同時5個user連到server
        print(" ### Server socket is listening... ###\n")
        self.users = {} # 初始化,現在沒有使用者連到server

    def handle_accept(self):
        while True:
            """ server進到waiting狀態等待client端的連線
                如果有使用者連到server,則透過accept()傳回有關client的資訊"""
            conn, addr = self.sock.accept()
            servThread = Thread(target=self.handle_single_connect, args=((conn, addr))) # 產生thread來接收訊息
            servThread.start()

    def handle_single_connect(self, conn, addr):
        username = conn.recv(RECV_BUFFER).decode() # python 3必須使用decode(),因為string和unicode為不同型別資料
        print("### New coonection from %s(%s:%s) ###\n" % (username, addr[0], addr[1]))
        self.users[username] = conn # 儲存client端資訊
        msg = username + u" 進入chatting room.\n"
        package = protocol.generateRequest(HOST, PORT, 'SYST', 'Admin', msg)
        self.broadcast(username, package)

        while True:
            package = conn.recv(RECV_BUFFER).decode()
            if not package:
                continue
            req = protocol.handleRequest(package)
            print(req.get_type())
            if req.get_type() == 'SEND': # 接收client端傳來聊天訊息
                self.broadcast(username, package)
            elif req.get_type() == 'EXIT': # 收到使用者離開chatting room訊息
                self.users.pop(req.get_name())
                print("### Connection with %s(%s:%s) ended. ###\n" % (username, addr[0], addr[1]))
                msg = username + u" 離開chatting room.\n"
                package = protocol.generateRequest(HOST, PORT, 'SYST', 'Admin', msg)
                self.broadcast(username, package)
        
    def broadcast(self, username, content):
        for name, conn in self.users.items():
            conn.sendall(content.encode())
        


if __name__ == "__main__":
    RECV_BUFFER = 4096
    HOST = 'localhost'
    PORT = 6666
    server = ChatServer(HOST, PORT)
    try:
        server.handle_accept()
    except Exception as e:
        print("error 1: %s", e)
    finally:
        server.close()






