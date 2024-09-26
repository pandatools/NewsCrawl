from DrissionPage import Chromium

tab = Chromium().latest_tab

# 访问网址
tab.get("https://linux.do/t/topic/5")
tab.wait.doc_loaded()
print(tab.response.text)
print(tab)