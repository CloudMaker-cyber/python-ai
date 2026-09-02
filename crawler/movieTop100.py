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
import re

#常量
MOVIE_LIST_FILE = "csv_data/movie_list.csv"
TMDB_BASE_URL = "https://www.themoviedb.org"
TMDB_TOP_URL1 = "https://www.themoviedb.org/movie/top-rated?language=zh-CN"
TMDB_TOP_URL2 = "https://www.themoviedb.org/discover/movie/items"

#获取电影年份
def get_movie_year(movie_years):
    movie_year = movie_years[0].strip() if movie_years else ""
    return movie_year.replace("(","").replace(")","")

#获取电影上映时间
def get_movie_release_dates(movie_release_dates):
    movie_release_date = movie_release_dates[0].strip() if movie_release_dates else ""
    return re.search(r'\d{4}-\d{2}-\d{2}', movie_release_date).group() if movie_release_date else ""


def get_movie_durations(movie_durations):
    movie_duration =  movie_durations[0].strip() if movie_durations else ""
    h_res = re.search(r"(\d+)h", movie_duration)
    m_res = re.search(r"(\d+)m", movie_duration)
    h = int(h_res.group(1)) if h_res else 0#因为前面用（）来分组了，所以需要用group(1)获取
    m = int(m_res.group(1)) if m_res else 0
    return h * 60 + m

#获取电影详细数据
def get_movie_info(movie_info_url):
    print(f"发送请求：{movie_info_url}，获取电影详情数据")
    mov_response =  requests.get(movie_info_url)
    mov_doc =  html.fromstring(mov_response.text)

    # 数据包括：电影名、年份、上映时间、类型、时长、评分、语言、导演、编剧、作者、主演、Slogan、简介
    movie_names = mov_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/a/text()")
    movie_years = mov_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/span/text()")
    movie_release_dates = mov_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[2]/text()")
    movie_genres = mov_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[3]/a/text()")
    movie_durations = mov_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[4]/text()")
    movie_scores = mov_doc.xpath("//*[@id='consensus_pill']/div/div[1]/div/div/@data-percent")
    movie_languages = mov_doc.xpath("//*[@id='media_v4']/div/div/div[2]/div/section/div[1]/div/section[1]/p[3]/text()")
    movie_directors = mov_doc.xpath("//li[@class='profile'][.//p[@class='character'][contains(.,'Director')]]/p[1]/a/text()")#筛选的写法
    movie_screenplay = mov_doc.xpath("//li[@class='profile'][.//p[@class='character'][contains(.,'Screenplay')]]/p[1]/a/text()")
    movie_novel = mov_doc.xpath("//li[@class='profile'][.//p[@class='character'][contains(.,'Novel')]]/p[1]/a/text()")
    movie_actors = mov_doc.xpath("//*[@id='cast_scroller']/ol/li[@class='card']/p[1]/a/text()")
    movie_slogans = mov_doc.xpath("//*[@id='original_header']/div[2]/section/div[3]/h3[@class='tagline']/text()")
    movie_introductions = mov_doc.xpath("//*[@id='original_header']/div[2]/section/div[3]/div/p/text()")

    #返回字典类型数据
    movie_info = {
        "电影名": movie_names[0].strip() if movie_names else "",
        "年份": get_movie_year(movie_years),
        "上映时间": get_movie_release_dates(movie_release_dates),
        "类型": movie_genres[0].strip() if movie_genres else "",
        "时长": get_movie_durations(movie_durations),
        "评分": movie_scores[0].strip() if movie_scores else "",
        "语言": movie_languages[0].strip() if movie_languages else "",
        "导演": movie_directors[0].strip() if movie_directors else "",
        "编剧": movie_screenplay[0].strip() if movie_screenplay else "",
        "作者": movie_novel[0].strip() if movie_novel else "",
        "主演": movie_actors[0].strip() if movie_actors else "",
        "Slogan": movie_slogans[0].strip() if movie_slogans else "",
        "简介": movie_introductions[0]    .strip() if movie_introductions else ""
    }

    return movie_info

#保存电影数据为csv
def save_all_movies(all_movies):
    with open(MOVIE_LIST_FILE,"w",encoding="utf-8",newline='') as csvfile:
        writer = csv.DictWriter(csvfile,fieldnames=["电影名","年份","上映时间","类型","时长","评分","语言","导演","编剧","作者","主演","Slogan","简介"])
        writer.writeheader()#写入表头
        writer.writerows(all_movies)#写入多行数据

#主函数，定义核心逻辑
def main():
    all_movies = []  # 所有电影信息列表
    #循环获取电影列表数据
    for page_num in range(1,6):
        # 1.发送请求，获取电影榜单数据
        if page_num == 1:
            response = requests.get(TMDB_TOP_URL1, timeout=60)
        else:
            response = requests.post(TMDB_TOP_URL2,
                                     f"air_date.gte=&air_date.lte=&certification=&certification_country=JP&debug=&first_air_date.gte=&first_air_date.lte=&include_adult=false&include_softcore=false&latest_ceremony.gte=&latest_ceremony.lte=&page={page_num}&primary_release_date.gte=&primary_release_date.lte=&region=&release_date.gte=&release_date.lte=2027-02-28&show_me=everything&sort_by=vote_average.desc&vote_average.gte=0&vote_average.lte=10&vote_count.gte=300&watch_region=JP&with_genres=&with_keywords=&with_networks=&with_origin_country=&with_original_language=&with_watch_monetization_types=&with_watch_providers=&with_release_type=&with_runtime.gte=0&with_runtime.lte=400",
                                     timeout=60)

        print(f"发送请求,访问第{page_num}页数据，获取电影榜单数据")
        # 2.解析数据，获取电影列表
        document = html.fromstring(response.text)
        movie_list = document.xpath("//div[@class='media-list-results contents']/div")

        # 3.遍历电影列表，获取电影详情

        for movie in movie_list:
            movie_urls = movie.xpath("./div/div/a/@href")

            if movie_urls:
                # 获取每个电影详细地址
                movie_info_url = TMDB_BASE_URL + movie_urls[0]
                # 发送请求，获取电影详细数据
                movie_info = get_movie_info(movie_info_url)
                all_movies.append(movie_info)

    #4.保存数据为csv文件
    save_all_movies(all_movies)
    print(f"保存电影数据为csv文件：{MOVIE_LIST_FILE}")

if __name__ == '__main__':
    main()




