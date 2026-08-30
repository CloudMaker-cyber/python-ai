# # 获取高分电影榜单(Top100)数据，并保存在cSV文件中
# # 数据包括：电影名、年份、上映时间、类型、时长、评分、语言、导演、作者、主演、Slogan、简介。
# 步骤：
# 1. 明确网站（https://www.themoviedb.org）的robots.txt中的抓取规则
# 2. 查看页面的结构，拆解具体的操作步骤，按步骤开发
# a．获取高分电影列表数据
# b. 遍历电影列表，获取每一部电影的详情信息，并提取电影数据信息
# c. 将电影详情信息保存到csv文件
import requests
import csv
from lxml import html

#常量
TMDB_BASE_URL = "https://www.themoviedb.org"
TMDB_TOP_URL = "https://www.themoviedb.org/movie/top-rated"

#获取电影详细数据
def get_movie_info(movie_info_url):
    pass

#保存电影数据为csv
def save_all_movies(all_movies):
    pass

#主函数，定义核心逻辑
def main():
    #1.发送请求，获取电影榜单数据
    response = requests.get(TMDB_TOP_URL,timeout=60)

    #2.解析数据，获取电影列表
    document = html.fromstring(response.text)
    movie_list = document.xpath("//div[@class='media-list-results contents']/div")

    #3.遍历电影列表，获取电影详情
    all_movies = [] #所有电影信息列表
    for movie in movie_list:
        movie_urls =  movie.xpath("./div/div/a/@href")

        if movie_urls:
            # 获取每个电影详细地址
            movie_info_url = TMDB_BASE_URL + movie_urls[0]
            print(movie_info_url)
            #发送请求，获取电影详细数据
            movie_info = get_movie_info(movie_info_url)
            all_movies.append(movie_info)


    #4.保存数据为csv文件
    save_all_movies(all_movies)

if __name__ == '__main__':
    main()




