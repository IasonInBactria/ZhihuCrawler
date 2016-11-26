# -*- coding: UTF-8 -*-

import requests
from lxml import html
import json
import re
from PIL import Image
import time
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

# 处理账户错误信息
class AccountError(Exception):
    def __init__(self, err_message):
        print err_message


# 获取验证码信息
def get_capcha(cur_session, cur_header):
    cur_time = str(int(time.time() * 1000))
    captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + cur_time + '&type=login'
    ret = cur_session.get(captcha_url, headers=cur_header)
    with open('captcha.jpg', 'wb') as f:
        f.write(ret.content)
        f.close()

    pic = Image.open('captcha.jpg')
    print '请输入验证码！'
    pic.show()
    pic.close()
    captcha = raw_input()
    return captcha


# 登录知乎，通过用户名和密码
def login_zhihu(login_info):
    login_url = 'https://www.zhihu.com/'
    user_name = login_info[0]
    password = login_info[1]
    account_type = ''
    # 判断帐号信息是否有效
    if re.match('^1\d{10}$', user_name):
        account_type = 'phone_num'
    elif re.match('^\S+@\d+\.\S+$', user_name):
        account_type = 'email'
    else:
        raise AccountError('帐号类型错误啊！')

    login_header = {}
    login_header['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 ' \
                                '(KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    login_header['Host'] = 'www.zhihu.com'

    # 获取_xsrf信息
    ret = requests.get(login_url, headers=login_header)
    if ret.status_code != 200:
        print '获取xsrf信息失败！状态码%d，%s' % (ret.status_code, str(ret.reason))
        return False
    else:
        ret_html = ret.text
        xpath_tree = html.fromstring(ret_html)
        xsrf_info = xpath_tree.xpath('//input[@name="_xsrf"]/@value')[0]

    # 提交表单
    up_form = {account_type: user_name, 'password': password, 'remember_me': 'true',
               '_xsrf': xsrf_info}
    login_header['Origin'] = 'https://www.zhihu.com'
    login_header['Refer'] = 'https://www.zhihu.com'
    login_header['X-Requested-With'] = 'XMLHttpRequest'
    login_url += 'login/' + account_type
    login_session = requests.session()
    up_form['captcha'] = get_capcha(login_session, login_header)

    try:
        ret = login_session.post(login_url, data=up_form, headers=login_header)
    except requests.RequestException, e:
        print '登录失败！'
        print e
        print ret.status_code
        return False

    if ret.status_code == 200:
        print '登录成功！'
        print ret.text.encode('utf-8')
    else:
        print '登录失败！状态码：%d %s\n' % (ret.status_code, str(ret.reason))
        return False

    json_dict = json.loads(ret.text)
    print json_dict['msg']
    personal_cookie = dict(ret.cookies.items())

    ret = login_session.get('https://www.zhihu.com/settings/profile', headers=login_header, allow_redirects=False)
    if ret.status_code == 200:
        print '跳转成功！'
    else:
        print '跳转失败！状态码：%d %s\n' % (ret.status_code, str(ret.reason))
        return False

    # 跳转到用户个人主页
    html_content = ret.text
    # print html_content + '\n'
    head_page_tree = html.fromstring(html_content)
    user_id = head_page_tree.xpath('//div[@class="url-preview"]/span[@class="token"]/text()')[0].encode(
        'utf-8')

    # 初始化个人信息爬虫类，src_tag的主要作用是控制走向，只获取输入用户和其关注的人的信息，不再向下递归
    crawler = ZhihuCrawler(user_id, login_session, login_header, personal_cookie, src_tag=True)
    crawler.send_request()


# 爬取知乎用户信息
class ZhihuCrawler():

    __doc__ = '''
    用于爬取我在知乎关注的用户的基本信息
    '''

    def __init__(self, user_id, cur_session, cur_header, cur_cookie, option='print_data_out', src_tag=False):
        '''
        用于初始化该爬虫类
        :param url:
        :param option:
        '''

        self.option = option
        self.personal_url = 'https://www.zhihu.com/people/' + user_id
        self.header = cur_header
        self.session = cur_session
        self.cookie = cur_cookie

        # 用户个人信息
        self.user_id = user_id
        self.login_list = login_list
        self.user_name = login_list[0]
        self.user_psword = login_list[1]
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
        self.account_type = ''

    def send_request(self):
        # followee_url = self.url + '/followees'
        self_page_url = 'https://www.zhihu.com/people/' + self.user_id
        self.personal_url = self_page_url

        try:
            ret = self.session.get(self_page_url, headers=self.header)
        except requests.RequestException, e:
            print('跳转到个人页面失败！状态码：%d\n' % ret.status_code)
            print('错误描述：%s' % str(e))
            return

        if ret.status_code == 200:
            # print '跳转到个人页面成功啦！'
            pass
        else:
            print('跳转到个人页面失败！状态码：%d\n' % ret.status_code)
            return

        # print ret.text
        self.process_xpath_source(ret.text, self_page_url, self.header, self.cookie, self.session)

    # 部分知乎用户的个人页面使用了新的布局，需要兼容
    def process_xpath_source(self, source, cur_url, cur_header, cookies, session):
        if len(source) <= 0:
            print '长度为空！\n'
            return
        else:
            xpath_tree = html.fromstring(source)
            # 解析获取的到的html
            print('用户个人信息：')
            print '*' * 20
            # 分析页面布局，区分是否为新版个人页面
            page_flag = False
            if len(xpath_tree.xpath('//head/@data-reactid')) > 0:
                page_flag = True
            if page_flag is True:
                self.user_name = xpath_tree.xpath('//span[@class="ProfileHeader-name"]/text()')[0].encode('utf-8')
                print('用户名：%s' % self.user_name)
                try:
                    self.user_location = xpath_tree.xpath('//div[@class="ProfileHeader-infoItem"]/text()')[0].encode('utf-8')
                    print('所在地:%s' % self.user_location)
                except:
                    pass
                if len(xpath_tree.xpath('//svg[@class="Icon Icon--male"]')) > 0:
                    self.user_gender = 'male'
                    print('性别：%s' % self.user_gender)
                elif len(xpath_tree.xpath('//svg[@class="Icon Icon--female"]')) > 0:
                    self.user_gender = 'female'
                    print('性别：%s' % self.user_gender)
                try:
                    work_list = xpath_tree.xpath('//div[@class="ProfileHeader-info"]/div[@class="ProfileHeader-'
                                                 'infoItem"][2]/text()')
                    for work_item in work_list:
                        self.user_employment += work_item.encode('utf-8')
                    if len(work_list) > 0:
                        print('职业经历：%s' % self.user_employment)
                except:
                    pass
                try:
                    edu_list = xpath_tree.xpath('//div[@class="ProfileHeader-info"]'
                                                '/div[@class="ProfileHeader-infoItem"][3]/text()')
                    for edu_item in edu_list:
                        self.user_employment += edu_item.encode('utf-8')
                    if len(edu_list) > 0:
                        print('教育经历：%s' % self.user_school)
                except:
                    pass
                try:
                    self.user_info = xpath_tree.xpath("//span[@class='RichText "
                                                      "ProfileHeader-headline']/text()")[0].encode('utf-8')
                    print('一句话介绍：%s' % self.user_info)
                except:
                    pass
                try:
                    follow_list = xpath_tree.xpath('//div[@class="Profile-followStatusValue"]/text()')
                    self.user_followees_num = follow_list[0]
                    self.user_followers_num = follow_list[1]
                    print '关注了%d人' % self.user_followees_num
                    print '被%d人关注' % self.user_followers_num
                except:
                    pass
                try:
                    self.user_agree_num = int(
                        xpath_tree.xpath('//div[@id="root"]/div/main/div/div[1]/div[2]/div[2]'
                                         '/div[1]/div[2]/div[3]/div[1]/text()[2]')[0].encode('utf-8'))
                    print('当前获得赞同数：%d' % self.user_agree_num)
                except:
                    pass
                try:
                    self.user_thank_num = int(xpath_tree.xpath('//div[@id="root"]'
                                                               '/div/main/div/div[1]/div[2]/div[2]/div[1]'
                                                               '/div[2]/div[3]/div[2]/text()[1]')[0].encode('utf-8'))
                    print('当前获得感谢数：%d' % self.user_thank_num)
                except:
                    pass
                # # 发送请求，获取全部个人信息
                # cur_header['Host'] = 'zhihu-web-analytics.zhihu.com'
                # cur_header['Referer'] = cur_url
                # ret = session.post(cur_url, cookies=cookies, headers=cur_header)
                # if ret.status_code == 200:
                #     print '获取全部信息成功！'
                #     print ret.text
                #
                #     try:
                #         self.user_introduction = xpath_tree.xpath('//div[@class="RichText ProfileHeader'
                #                                                   '-detailValue"]/text()')[0].encode('utf-8')
                #         print '个人简介:%s' % self.user_introduction
                #     except:
                #         pass
                #     try:
                #         self.user_weibo_addr = \
                #         xpath_tree.xpath('//div[@id="ProfileHeader"]/div[2]/div/div/div[1]/div[2]'
                #                          '/span/div/div[5]/div/a/@href')[0].encode('utf-8')
                #         print '社交帐号：%d' % self.user_weibo_addr
                #     except:
                #         pass
                # else:
                #     print ret.reason

            else:
                self.user_name = xpath_tree.xpath('//div[@class="title-section"]/span[@class="name"]/text()')[0].encode('utf-8')
                print('用户名：%s' % self.user_name)

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
                    self.user_info = xpath_tree.xpath("//span[@class='bio ellipsis']/@title")[0].encode('utf-8')
                    print('一句话介绍：%s' % self.user_info)
                except:
                    pass
                try:
                    self.user_introduction = xpath_tree.xpath('//textarea[@class="zm-editable-editor-input description" '
                                                              'and @id="profile-header-description-input" and '
                                                              '@name="description"]/text()')[0].encode('utf-8')
                    #intro_list = self.user_introduction.split('\n')
                    # print intro_list
                    print('个人简介:%s' % self.user_introduction)
                except:
                    pass
                try:
                    self.user_weibo_addr = xpath_tree.xpath('//a[@class="zm-profile-header-user-weibo"]/@href')[0].encode('utf-8')
                    print('新浪微博地址:%s' % self.user_weibo_addr)
                except:
                    pass

                print('个人知乎主页地址:%s' % self.personal_url)

                try:
                    self.user_followees_num = int(xpath_tree.xpath('//a[@href="/people/' + self.user_id +'/followees"]'
                            '/strong/text()')[0].encode('utf-8'))
                    print('关注了%d人' % self.user_followees_num)
                except:
                    pass
                try:
                    self.user_followers_num = int(xpath_tree.xpath('//a[@href="/people/' + self.user_id
                            +'/followers"]/strong/text()')[0].encode('utf-8'))
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
            print '*' * 25

            # 跳转到关注者页面
            if self.src_tag is True:
                try:
                    ret = session.get(cur_url + '/followees', cookies=cookies, headers=cur_header)
                except session.RequestException, e:
                    print('跳转到关注页面失败！状态码：%d\n' % ret.status_code)
                    print('错误描述：%s' % str(e))
                    return

                if ret.status_code == 200:
                    # print '跳转到关注页面成功啦！'
                    pass
                else:
                    print'跳转到关注页面失败！状态码：%d %s\n' % (ret.status_code, str(ret.reason))
                    return

            # 模拟点击页面底部的"更多"按钮，获取全部关注者
            if self.src_tag is True and self.user_followees_num > 0:
                print('下面获取其关注的%d名用户的信息。。。\n' % self.user_followees_num)
                xpath_tree = html.fromstring(ret.text)
                self.get_all_followees(xpath_tree, self.user_followees_num, session)

    def get_all_followees(self, xpath_tree, followees_num, cur_session):

        '''通过模拟鼠标点击，发送http请求，获取全部关注者'''
        count = 0
        # 先获取20个人现成的
        cur_list = xpath_tree.xpath('//a[@class="zg-link author-link"]/@href')
        for cur_item in cur_list:
            cur_split_list = cur_item.split('/people/')
            # print cur_split_list[1]
            new_crawler = ZhihuCrawler(cur_split_list[1], self.session, self.header, self.cookie)
            new_crawler.send_request()
            count += 1
        # cur_header['Refer'] = 'https://www.zhihu.com/people/swjason/followees'
        _xsrf = xpath_tree.xpath('//input[@name="_xsrf"]/@value')[0].encode('utf-8')
        # cur_header['X-Xsrftoken'] = _xsrf

        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Host': "www.zhihu.com",
            'Referer': 'https://www.zhihu.com/people/swjason/followees',
            'Origin': 'https: // www.zhihu.com',
            'X-Requested-With': 'XMLHttpRequest',
            'X-Xsrftoken': _xsrf
        }

        data_init = xpath_tree.xpath('//div[@class="zh-general-list clearfix"]/@data-init')[0].encode('utf-8')
        params_dict = json.loads(data_init)
        cur_hash_id = params_dict['params']['hash_id']

        click_num = followees_num / 20

        for i in xrange(1, click_num + 1):
            # 因为关注者列表一次只显示20人，所以需要多次发送请求显示全部关注的人
            more_url = 'https://www.zhihu.com/node/ProfileFolloweesListV2'
            params = json.dumps(
                {'offset': i * 20, 'order_by': 'created', "hash_id": cur_hash_id})
            payload = {'method': 'next', 'params': params, '_xsrf': _xsrf}

            try:
                ret_more = cur_session.post(more_url, data=payload, headers=header)
                if ret_more.status_code == 200:
                    cur_result = ret_more.text
                    # if i < 3:
                    #     print cur_result
                    # 获取当前用户全部关注的人的信息
                    info_dict = json.loads(cur_result)
                    cur_info_list = info_dict['msg']
                    for item in cur_info_list:
                        xpath_tree = html.fromstring(item)
                        cur_href = xpath_tree.xpath('//a[@class="zm-item-link-avatar"]/@href')[0].encode('utf-8')
                        # 拆分字符串，获取关注的人的知乎ID
                        cur_split_list = cur_href.split('/people/')
                        # print cur_split_list[1]
                        new_crawler = ZhihuCrawler(cur_split_list[1], self.session, self.header, self.cookie)
                        new_crawler.send_request()
                        count += 1

                    # print '获取成功！'
                else:
                    print('获取失败！状态码：%d\n' % ret_more.status_code)
                    print ret_more.reason
            except requests.RequestException as e:
                pass
           # print('%d:%s' % i, cur_name)
        print count

if __name__ == '__main__':
    print '请输入用户名和密码，以空格分隔，输入完成后按回车键结束：\n'
    login_str = raw_input()
    login_list = login_str.split(' ')
    while len(login_list) != 2 or len(login_list[1]) < 6:
        print '输入错误，请重新输入！'
        login_str = raw_input()
        login_list = login_str.split(' ')

    login_zhihu(login_list)



