import time

from DrissionPage import Chromium
import feapder
tab = Chromium().latest_tab
def crawl_html(html):
    feapder_html = feapder.Response.from_text(text=html, url="", cookies={}, headers={})
    crawl_list = feapder_html.xpath('//div[@class="cell el-tooltip"]/text()').extract()
    crawl_list = [i.strip() for i in crawl_list if i.strip() != '']
    return crawl_list

tab.get("http://lyybj.linyi.gov.cn:7777/hallEnter/#/search/Supplies")
tab.wait.doc_loaded()
name = tab.ele('@placeholder=请输入耗材名称')
name.input('%')
find = tab.ele('@text()=查询')
find.click()
time.sleep(16)
html = tab.html
crawl_list = crawl_html(html)
print(crawl_list)
for i in range(5):
    print(f"第{i+2}页")
    next = tab.ele('.btn-next')
    next.click()
    time.sleep(16)
    html = tab.html
    crawl_list = crawl_html(html)
    print(crawl_list)