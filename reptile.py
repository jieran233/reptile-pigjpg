import requests
import json
import re
API = 'https://pigjpg.com/api/pic/?order=-create_time&page='

def getThisPagePic(page=1): # 此页图片爬取完毕返回True，此页不存在返回False，自动打印异常
    url = 'https://pigjpg.com/api/pic/?order=-create_time&page=' + str(page)
    # http的连接数超过最大限制，默认的情况下连接是Keep-alive的，所以这就导致了服务器保持了太多连接而不能再新建连接
    # 产生的连接数过多而导致Max retries exceeded，在header中不使用持久连接  'Connection': 'close' 或 requests.adapters.DEFAULT_RETRIES = 5
    headers = {'Connection': 'close'}
    requests.adapters.DEFAULT_RETRIES = 5
    try:
        got = requests.get(url, headers=headers)
    except Exception as e:
        print('\033[0;31m' + str(e.args) + '\033[0m')
    got_ = json.loads(got.text)
    if(got_['pics'] == []):
        return(False)
    else:
        for i in range(len(got_['pics'])):
            thisurl = got_['pics'][i]['info']['src'][-1][0]
            thisfilename = re.findall('([^<>/\\\|:""\*\?]+\.\w+$)', thisurl)
            thisfilename = thisfilename[0]
            print(thisfilename)
            try:
                pic_data = requests.get(thisurl, headers=headers).content # 因为图片为流媒体文件，所以这里使用的是content，将它转为二进制
            except Exception as e:
                print('\033[0;31m' + str(e.args) + '\033[0m')
            with open('imgs/{}'.format(thisfilename),'wb')as f: # 使用with open() 存储图片，wb标识符表示写二进制
                f.write(pic_data)
        return(True)

if(__name__ == '__main__'):
    page = 1
    while(True):
        print('\033[1;32;40m' + '开始爬取第 {} 页'.format(str(page)) + '\033[0m')
        if(getThisPagePic(page)):
            page = page + 1
        else:
            break