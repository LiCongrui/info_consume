#-*- coding:utf-8 -*-
import os
import time
import json
import datetime
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
from user_portrait.time_utils import ts2datetime
from User_sort_interface import user_sort_interface
from Offline_task import search_user_task , getResult , delOfflineTask
from temporal_rank import get_temporal_rank
from user_portrait.global_utils import R_ADMIN
from imagine import imagine
from utils import submit_task, search_task, get_group_list,\
       delete_group_results, get_social_inter_content, search_group_sentiment_weibo,\
       get_group_user_track, search_group_results, get_influence_content

                  
mod = Blueprint('influence_sort', __name__, url_prefix='/influence_sort')

@mod.route('/user_sort/', methods=['GET', 'POST'])
def user_sort():
    end_time = datetime.datetime.now()
    #end_time_nyr = end_time.strftime('%Y-%m-%d')
    end_time_nyr = '2013-09-07'
    #start_time = end_time + datetime.timedelta(days=-7)
    #start_time_nyr = start_time.strftime('%Y-%m-%d') 
    start_time_nyr = '2013-09-07'
    username = request.args.get('username', '') 
    search_time = request.args.get('time', '7')
    sort_norm = request.args.get('sort_norm', 'bci')
    sort_scope = request.args.get('sort_scope', '')
    arg = request.args.get('arg', '')
    st = request.args.get('st', start_time_nyr)
    et = request.args.get('et', end_time_nyr)
    isall = request.args.get('all','')
    number = request.args.get('number', 200)
    task_number = request.args.get('task_number', 5)
    _all = True
    if isall == 'True':
        _all = True
    else :
        _all = False
    if arg :
        pass
    else :
        arg = None
    results = user_sort_interface(username,int(search_time),sort_scope,sort_norm,arg,st,et,_all,task_number, number)
    return json.dumps(results)

@mod.route('/search_task/', methods=['GET', 'POST'])
def search_task():
    username = request.args.get('username', '')
    results = search_user_task(username)
    return json.dumps(results)

@mod.route('/get_result/' , methods=['GET','POST'])
def get_result():
    search_id = request.args.get('search_id','')
    results = getResult(search_id)
    return json.dumps(results)

@mod.route('/delete_task/' , methods =['GET','POST'])
def delete_task():
    search_id = request.args.get('search_id','')
    result = {}
    result['flag'] = delOfflineTask(search_id)
    return json.dumps(result)


@mod.route('/imagine/')
def ajax_imagine():
    uid = request.args.get('uid', '') # uid
    query_keywords = request.args.get('keywords','') # 查询字段
    submit_user = request.args.get('submit_user', '')
    query_weight = request.args.get('weight','') # 权重
    size = request.args.get('size', 100)
    keywords_list = query_keywords.split(',')
    weight_list = query_weight.split(',')

    if len(keywords_list) != len(weight_list):
        return json.dumps([])

    query_fields_dict = {}
    for i in range(len(keywords_list)):
        query_fields_dict[keywords_list[i]] = int(weight_list[i])

    # 如果查询为空，获取上一次请求数据，再为空，默认领域搜索
    if not query_fields_dict:
        user_imagine_dict = {}
        imagine_setting = R_ADMIN.hget(submit_user, "imagine_setting")
        if not imagine_setting:
            user_info = es_user_portrait.get(index="user_portrait_1222", doc_type="user", id=uid, _source=False, fields=["domain"])['_source']
            user_domain = user_info['fields']['domain'][0]
            query_fields_dict[user_domain] = 1
        else:
            query_fields_dict = json.loads(imagine_setting)
    else:
        R_ADMIN.hset(submit_user, "imagine_setting", json.dumps(query_fields_dict))
        


    query_fields_dict['size'] = int(size)

    result = []
    if uid and query_fields_dict:
        result = imagine(submit_user, uid, query_fields_dict)
    if result:
        return json.dumps(result)

    return json.dumps([])


@mod.route('/submit_task/',methods=['GET', 'POST'])
def ajax_submit_task():
    input_data = dict()
    input_data = request.get_json()
    print input_data, input_data['submit_user']
    try:
        submit_user = input_data['submit_user']
    except:
        return 'no submit_user information'
    now_ts = int(time.time())
    input_data['submit_date'] = now_ts
    status = submit_task(input_data)
    return json.dumps(status)