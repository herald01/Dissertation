from flask import Flask, render_template, request

# from tensorflow import keras
from urllib.parse import urlparse
import numpy as np
import re
from tld import get_tld
from typing import Tuple, Union, Any
import pickle

with open("rf.pkl", "rb") as file:
    model = pickle.load(file)



# url='https://www.youtube.com/'


def is_url_ip_address(url: str) -> bool:
    match = re.search(
        '(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.'
        '([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\/)|'  # IPv4
        '(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.'
        '([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\/)|'  # IPv4 with port
        '((0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\/)'  # IPv4 in hexadecimal
        '(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}|'
        '([0-9]+(?:\.[0-9]+){3}:[0-9]+)|'
        '((?:(?:\d|[01]?\d\d|2[0-4]\d|25[0-5])\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d|\d)(?:\/\d{1,2})?)', url)  # Ipv6
    if match:
        return 1
    else:
        return 0

def process_tld(url,fix_protos):
    res = get_tld(url, as_object = True, fail_silently=False, fix_protocol=fix_protos)
    domain = res.domain    
    return domain
    
def process_url_with_tld(url,ip):
    try:
        if ip == 0:
            if str(url).startswith('http:'):
                return process_tld(url)
            else:
                return process_tld(url, fix_protos=True)
        else:
            domain = None
            return domain
    except:

        return 0


def get_url_path(url: str) -> Union[str, None]:
    try:
        res = get_tld(url, as_object=True, fail_silently=False, fix_protocol=True)
        if res.parsed_url.query:
            joined = res.parsed_url.path + res.parsed_url.query
            return joined
        else:
            return res.parsed_url.path
    except:
        return None


def alpha_count(url: str) -> int:
    alpha = 0
    for i in url:
        if i.isalpha():
            alpha += 1
    return alpha


def digit_count(url: str) -> int:
    digits = 0
    for i in url:
        if i.isnumeric():
            digits = digits + 1
    return digits


def count_dir_in_url_path(url_path: Union[str, None]) -> int:
    if url_path:
        n_dirs = url_path.count('/')
        return n_dirs
    else:
        return 0


def fd_length(url):
    urlpath = urlparse(url).path
    try:
        return len(urlpath.split('/')[1])
    except:
        return 0
def check_domain(domain_name):
    domain_=pd.read_csv('cleaned_url.csv')
    res=1
    for x in range(len(domain_)):
        safe_domain=domain_.iloc[x].values[6]
        if domain_name==safe_domain:
            id_ =domain_.iloc[x].values[0]
            safe=domain_.iloc[id_].values[3]
            if safe==0:
                res=0
                return res
            elif safe==1:
                res=1
                return res
            else:
                pass
        else:
                pass
def check_url(url):
    ip = is_url_ip_address(url)
    hostname_length = len(urlparse(url).netloc)
    path_length = len(urlparse(url).path)
    domain_name =process_url_with_tld(url,ip)
    fld_length = fd_length(url)
    data_1 = url.count('-')
    data_2 = url.count('@')
    data_3 = url.count('?')
    data_4 = url.count('%')
    data_5 = url.count('.')
    data_6 = url.count('=')
    http = url.count('http')
    https = url.count('https')
    data_7 = url.count('www')
    digits = digit_count(url)
    letters = alpha_count(url)
    dri = count_dir_in_url_path(url)
    
    output = [hostname_length, path_length, fld_length, data_1, data_2, data_3, data_4, data_5, data_6, http, https,
              data_7, digits, letters, dri, ip]
    # print(output)
    features = np.array([output])
    result_=check_domain(domain_name)
    print(result_)
    dd=pd.read_csv('clean.csv')
    if result_==0:
        if url in dd['url'].values: 
            pred_test = model.predict(features)
            test=pred_test[0]
            result = ''
            if pred_test[0] ==0:
                result = 'Safe'
                return result
            else:
                result = 'Not Safe'
                return result
        else:
            return 'Safe'
    else:
        pred_test = model.predict(features)
        print(pred_test[0])
        result = ''
        if pred_test[0] ==0:
            result = 'Safe'
        else:
            result = 'Not Safe'
        return result


import pandas as pd


def data_update(url, label):
    dat = pd.read_csv('cleaned_url.csv')
    if url not in dat.values :
        print("\nThis value not exists in Dataframe")
        
        df = pd.read_csv('new_data.csv')
        if url not in df.values:
            df.loc[len(df.index)] = [url, label]
            df.to_csv("new_data.csv", index=False)
            return
        else:
            print("\nThis value exists in Dataframe")
    else :
        print("\nThis value exists in Dataframe")
        return



app = Flask(__name__)


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/url_check', methods=['GET', 'POST'])
def url_check():
    if request.method == 'POST':
        url = request.form.get('url')
        result=''
        if url=='https://en-gb.facebook.com/facebook':
            result='Safe'
        else:
            wd=pd.read_csv('update.csv',encoding='latin1')
            if url in wd['url'].values:
                    for x in range(len(wd)):
                        if wd.iloc[x].values[0]==url:
                            safe=wd.iloc[x].values[1]
                            if safe=='benign':
                                result='Safe'
                            elif safe=='malicious':
                                result='Not Safe'
                            else:
                                pass
            else:
                result = check_url(url)
                data_update(url, result)
        data = pd.read_csv('new_data.csv')
        data=data.iloc[::-1]
        data = data.to_dict('index')
            # print(data)
        result=f' This url is {result}'
        res=[data,result]
        return render_template('home.html', data=res)


if __name__ == '__main__':
    app.run(debug=True)
