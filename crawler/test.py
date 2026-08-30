import requests
from lxml import html

#定义url
target_url = "https://www.tiobe.com/tiobe-index/"

#发送请求,获取数据
response = requests.get(target_url)

document = html.fromstring(response.text)

th_list = document.xpath("//*[@id='top20']/thead/tr/th/text()")
print(th_list)

tr_list = document.xpath("//*[@id='top20']/tbody/tr")
for tr in tr_list:
    td_list = tr.xpath("./td/text()")
    print(td_list)
