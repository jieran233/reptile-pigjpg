import sys
import requests
import json
import re
import os
import signal

API = 'https://pigjpg.com/api/pic/?order=-create_time&page='
OUTPUT_DIR = None

stop_requested = False


def sigint_handler(signum, frame):
    global stop_requested
    print(':: 已请求停止...')
    stop_requested = True


def getThisPagePic(_page=1):
    global stop_requested
    url = API + str(_page)
    headers = {'Connection': 'close'}
    requests.adapters.DEFAULT_RETRIES = 5

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
            
            try:
                pic_data = requests.get(this_url, headers=headers).content
            except Exception as e:
                print('\033[91m' + str(e.args) + '\033[00m')

            with open(this_filepath, 'wb') as f:
                f.write(pic_data)
            print('OK "{}"'.format(this_filename))
        return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: reptile.py <output_directory>')
        sys.exit(1)

    OUTPUT_DIR = os.path.realpath(sys.argv[1])
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    signal.signal(signal.SIGINT, sigint_handler)

    page = 1
    while True:
        print('\033[92m' + ':: 开始爬取第 {} 页'.format(str(page)) + '\033[00m')
        if getThisPagePic(page):
            page = page + 1
        else:
            break
