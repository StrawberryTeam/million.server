#!/usr/bin/python3
# -*- coding: utf-8 -*-
from websocket_server import WebsocketServer
import common, config
import json
import base64
import time

# 通用处理
class Million:

    _port = 9001
    _server = None

    def __init__(self):
        self._server = WebsocketServer(self._port, "0.0.0.0")                                       
        self._server.set_fn_new_client(self.new_client) #用户加入                            
        self._server.set_fn_client_left(self.client_left) #用户断开
        self._server.set_fn_message_received(self.message_received) #接收消息
        self._server.run_forever()

    # 验证发送或接收到的数据包是否合法
    def verifyData(self, data, stype = 'receive'):
        if (type(data) is not dict):
            data = json.loads(data)
        if 'type' not in data:
            raise Exception('Data type error type:' + data['type'])

        if 'receive' == stype:
            if 'UUID' not in data:
                raise Exception('UUID can not empty {}'.format(data))
        return data

    # 向客户端发送
    def sendTo(self, clientId, data):
        try:
            data = self.verifyData(data, 'send')
        except Exception as e:
            return common.ex(e)
            
        # 全员发送
        if 'all' == clientId:
            # data['receiver'] = 'all'
            self._server.send_message_to_all(json.dumps(data, ensure_ascii=False))
        else:
            self._server.send_message(clientId, json.dumps(data, ensure_ascii=False))

        print("发送: {} to client {}".format(data, clientId))


    # 发送聊天消息
    def sendChat(self, fromName, toId, msg):
        return self.sendTo(toId, {
            'from': fromName,
            'type': 'chat',
            'msg': msg.strip()
        })

    # 当新的客户端连接时会提示                                                                        
    # Called for every client connecting (after handshake)                          
    def new_client(self, client, server):                                    
        print("New client connected and was given id {}".format(client['id']))
        # self.sendTo('all', {'type': 'newplayer', 'msg': '进入了房间'})
                                                                                
    # 当旧的客户端离开                                                                         
    # Called for every client disconnecting                                         
    def client_left(self, client, server):
        print("Client({}) disconnected".format(client['id']))
                                                                                
    # UUID: clientHandler
    _clients = {}
    # 接收客户端的信息。                                                                             
    # Called when a client sends a message                                          
    def message_received(self, client, server, data):
        try:
            data = self.verifyData(data)
        except Exception as e:
            return common.ex(e)
        print("Client({}) 接收: {}".format(client['id'], data))

        self._clients[data['UUID']] = client
        # data['_clientId'] = client
        name = data['type']
        try:
            getattr(self, name)(data)
        except AttributeError as e:
            return common.ex('接收消息处理失败', e)

    # 给客户端显示错误
    def errorShow(self, to, msg):
        self.sendTo(to, {
            'type': 'errorShow',
            'msg': msg
        })
        return False


    # 用户信息
    _userList = {}

    # 新用户加入
    def newplayer(self, data):
        print('do newplayer')

        if not data['name'].strip():
            return self.errorShow(self._clients[data['UUID']], '名字不能为空')

        # 添加人员信息
        self._userList[data['UUID']] = {
            'UUID': data['UUID'], 
            'name': data['name'], 
            'jointime': int(time.time()), 
            # 'joinip': data["ip"],
            # '_clientId': data["_clientId"],
        }

        # 发送消息
        self.sendChat('系统', 'all', '欢迎 {} 加入海岛争夺'.format(data['name']))

        return self.getMyInfo({"UUID": data['UUID']})

    # 获取用户信息
    def getMyInfo(self, data):
        print('do get my info')

        if data['UUID'] not in self._userList:
            print('notlogin')
            return self.sendTo(self._clients[data['UUID']], {
                'type': 'getMyInfo',
                'status': 'notlogin',
            })
        else:
            print('login')
            userInfo = self._userList[data['UUID']]
            return self.sendTo(self._clients[data['UUID']], {
                'type': 'getMyInfo',
                'status': 'success',
                'userInfo': userInfo
            }) 

    # 聊天 
    def chat(self, data):
        print('do chat')
        self.sendChat(data['from'], data['to'], data['msg'])

    # 获取已创建房间列表
    def getRoomList(self, data, refresh = False):
        print('do get room list')
        # 还没有房间
        if len(self._roomList) <= 0:
            return False

        to = self._clients[data['UUID']]
        # 即刷新所有人的列表
        if True == refresh:
            to = 'all'

        self.sendTo(to, {
            'type': "getRoomList",
            'status': 'success',
            'roomList': self._roomList,
        })


    # 房间缓存
    _roomList = {}
    # 最后的 room
    _lastRoomId = 5000
    # 创建新房间
    def newRoom(self, data):
        print('do get newRoom')
        self._lastRoomId = self._lastRoomId + 1
        roomId = self._lastRoomId
        self._roomList[roomId] = {
            'roomId': roomId,
            'name': data['name'],
            'min_per': data['min_per'],
            'map_size': data['map_size'],
            'created_at': int(time.time()),
            'userList': [data['UUID']]
        }

        # 通知创建人创建成功
        self.sendTo(self._clients[data['UUID']], {
            'type': 'newRoom',
            'status': 'success',
            'roomId': roomId,
        })

        # 通知大厅 重新加载
        return self.getRoomList(data, True)

    # 加入一个房间
    def join2Room(self, data):
        print('do join to room')
        if data['roomId'] not in self._roomList:
            self.getRoomList(data) # 刷新他的房间列表
            return common.ex('房间已被解散，请重新进入')

        self.sendTo(self._clients[data['UUID']], {
            'type': "getRoomList",
            'status': 'success',
            'roomInfo': self._roomList[data['roomId']],
        })

Million()