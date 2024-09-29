from DrissionPage._base.chromium import Chromium
from DrissionPage._configs.chromium_options import ChromiumOptions

from config import dy_settings


def create_chrome():
    co = ChromiumOptions()
    if not dy_settings.show_chrome:
        co.incognito()
        co.headless()
        co.set_argument('--no-sandbox')
        co.set_argument('--headless=new')
        return Chromium(co)
    else:
        return Chromium()