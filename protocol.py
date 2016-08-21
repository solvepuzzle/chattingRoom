from time import time
from datetime import datetime
from threading import Lock

mutex = Lock()
count = 0 # 0: server可以使用, 1: client可以使用

class Protocol(object):
    def __init__(self):
        super().__init__() # 使用object建構子
        self.header = Header()
        self.dataEntity = DataEntity()
    def set_version(self, version="Protocol"):
        self.version = version
    def set_uri(self, uri):
        self.uri = uri
    def set_type(self, reqtype):
        self.type = reqtype
        

class Header(object):
    def __init__(self):
        super().__init__() # 使用object建構子
        self.dict = {}
    def set_time(self, time):
        self.dict['time'] = str(float(time))
    def set_name(self, name):
        self.dict['name'] = name
    def set_datalen(self, dataEntity):
        self.dict['datalen'] = str(len(dataEntity.data))
    def pack(self):
        package = ''
        for key, value in self.dict.items():
            package += (str(key) + ':' + str(value) + '\n')
        return package
    def unpack(self, lines):
        for line in lines:
            key_value = line.split(':', 1)
            key = key_value[0]
            value = key_value[1]
            self.dict[key] = value
class DataEntity(object):
    def __init__(self):
        super().__init__() # 使用object建構子
        self.data = '' # 一開始沒有data
    def set_data(self, data):
        self.data = data
    def pack(self):
        return self.data
    def unpack(self, package):
        self.data = package

class Request(Protocol):
    def __init__(self):
        super().__init__() # 使用Protocol建構子
    def generate(self, uri, port, reqtype, time, name, data):
        self.set_version()
        self.set_uri(uri+":"+str(port))
        self.set_type(reqtype)
        print(time)
        self.header.set_time(time)
        self.header.set_name(name)
        self.dataEntity.set_data(data)
        self.header.set_datalen(self.dataEntity)
    def pack(self): # 產生封包
        package = ''
        package += self.version + ' '
        package += self.uri + ' '
        package += self.type + ' '
        package += '\n'
        package += self.header.pack()
        package += self.dataEntity.pack()
        return package
    def unpack(self, package): # 解開封包
        lines = package.split('\n')
        request_line = lines[0].split(' ')
        self.protocol = request_line[0]
        self.uri = request_line[1]
        self.type = request_line[2]
        self.header.unpack(lines[1:4])
        self.dataEntity.unpack(''.join(lines[4:]))
        
    def get_uri(self):
        return self.uri
    def get_type(self):
        return self.type
    def get_time(self):
        if 'time' in self.header.dict.keys():
            return float(self.header.dict['time'])
    def get_name(self):
        if 'name' in self.header.dict.keys():
            return self.header.dict['name']
    def get_data(self):
        return self.dataEntity.data

def read_time(timestamp): # 轉換封包裡的時間格式
    return str(datetime.fromtimestamp(int(timestamp)))
        
def handleRequest(package):
    req = Request()
    req.unpack(package)
    return req

def generateRequest(host, port, reqtype, username, data=''):
    """ 產生request封包 """
    req = Request()
    req.generate(host, port, reqtype, time(), username, data)
    package = req.pack()
    return package

