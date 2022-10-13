import requests as r
from lxml import etree
import time
import random
import base64

def login():
    flag = 0
    # 设填写的体温a是36.0~36.8的随机数
    a = random.uniform(36.0, 36.8)
    a = str(a)[:4:]
    b = random.uniform(36.0, 36.8)
    b = str(b)[:4:]

    # 此处是找到当前时间戳定位url
    timetamp = time.mktime(time.localtime())
    timetamp = int(timetamp)
    # 各个链接
    url = "http://xscfw.hebust.edu.cn/survey/ajaxLogin"  # 登录链接
    url2 = "http://xscfw.hebust.edu.cn/survey/index"  # 获取sid链接
    url3 = f"http://xscfw.hebust.edu.cn/survey/surveySave?timestamp={timetamp}"  # 填报体温的地址
    url4 = f"http://xscfw.hebust.edu.cn/survey/verifyCode?d={timetamp}"

    def ocr(path):
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
        # 二进制方式打开图片文件
        f = open(path, 'rb')
        img = base64.b64encode(f.read())

        params = {"image": img}

        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=Ny48ItG8jj4ueTWk3AM6ZRu6&client_secret=ZFsn9tfI5nSsrblMdn4Ca2GG8sjIHjGq'
        response = r.get(host)
        if response:
            access_token = response.json()['access_token']
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = r.post(request_url, data=params, headers=headers)
        if response:
            return response.json()['words_result'][0]['words']


    def tianbao():
        # 填报程序
        try:
            rep = r.post(url=url3, params=data, headers=header, cookies=cookies)
            flag=1
        except:
            print("填报出错")
            flag = 0

    # 账号信息
    param = {
        "stuNum": "190708324",  # 学号
        "pwd": "Lc2#0002191219",  # 密码
        "vcode": ""
        # 韩天华
        # "stuNum": "190708305",  # 学号
        # "pwd": "Lc2#0111160012",  # 密码
        # "vcode": ""
        # 杨旭帅
        # "stuNum": "190708320",  # 学号
        # "pwd": "Xxxy2019....",  # 密码
        # "vcode": ""
    }

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.62"
    }

    # 识别验证码
    def identification():
        img = r.get(url=url4, headers=header, cookies=cookies,stream=True)
        # 下载图片
        with open('verifyCode.jpg', 'wb') as fd:
            for chunk in img.iter_content(128):
                fd.write(chunk)

        # 识别验证码
        vcode = ocr('verifyCode.jpg')
        # 验证码识别结果
        print(vcode)

        # 添加字典属性值
        param['vcode'] = vcode
        # 提交表单
        response = r.post(url=url, headers=header, cookies=cookies, params=param)
        data = response.json()
        return data['data']

    # 登录程序
    try:
        response = r.post(url=url, params=param, headers=header)
        cookiesJAR = response.cookies  # 获取cookies
        cookies = cookiesJAR.get_dict()  # 把cookies写成字典形式

        try:
            while 1:
                data = identification()
                if data != 'vcode':
                    break
        except:
            print("error")

        res = r.get(url=url2, headers=header, cookies=cookies, params=param)
        print("登录成功")
    except:
        print("登录失败")
        flag = 0

    # 获取完成情况
    try:
        res.encoding = 'uft-8'
        html = etree.HTML(res.text)
        content = html.xpath('/html/body/ul/li[1]/div/span/text()')
        print(content)
    except:
        print("获取失败")
        flag = 0
    # 获取当前日期要填的文档的sid
    try:
        url6 = 'http://xscfw.hebust.edu.cn/survey/index.action'
        rek = r.get(url=url6, cookies=cookies, headers=header, params=param)
        rek.encoding = 'utf-8'
        html3 = etree.HTML(rek.text)
        sid = html3.xpath('/html/body/ul/li[1]/@sid')[0]
        print(f"获取sid成功：{sid}")
    except:
        print("获取sid失败")
        flag = 0
    # 获取stuId和qid
    try:
        url5 = f'http://xscfw.hebust.edu.cn/survey/surveyEdit?id={sid}'
        rej = r.get(url=url5, cookies=cookies, headers=header)
        rej.encoding = 'utf-8'
        html2 = etree.HTML(rej.text)
        stuId = html2.xpath('//*[@id="surveyForm"]/input[2]/@value')[0]
        qid = html2.xpath('//*[@id="surveyForm"]/input[3]/@value')[0]
        print(f"获取stuId成功：{stuId}")
        print(f"获取qid成功:{qid}")
    except:
        print("获取stuId qid 失败")
        flag = 0
    # 要填写的数据,其中a是36.0~36.8的随机数
    # 要填写的数据,其中b是36.0~36.8的随机数
    try:
        data = {
            "id": sid,
            "stuId": stuId,
            "qid": qid,
            "location": '',
            "c0": "不超过37.3℃，正常",
            "c1": a,
            "c3": "不超过37.3℃，正常",
            "c4": b,
            "c6": "健康",
        }
    except:
        print("获取信息有误")
        flag = 0
    # 判断程序
    try:
        print("开始执行")
        if content[0] == '已完成':
            flag = 1
            print('填报成功')
        if content[0] == '未完成':
            tianbao()
            flag = 1
            print('填报成功')
    except:
        print("判断失败")
        flag = 0
    print(flag)


if __name__ == "__main__":
    login()