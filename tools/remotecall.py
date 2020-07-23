from .dbhandle import DBHandle
import json
import requests
import traceback
import time
import datetime
from .utls import Logger

def patch(data):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    # print(data)
    return requests.patch('http://172.16.102.228:8080/account/breed/update', json=data, headers=headers)

def post(url, data):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    return requests.post(url, json=data, headers=headers)

def get_comment(tag, attitude, count):
    r = post('http://172.16.102.228:8080/comment/list', {'tag': tag, 'attitude': attitude, 'count': count})
    logger = Logger()
    if r.status_code != 200:
        logger.error('get comment failed: {}'.format(r.json()))
        return []
    
    body = r.json()
    if body['code'] != 0:
        logger.error('get comment failed: {}'.format(body))
        return []
    
    comments = []
    for item in body['data']:
        comments.append(item['content'])
    
    return comments

def get_article(tag, count):
    r = post('http://172.16.102.228:8080/article/list', {'tag': tag, 'count': count})
    logger = Logger()
    if r.status_code != 200:
        logger.error('get article failed: {}'.format(r.json()))
        return []
    
    body = r.json()
    if body['code'] != 0:
        logger.error('get article failed: {}'.format(body))
        return []
    
    article = []
    for item in body['data']:
        article.append({'title': item['title'], 'content': item['content']})
    
    return article

def update_account(account):
    data = {
        'platform': account['platform'], 
        'account': account['account']
    }

    if account['status'] in [2, 3, 4]:
        data['breed_time'] = (account['uptime'] - account['addtime']) * 1000
   
    data['status'] = account['status']
    data['keep_session'] = account['keep_session']
    data['keep_session']['cookie'] = json.dumps(data['keep_session']['cookie'])
    if account['focus_topic']:
        data['focus_topic'] = account['focus_topic']
    if account['location_info']:
        data['location_info'] = [account['location_info']]
    if account['gender']:
        data['gender'] = account['gender']
    if account['birthday']:
        data['birthday'] = account['birthday']
    if account['school']:
        data['school'] = account['school']
    if account['company']:
        data['company'] = account['company']
    if account['profession']:
        data['profession'] = account['profession']
    if account['hobby']:
        data['hobby'] = account['hobby']
    if account['family_role']:
        data['family_role'] = account['family_role']
    if account['activity_level']:
        data['activity_level'] = account['activity_level']
    if account['fans_count']:
        data['fans_count'] = account['fans_count']
    if account['article_count']:
        data['article_count'] = account['article_count']
    if account['growth_value']:
        data['growth_value'] = account['growth_value']
    if account['last_ip']:
        data['last_ip'] = account['last_ip']
    data['task_id'] = account['task_id']

    r =patch(data)
    if r.status_code != 200:
        return False
    return True
