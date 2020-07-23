from flask import Flask,request
from flask import jsonify
from flask import Blueprint
from numpy.lib.npyio import load

import logging, json, requests, traceback

from tools import Logger
from transformers.run_generation import preLoadCtrl, preLoadGpt2, genText


ctrl_t, ctrl_m, ctrl_a = None, None, None
gpt_t, gpt_m, gpt_a = None, None, None
topic_engine_flag = 0

def split_combine_text(text_ctrl, text_gpt2):
    """
    处理模型返回的文本
    """
    id = 0
    def combine_text(title_list, body_list, nums):
        text_list = []
        nonlocal id
        for i in range(nums):
            text_dic = {}
            text_dic["id"] = id
            text_dic["title"] = title_list[i]
            body = body_list[i].replace("\n", "")
            body = body.replace("\u2019", "'").replace("\u201c", "\"").replace("\u2019", "\"")
            text_dic["text"] = body[:body.rfind(".") + 1]
            text_list.append(text_dic)
            id += 1
        return text_list

    title_ctrl_list = []
    text_ctrl_list = []
    for i in range(len(text_ctrl)):
        title_temp = text_ctrl[i].split("News")[1].split("\n")[0]
        text_temp = text_ctrl[i][len(title_temp) + 6:]
        title_ctrl_list.append(title_temp)
        text_ctrl_list.append(text_temp)

    title_gpt2_list = []
    text_gpt2_list = []
    for i in range(len(text_gpt2)):
        title_temp = text_gpt2[i].split("|")[0]
        text_temp = text_gpt2[i].split("| ")[1][2:].split("<|endoftext|>")[0]
        title_gpt2_list.append(title_temp)
        text_gpt2_list.append(text_temp)

    combine_ctrl_list = combine_text(title_ctrl_list, text_ctrl_list,
                                     len(text_ctrl))
    combine_gpt2_list = combine_text(title_gpt2_list, text_gpt2_list,
                                     len(text_gpt2))
    return combine_ctrl_list + combine_gpt2_list

def start_gen_engine():
    """
    加载GPT2和CTRL模型
    """
    loggre = Logger()
    global gpt_t, gpt_m, gpt_a, ctrl_t, ctrl_m, ctrl_a, topic_engine_flag

    try:
        gpt_t, gpt_m, gpt_a = preLoadGpt2()
        ctrl_t, ctrl_m, ctrl_a = preLoadCtrl()
        topic_engine_flag = 1
        loggre.info(
            'Topic to paragraph generator engine started SUCCESSFULLY!!!')
    except:
        loggre.error(
            'Topic to paragraph generator engine loadedERROR!!!')
        return jsonify(
            code=1202002,
            msg='Topic to paragraph generator engine loaded ERROR!!!!'
        ), 200

def create_routes():
    bp = Blueprint(__name__, 'nurture')
    loggre = Logger()

    start_gen_engine()

    def exception_handler(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                loggre.error(traceback.format_exc())
                return jsonify(code=1201999, msg='inner error'), 200

        wrapper.__name__ = func.__name__
        return wrapper

    def post(url, data):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        return requests.post(url, data=json.dumps(data), headers=headers)

    @bp.route("/topic_gen", methods=('post', ))
    @exception_handler
    def topic_gen():
        """
        topic to paragraph文本生成
        """
        body = request.get_json()
        loggre.info(json.dumps(body))

        if 'title' not in body or (not body['title']):
            loggre.error('title is undefined or it is a invalide value')
            return jsonify(
                code=1202002,
                msg='title is undefined or it is a invalide value.'
            )
        if 'length' not in body or not body['length'] or (str.isdigit(str(body['length'])) != True 
                                                          or 100 > int(body['length']) 
                                                          or int(body['length']) > 500):
            loggre.error(
                'length is undefined or it is a invalide value (length must be an Interger.| length must be between 100 and 500)')
            return jsonify(
                code=1202002,
                msg='length is undefined or it is a invalide value (length must be an Interger.| length must be between 100 and 500)'
            ), 200
        if 'nums' not in body or not body['nums'] or (str.isdigit(str(body['nums'])) != True 
                                                          or 1 > int(body['nums']) 
                                                          or int(body['nums']) > 20):
            loggre.error(
                'nums is undefined or it is a invalide value. (nums must be an Interger.| nums must be between 1 and 20)')
            return jsonify(
                code=1202002,
                msg='nums is undefined or it is a invalide value. (nums must be an Interger.| nums must be between 1 and 20)'
            ), 200
        loggre.info(body)
        
        title=str(body['title'])
        length=int(body['length'])
        nums=int(body['nums'])

        global gpt_t, gpt_m, gpt_a, ctrl_t, ctrl_m, ctrl_a

        if topic_engine_flag == 1:
            ctrl_sample_nums = int(nums / 1.5) + nums % 2
            gpt2_sample_nums = nums - ctrl_sample_nums
            text_ctrl = genText(ctrl_t, ctrl_m, ctrl_a, length,
                                ctrl_sample_nums, "News " + title)

            text_gpt2 = genText(gpt_t, gpt_m, gpt_a, length,
                                gpt2_sample_nums, title + " | ")

            text_list = split_combine_text(text_ctrl, text_gpt2)
            return jsonify(code=0, msg=0, data=text_list), 200
        else:
            loggre.error(
                'Topic to paragraph generator engine is not loaded !')
            return jsonify(
                code=1202002,
                msg='Topic to paragraph generator engine is not loaded !'
            ), 200

    return bp