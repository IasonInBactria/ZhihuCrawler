# -*- coding: UTF-8 -*-

import requests
from lxml import html
import json
import re

# from bs4 import BeautifulSoup
#
# html = """
# <html><head><title>The Dormouse's story</title></head>
# <body>
# <p class="title" name="dromouse"><b>The Dormouse's story</b></p>
# <p class="story">Once upon a time there were three little sisters; and their names were
# <a href="http://example.com/elsie" class="sister" id="link1"><!-- Elsie --></a>,
# <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
# <a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
# and they lived at the bottom of a well.</p>
# <p class="story">...</p>
# """
#
# soup = BeautifulSoup(html)
# print soup.prettify()
# print '\n'
# print soup.head
# print soup.title

# ret = requests.get('https://mail.163.com')
# print type(ret)
# print ret.status_code
# print ret.encoding


# import urllib
#
# pic_src = ['https://pic2.zhimg.com/1ee77bfbd493593987569edbb9cda2d1_b.jpg', 'https://pic4.zhimg.com/bd92d8d07979a6b2e8852f59e240614b_b.jpg',
#             'https://pic4.zhimg.com/84a4fda92946c61402c4021600eb6ebb_b.jpg', 'https://pic1.zhimg.com/cc0da95d6cae5566832785dbba5e058c_b.jpg',
#             'https://pic3.zhimg.com/9bcc9ccb6e92b23532584cc4023f2a2a_b.jpg']
#
# pic_tag = 1
# for item in pic_src:
#     pic_path = 'D:/备份/Theme/NewWallpaper/%d.jpg' % pic_tag
#     urllib.urlretrieve(item, pic_path.decode('utf-8'))
#     pic_tag += 1


# 爬取知乎用户信息
class ZhihuCrawler():

    __doc__ = '''
    用于爬取当前永恒在知乎关注的用户的基本信息
    '''

    def __init__(self, user_id, option = 'print_data_out', src_tag=False):
        '''
        用于初始化该爬虫类
        '''

        self.option = option
        self.url = 'https://www.zhihu.com/people/' + user_id
        self.header = {}
        self.header['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 ' \
                                    '(KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
        self.header['Host'] = 'www.zhihu.com'
        self.header['Refer'] = 'https://www.zhihu.com/'
        self.cookie = {'q_c1': '0afa6d2733cf4ccbb679cbef4ff3a925|1472200908000|1464101674000',
                       'd_c0': '"AADA4lLk-AmPTscNDPGjJ4t3d2RopvZzJHI=|1464101674"',
                       '__utma': '51854390.815922627.1472525738.1472525738.1472545857.2',
                       '__utmz': '51854390.1472524354.3.2.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/people/swjason',
                       '_za': '9a6e39b1-999f-4d2f-b460-abcd76557e1e',
                       '_zap': '2dd99035-ec47-4726-9fef-543a8bb94d2b',
                       '_xsrf': 'a854eb73acb2a92f1cd987c6bd157688',
                       'l_cap_id': '"MTgwZjU5NzkzMGQ5NDY3Mzg5OGZmMDNlOWYxYWQyODA=|1472309343|b7ef7e436372d6aa1930d0887f0ce7d4e63bc133"',
                       'cap_id': '"NGM1NTk2N2U5YTMwNDg5ODk5MjVmNjk1MWQ3NzlhMjM=|1472309343|9c0387b34e5c29d432b3cdcfaee20bd4f8ac8481"',
                       'login': '"MzgyZGJhMzc1ODNjNDhlNjk2OGNiN2Y5MDkyN2NmMmQ=|1472309357|5df80be837712c8cf0e78e2fab6fe3ef448b1b33',
                       'a_t': '"2.0AADAPLkZAAAXAAAAj9TsVwAAwDy5GQAAAADA4lLk-AkXAAAAYQJVTW016VcAscVcbbeQM3694bTyr4hpz7jJHXcnnD_YZJvOAQ0xENmbZ24rcA2XFg=="',
                       'z_c0': 'Mi4wQUFEQVBMa1pBQUFBQU1EaVV1VDRDUmNBQUFCaEFsVk5iVFhwVndDeHhWeHR0NUF6ZnIzaHRQS3ZpR25QdU1rZGR3|1472546703|e87c0b2393382a42c8e4ecb063fe20b0179565a5',
                       '__utmc': '51854390', '__utmv': '51854390.100-1|2=registration_date=20120925=1^3=entry_date=20120925=1', '__utmb': '51854390.17.9.1472545898784'}
        # 用户个人信息
        self.user_id = user_id
        self.user_name = ''
        self.user_gender = ''
        self.user_location = ''
        self.user_followers_num = 0
        self.user_followees_num = 0
        self.user_agree_num = 0
        self.user_thank_num = 0
        self.user_school = ''
        self.user_major= ''
        self.user_employment = ''
        self.user_profession = ''
        self.user_info = ''
        self.user_introduction = ''
        self.user_weibo_addr = ''
        self.src_tag = src_tag
        self.skilled_topic_list = []

    def send_request(self):
        '''
        发送HTTP请求
        :return:
        '''
        if self.src_tag is True:
            get_url = self.url + '/followees'
        else:
            get_url = self.url
        try:
            ret = requests.get(get_url, cookies=self.cookie, headers=self.header)
        except requests.RequestException, e:
            print '查询用户信息失败！'
            print e.strerror
            print ret.status_code

        if ret.status_code == 200:
            pass
            # print '登录成功！'
        else:
            print('登录失败！状态码：%d\n' % ret.status_code)
            return

        html_content = ret.text
        # print html_content + '\n'
        self.process_xpath_source(html_content)

    def process_xpath_source(self, source):
        if len(source) <= 0:
            print '长度为空！\n'
            return
        else:
            # print source
            xpath_tree = html.fromstring(source)
            # 解析获取的到的html
            print('用户个人信息：')
            print '*' * 20
            try:
                self.user_name = xpath_tree.xpath('//a[@class="name"]/text()')[0].encode('utf-8')
                print('用户名：%s' % self.user_name)
            except:
                pass
            try:
                self.user_location = xpath_tree.xpath('//span[@class="location item"]/@title')[0].encode('utf-8')
                print('所在地:%s' % self.user_location)
            except:
                pass
            try:
                self.user_gender = xpath_tree.xpath('//span[@class="item gender"]/i/@class')[0].encode('utf-8')
                if 'female' in self.user_gender:
                    self.user_gender = 'female'
                else:
                    self.user_gender = 'male'
                print('性别：%s' % self.user_gender)
            except:
                pass
            try:
                self.user_employment = xpath_tree.xpath('//span[@class="employment item"]/@title')[0].encode('utf-8')
                print('任职单位：%s' % self.user_employment)
            except:
                pass
            try:
                self.user_profession = xpath_tree.xpath('//span[@class="education-extra item"]/@title')[0].encode('utf-8')
                print('所在行业：%s' % self.user_profession)
            except:
                pass
            try:
                self.user_school = xpath_tree.xpath('//span[@class="education item"]/@title')[0].encode('utf-8')
                print('毕业学校:%s' % self.user_school)
            except:
                pass
            try:
                self.user_major = xpath_tree.xpath('//span[@class="education-extra item"]/@title')[0].encode('utf-8')
                print('专业:%s' % self.user_major)
            except:
                pass
            try:
                self.user_info = xpath_tree.xpath("//span[@class='bio']/@title")[0].encode('utf-8')
                print('个人信息：%s' % self.user_info)
            except:
                pass
            try:
                self.user_introduction = xpath_tree.xpath('//textarea[@class="zm-editable-editor-input description" '
                                                          'and @id="profile-header-description-input" and '
                                                          '@name="description"]/text()')[0].encode('utf-8')
                print('个人简介:%s' % self.user_introduction)
            except:
                pass
            try:
                self.user_weibo_addr = xpath_tree.xpath('//a[@class="zm-profile-header-user-weibo"]/@href')[0].encode('utf-8')
                print('新浪微博地址:%s' % self.user_weibo_addr)
            except:
                pass

            print('个人知乎主页地址:%s' % self.url)

            try:
                self.user_followees_num = int(xpath_tree.xpath('//a[@href="/people/' + self.user_id +'/followees"]/strong/text()')[0].encode('utf-8'))
                print('关注了%d人' % self.user_followees_num)
            except:
                pass
            try:
                self.user_followers_num = int(xpath_tree.xpath('//a[@href="/people/' + self.user_id +'/followers"]/strong/text()')[0].encode('utf-8'))
                print('被%d人关注' % self.user_followers_num)
            except:
                pass
            try:
                self.user_agree_num = int(xpath_tree.xpath('//span[@class="zm-profile-header-user-agree"]/strong/text()')[0].encode('utf-8'))
                print('当前获得赞同数：%d' % self.user_agree_num)
            except:
                pass
            try:
                self.user_thank_num = int(xpath_tree.xpath('//span[@class="zm-profile-header-user-thanks"]/strong/text()')[0].encode('utf-8'))
                print('当前获得感谢数：%d' % self.user_thank_num)
            except:
                pass
            # 20160913 获取当前用户擅长话题
            if len(xpath_tree.xpath('//div[@class="zm-profile-section-wrap zm-profile-section-grid skilled-topics"]')) > 0:
                hide_lst = xpath_tree.xpath('//script[@class="ProfileExpertItem-template"]/text()')
                for item in hide_lst:
                    ret_item = re.search('class="zg-gray-darker">(.*?)</a>', item.encode('utf-8'))
                    self.skilled_topic_list.append(ret_item.groups(0)[0])
                # 隐藏的擅长话题对应的是'script'类型的结点，其向下的层级没有层次关系，都是普通的文本，需要使用正则表达式
                for item in xpath_tree.xpath('//script[@class="ProfileExpertItem-template"]/div/div/div/h3/a/text()'):
                    self.skilled_topic_list.append(item.encode('utf-8'))
                for item in xpath_tree.xpath('//div[@class="zm-profile-section-list zg-clear"]/div/div/div/h3/a/text()'):
                    self.skilled_topic_list.append(item.encode('utf-8'))
                print '该用户擅长话题：'
                for item in self.skilled_topic_list:
                    print item

            print '*' * 25
            # 模拟点击页面底部的"更多"按钮，获取全部关注者
            if self.src_tag is True:
                print('下面获取其关注的%d名用户的信息。。。\n' % self.user_followees_num)
                self.get_all_followees(xpath_tree, self.user_followees_num)

    def get_all_followees(self, xpath_tree, followees_num):

        '''通过模拟鼠标点击，发送http请求，获取全部关注者'''
        more_header = {}
        more_header['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' \
                                    ' Chrome/52.0.2743.116 Safari/537.36'
        more_header['Host'] = 'www.zhihu.com'
        more_header['Origin'] = 'https://www.zhihu.com'
        more_header['Referer'] = 'https://www.zhihu.com/people/swjason/followees'
        more_header['X-Requested-With'] = 'XMLHttpRequest'
        more_header['X-Xsrftoken'] = '264c48f2b1b06633e4dde54460648cb0'
        _xsrf = xpath_tree.xpath('//input[@name="_xsrf"]/@value')[0].encode('utf-8')
        data_init = xpath_tree.xpath('//div[@class="zh-general-list clearfix"]/@data-init')[0].encode('utf-8')
        params_dict = json.loads(data_init)
        cur_hash_id = params_dict['params']['hash_id']

        click_num = followees_num / 20
        count = 0

        cur_href_list = xpath_tree.xpath('//a[@class="zm-item-link-avatar"]/@href')
        for item in cur_href_list:
            # 拆分字符串，获取关注的人的知乎ID
            cur_href = item.encode('utf-8')
            # cur_split_list = cur_href.split('/people/')
            # 此处最好用正则表达式，因为知乎现在不仅有个人账号，抓取到的html的形式未必有'/people/'
            ret_re = re.match('/\w+/(.*)', cur_href)
            new_crawler = ZhihuCrawler(ret_re.groups(0)[0], src_tag=False)
            new_crawler.send_request()
            count += 1

        for i in xrange(1, click_num + 1):
            # 因为关注者列表一次只显示20人，所以需要多次发送请求显示全部关注的人
            more_url = 'https://www.zhihu.com/node/ProfileFolloweesListV2'
            params = json.dumps(
                {'offset': i * 20, 'order_by': 'created', "hash_id": cur_hash_id})
            payload = {'method': 'next', 'params': params, '_xsrf': _xsrf}

            try:
                ret_more = requests.post(more_url, cookies=self.cookie, data=payload, headers=more_header)
                if ret_more.status_code == 200:
                    cur_result = ret_more.text
                    info_dict = json.loads(cur_result)
                    cur_info_list = info_dict['msg']
                    for item in cur_info_list:
                        xpath_tree = html.fromstring(item)
                        cur_href = xpath_tree.xpath('//a[@class="zm-item-link-avatar"]/@href')[0].encode('utf-8')
                        # 拆分字符串，获取关注的人的知乎ID
                        cur_split_list = cur_href.split('/people/')
                        new_crawler = ZhihuCrawler(cur_split_list[1], src_tag=False)
                        new_crawler.send_request()
                        count += 1
                else:
                    print('获取失败！状态码：%d\n' % ret_more.status_code)
                    print ret_more.reason
            except requests.RequestException as e:
                pass

        print count

if __name__ == '__main__':
    print '请输入知乎用户ID：\n'
    start_name = raw_input()
    # src_tag的主要作用是控制走向，只获取输入用户和其关注的人的信息，不再向下递归
    crawler = ZhihuCrawler(start_name, src_tag=True)
    crawler.send_request()
