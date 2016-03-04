#!/usr/bin/python
#encoding=utf-8
import hashlib
import json
import time
import os
import re
from bottle import route,run,request,get,post,install
from bottle.ext import redis
plugin = redis.RedisPlugin(host='localhost', password='XXX')
install(plugin)

config_cate_expire = {'food':0, 'sport':0, 'blog':86400}
cate_re = '<cate:re:('+'|'.join(config_cate_expire.keys())+')>'

@get('/get/'+cate_re)
def getResult(cate, rdb):
    query = request.query.query or ''
    if (len(query) < 1):
        return error_003('query')

    query_str = query.encode('utf-8')
    query_md5 = hashlib.md5(query_str).hexdigest()
    query_key = cate+'|res|'+query_md5
    if (rdb.exists(query_key)):
        return fetch(rdb, query_key)

    words = parseText(cate, query_str, rdb, False)
    if (len(words) == 0):
        return output(1, [])

    num = rdb.zinterstore(query_key, words)
    if (num == 0):
        rdb.zunionstore(query_key, words)
    rdb.expire(query_key, 300)

    return fetch(rdb, query_key)

def fetch(rdb, query_key):
    result = rdb.zrangebyscore(query_key, '-inf', '+inf')
    return output(1, result)

@post('/set/'+cate_re+'/<info:re:[a-zA-Z0-9_]+>')
def setText(cate, info, rdb):
    words = parseText(cate, request.body.read(), rdb, True)
    score = request.query.score or str(int(time.time()))
    cate_key = cate+'|info|'+info

    # delete old word relation
    for word in rdb.smembers(cate_key):
        rdb.zrem(word, info)

    # add new word relation and item
    for word in words:
        rdb.zadd(word, info, score)
        rdb.sadd(cate_key, word)

    if (config_cate_expire[cate] > 0) and rdb.exists(cate_key) > 0:
        rdb.expire(cate_key, config_cate_expire[cate])

    return output(1, len(words))

def getKey(cate, word, rdb, incr):
    word_id = getWordId(word, rdb, incr)
    if word_id > 0:
        return cate+'|word|'+str(word_id)
    return False

def parseText(cate, text, rdb, auto_id):
    text = text.decode('utf-8')

    result = []
    re_str = [u"([\u4e00-\u9fff])", u"([\w]+)"]
    for xx in re_str:
        pattern = re.compile(xx)
        results = pattern.findall(text)
        for word in results:
            _ = getKey(cate, word, rdb, auto_id)
            if _:
                result.append(_)

    return list(set(result))


def getWordId(word, rdb, auto_id):
    word_md5 = hashlib.md5(word.encode('utf-8')).hexdigest()
    result = 0
    if rdb.hexists('word_index', word_md5):
        result = rdb.hget('word_index', word_md5)
    elif auto_id:
        result = rdb.incr('word_count')
        rdb.hset('word_index', word_md5, result)
    return result

def output(success, data=None, error=None):
    result = {'success':success}
    if (success == 1 and data != None):
        result['data'] = data
    elif (success == 0 and error != None):
        result['error'] = error
    return json.dumps(result)

def error(num, msg):
    result = {'code':num, 'msg':msg}
    return output(0, None, result)

def error_003(msg):
    return error('003', msg+' is invalid')

config_file = open('host.conf')
_host, _port = config_file.read().split(':')
config_file.close()
run(host=_host, port=_port)

