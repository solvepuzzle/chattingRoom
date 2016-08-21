#coding=utf-8
import socket
import io
import sys
import tkinter
import protocol
from threading import Thread
from time import sleep



# Chatting Room 視窗
class ChatFrame(tkinter.Frame):
    def __init__(self, master=None): # 建構子
        tkinter.Frame.__init__(self, master)
        self.publicText = tkinter.Text(self, width=60, height=20)
        self.inputText = tkinter.Text(self, width=40, height=5)
        self.sendButton = tkinter.Button(self, text='send', command=self.__send)
        self.clearButton = tkinter.Button(self, text='clear', command=self.__clear)
        self.exitButton = tkinter.Button(self, text='exit', command=self.__exit)
        self.__create_widgets()
        self.grid() # 產生聊天室窗, 輸入文字介面以及button等
        cliThread = Thread(target = self.__receive_message, args=())
        cliThread.start() # 產生thread來接收訊息
        client.sendall(client.username)

    def __create_widgets(self):
        self.publicText.grid(column=0, row=0, columnspan=3)
        self.inputText.grid(column=0, row=1, columnspan=3, rowspan=2)
        self.sendButton.grid(column=0, row=3)
        self.clearButton.grid(column=1, row=3)
        self.exitButton.grid(column=2, row=3)

    def __send(self):
        msg = self.inputText.get("1.0", "end-1c") # 需要用"end-1c",不然tkinter會自動在空白字串後加上'\n'
        if len(msg) == 0: # 沒有訊息則回傳
            return
        package = protocol.generateRequest(host, port, 'SEND', username, msg)
        client.sendall(package)
        self.inputText.delete("1.0", tkinter.END) # 清除輸入介面的文字

    def __clear(self):
        self.publicText.delete("1.0", tkinter.END)

    def __exit(self): # 使用者按下exit後離開chatroom並且關閉視窗
        package = protocol.generateRequest(host, port, 'EXIT', username)
        client.sendall(package)
        client.close()
        sys.exit(0)

    def __receive_message(self):
        while True:
            try:
                package = client.receive()
                req = protocol.handleRequest(package)
               
                if req.get_type() == 'SEND': # 接收到send button傳來的訊息
                    msg = req.get_data()
                    time = protocol.read_time(req.get_time())
                    output = req.get_name() + " " + time + ": "
                    output += msg + "\n"
                    self.publicText.insert(tkinter.INSERT, output)
                    
                elif req.get_type() == 'SYST': # 接收到server傳來的訊息
                    msg = req.get_data()
                    time = protocol.read_time(req.get_time())
                    output = "***SYSTEM: " + msg + "(" + time + ")" + "***\n"
                    self.publicText.insert(tkinter.INSERT, output)
                    
            except Exception as e:
                print("error : %s", e)
        

class ChatClient(socket.socket): # ChatClient繼承socket類別
    def __init__(self, username): # ChatClient建構子
        super().__init__() # 使用socket的建構子
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = username
    def connect(self, host, port, timeout=15):
        self.sock.connect((host, port))
        self.sock.settimeout(timeout)
    def close(self):
        self.sock.close()
    def receive(self):
        return self.sock.recv(RECV_BUFFER).decode()
    def sendall(self, message):
        self.sock.sendall(message.encode()) # python 3 必須使用encode()因為string和unicode為不同型別的資料


if __name__ == "__main__":
    if len(sys.argv)<3:
        print('Usage : python client.py hostname port')
        sys.exit(0)
    host = sys.argv[1]
    port= int(sys.argv[2])

    username = input("Please input your name: ").strip() # 移除多餘字元(ex: 空白)

    RECV_BUFFER = 4096

    client = ChatClient(username)
    try:
        client.settimeout(10)
        client.connect(host, port)
        print("### Connection succeeded ###\n")
    except Exception as e:
        print("### Connection failed: %s", e)
        sys.exit(0)

    app = ChatFrame()
    app.master.title(username+"@chatrooom")
    app.mainloop()
    
    
