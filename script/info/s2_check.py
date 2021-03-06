#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'orleven'

import re
import time
import urllib.parse
import requests
requests.packages.urllib3.disable_warnings()

_ERROR_KEYS = ['Struts Problem Report','org.apache.struts2','struts.devMode','struts-tags',
              'There is no Action mapped for namespace']


def get_script_info(data=None):
    script_info = {
        "name": "struts scan",
        "info": "This is a test.",
        "level": "low",
        "type": "info",
    }
    return script_info

def prove(data):
    data = init(data, 'web')
    # _status_flag = 5 # 暂定
    if data['base_url'] :
        test = _gethtml(data['url'],data['headers'], data['timeout'])
        if test['code'] != 0:
            funlist = [_checkDevMode,_checkBySuffix,_checActionsErrors,_checkCheckBox,_checkl18n]
            for fun in funlist:
                flag = fun(data['base_url'], data['headers'], data['timeout'])
                info = fun.__name__
                if flag:
                    data['flag'] = 1
                    data['data'].append({"flag": info})
                    data['res'].append({"info": "struts_by" + info, "key": info})
                    break
    return data



# check suffix :.do,.action
def _checkBySuffix(url,headers,timeout):
    
    info = _gethtml(url, headers,timeout)
    if info['code'] == 404:
        return False
    html = info['html']
    matchs_action = re.findall(r"""(['"]{1})(/?((?:(?!\1|\n|http(s)?://).)+)\.action)(\?(?:(?!\1).)*)?\1""", html,
                        re.IGNORECASE)
    matchs_do = re.findall(r"""(['"]{1})(/?((?:(?!\1|\n|http(s)?://).)+)\.do)(\?(?:(?!\1).)*)?\1""", html,
                        re.IGNORECASE)

    if len(matchs_do)+len(matchs_action)> 0 and (".action" in str(matchs_action) or ".do" in str(matchs_do)):
        return True
    else:
        return False


# check devMode page
def _checkDevMode(url,headers,timeout):
    target_url = url+"/struts/webconsole.html"
    info = _gethtml(target_url,headers,timeout)

    if info['code'] == 200 and "Welcome to the OGNL console" in info['html']:
        return True
    else:
        return False

# check Error Messages.
def _checActionsErrors(url,headers,timeout):
    test_tmpurls = []
    test_tmpurls.append(url+"/?actionErrors=1111")
    test_tmpurls.append(url+"/tmp2017.action")
    test_tmpurls.append(url + "/tmp2017.do")
    test_tmpurls.append(url + "/system/index!testme.action")
    test_tmpurls.append(url + "/system/index!testme.do")

    for test_url in test_tmpurls:
        info = _gethtml(test_url,headers,timeout)
        for error_message in _ERROR_KEYS:
            if error_message in info['html'] and info['code'] == 500:
                print ("[+] found error_message:",error_message)
                return True
    return False

# check CheckboxInterceptor.
def _checkCheckBox(url,headers,timeout):
    for match in re.finditer(r"((\A|[?&])(?P<parameter>[^_]\w*)=)(?P<value>[^&#]+)", url):

        info = _gethtml(url.replace(match.group('parameter'), "__checkbox_"+match.group('parameter')),headers,timeout)
        check_key = 'name="{}"'.format(match.group('parameter'))
        check_value = 'value="false"'

        html = info['html']
        matchs_inputTags = re.findall(r"""<\s*input[^>]*>""", html,re.IGNORECASE)
        for input_tag in matchs_inputTags:
            if check_key in input_tag and check_value in input_tag:
                return True

    return False



def _checkl18n(target,headers,timeout):
    info_orgi = _gethtml(target,headers,timeout)
    time.sleep(0.5)
    info_zhCN = _gethtml(target+"?"+'request_locale=zh_CN',headers,timeout)
    time.sleep(0.5)
    info_enUS = _gethtml(target+"?"+ 'request_locale=en_US',headers,timeout)
    time.sleep(0.5)

    if "request_locale=zh_CN" in info_orgi['html'] and "request_locale=en_US" in info_orgi['html']:
        return True

    if abs(len(info_zhCN['html']) - len(info_enUS['html'])) > 1024:
        return True

    return False

def _gethtml(url,headers,timeout):
    try:
        u = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        content = u.text
        return {"html":content,"code":u.status_code,"url":url}
    except Exception as e:
        # print(e)
        # _status_flag = _status_flag - 1
        return {"html":"", "code":0, "url": url}
        # return _get_html_phantomJS(url)

# 使用PhantomJS获取网页源码
def _get_html_phantomJS(url):
    try:
        from selenium import webdriver
        dr = webdriver.PhantomJS()
        dr.get(url)
        time.sleep(2)
        return {"html": dr.page_source, "code": 200, "url": url}

    except Exception as e:
        # http://phantomjs.org/
        print (e)
        return {"html":"", "code":500, "url":url}
