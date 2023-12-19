import sys
import requests
import json
import re
import os
import signal

API = 'https://pigjpg.com/api/pic/?order=-create_time&page='
OUTPUT_DIR = os.path.split(os.path.realpath(__file__))[0]

stop_requested = False


def sigint_handler(signum, frame):
    global stop_requested
    print(':: 已请求停止...')
    stop_requested = True


def getThisPagePic(_page=1):  # 此页图片爬取完毕返回True，此页不存在返回False，自动打印异常
    global stop_requested
    url = API + str(_page)
    # http的连接数超过最大限制，默认的情况下连接是Keep-alive的，所以这就导致了服务器保持了太多连接而不能再新建连接
    # 产生的连接数过多而导致Max retries exceeded，在header中不使用持久连接  'Connection': 'close' 或 requests.adapters.DEFAULT_RETRIES = 5
    headers = {'Connection': 'close'}
    requests.adapters.DEFAULT_RETRIES = 5
    # 请求图片列表
    try:
        got = requests.get(url, headers=headers)
    except Exception as e:
        print('\033[91m' + str(e.args) + '\033[00m')
    got_ = json.loads(got.text)
    if not got_['pics']:
        return False
    else:
        for i in range(len(got_['pics'])):
            if stop_requested:
                sys.exit(0)

            this_url = got_['pics'][i]['info']['src'][-1][0]
            this_filename = re.findall(r'([^<>/\\\|:""\*\?]+\.\w+$)', this_url)
            this_filename = this_filename[0]
            this_filepath = os.path.join(OUTPUT_DIR, this_filename)
            if os.path.exists(this_filepath):
                print('IGNORE "{}" (already exist)'.format(this_filename))
                continue
            # 请求图片文件
            try:
                pic_data = requests.get(this_url, headers=headers).content  # 因为图片为流媒体文件，所以这里使用的是content，将它转为二进制
            except Exception as e:
                print('\033[91m' + str(e.args) + '\033[00m')
            # 保存图片文件
            with open(this_filepath, 'wb') as f:  # 使用with open() 存储图片，wb标识符表示写二进制
                f.write(pic_data)
            print('OK "{}"'.format(this_filename))
        return True


if __name__ == '__main__':
    page = 1

    OUTPUT_DIR = os.path.realpath(OUTPUT_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 注册 SIGINT 信号处理函数
    signal.signal(signal.SIGINT, sigint_handler)

    while True:
        print('\033[92m' + ':: 开始爬取第 {} 页'.format(str(page)) + '\033[00m')
        if getThisPagePic(page):
            page = page + 1
        else:
            break
