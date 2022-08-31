# coding:utf-8

import pymysql
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
}

def get_areas_pinying():
    """获取各个区域的拼音"""
    url_all = "https://m.tianqi.com/lishi/shanghai"
    html_all = requests.get(url_all).text
    soup_all = BeautifulSoup(html_all, 'html.parser')
    res = soup_all.find(class_="newSearchList").select('ul li a')

    ## 获取 a 标签内的 href title 属性，标签内的文本
    areas = []
    for url in res:
        area_py = url.get('href').split('/')[-2]
        areas.append(area_py)
    
    return areas


def get_area_url(areas, years, months):
    """ 拼接成 url """
    urls = []
    for area in areas:
        for year in years:
            for month in months:
                url = 'https://m.tianqi.com/lishi/%s/%s%s.html'%(area, year, month)
                urls.append(url)
    return urls

def get_save_date(urls):
    """爬取数据，存入数据库"""
    db = pymysql.connect("localhost","root","123456","zyj_weather")
    cursor = db.cursor()

    for url in urls:
        
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        ## 获取 日期，天气，温度 所在的标签
        info_date = soup.find(class_='weatherbox').select('.date')
        info_txt1 = soup.find(class_='weatherbox').select('.txt1')
        info_txt2 = soup.find(class_='weatherbox').select('.txt2')
        ## 从标签中提取数据
        for i,j,k in zip(info_date, info_txt1, info_txt2):
            area = url.split('/')[-2]
            year = url.split('/')[-1][:4]
            date = i.get_text()[:5]
            weather = j.get_text()
            t = k.get_text().replace('℃','').split('~')
            t_low = t[0]
            t_high = t[1]
            
            ## 将提取的数据存入数据库
            sql = "INSERT INTO weather(area,year,datetime,weather,t_low,t_high) VALUES(%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,(area, year,date, weather, t_low, t_high))
        print(url)
    db.commit()
    cursor.close()
    db.close()


if __name__ == "__main__":
    years = ['2016', '2017', '2018']
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    areas = get_areas_pinying()
    urls = get_area_url(areas, years, months)
    get_save_date(urls)
