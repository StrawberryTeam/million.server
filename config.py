# -*- coding: utf-8 -*-
#!/usr/bin/python3

'''
    所有配置
'''
APP_ENV = "LOCAL" # 开发环境
# APP_ENV = "PRODUCTION" # 生产环境

if "LOCAL" == APP_ENV:
    mongo_client = 'mongodb://192.168.56.102:27017'
    db = 'million'
