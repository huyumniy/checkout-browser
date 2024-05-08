import undetected_chromedriver as webdriver
import os
import ast
from urllib.parse import urlparse
import eel
import tempfile
import shutil
from selenium.webdriver.common.by import By
import undetected_chromedriver as webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class ProxyExtension:
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {"scripts": ["background.js"]},
        "minimum_chrome_version": "76.0.0"
    }
    """

    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: %d
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        { urls: ["<all_urls>"] },
        ['blocking']
    );
    """

    def __init__(self, host, port, user, password):
        self._dir = os.path.normpath(tempfile.mkdtemp())

        manifest_file = os.path.join(self._dir, "manifest.json")
        with open(manifest_file, mode="w") as f:
            f.write(self.manifest_json)

        background_js = self.background_js % (host, port, user, password)
        background_file = os.path.join(self._dir, "background.js")
        with open(background_file, mode="w") as f:
            f.write(background_js)

    @property
    def directory(self):
        return self._dir

    def __del__(self):
        shutil.rmtree(self._dir)


def selenium_connect(link, proxy='', user_agent='', cookie_string=''):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    #options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-site-isolation-trials")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--lang=EN')
    print(user_agent)
    if user_agent: options.add_argument(f'--user-agent={user_agent}')
    cwd= os.getcwd()
    extension = cwd + "/uBlock-Origin"
    print(extension)
    if proxy:
        proxy = proxy.split(":", 3)
        proxy[1] = int(proxy[1])
        print(proxy)
        proxy_extension = ProxyExtension(*proxy)
        options.add_argument(f"--load-extension={proxy_extension.directory},{extension}")
    else: options.add_argument(f"--load-extension={extension}")

    prefs = {"credentials_enable_service": False,
        "profile.password_manager_enabled": False}
    options.add_experimental_option("prefs", prefs)
    try:
        driver = webdriver.Chrome(
            options=options,
            enable_cdp_events=True
        )
    except: driver.quit()
    
    # Convert cookie string to dictionary
    if cookie_string:
        parsed_url = urlparse(link)
        cookie_string = ast.literal_eval(cookie_string)
        main_domain = parsed_url.scheme + "://" + cookie_string[0]['domain'].split('.', 1)[1]
        print(main_domain)
        driver.get(main_domain)
        
        for cookie in cookie_string:
            print(cookie)
            driver.add_cookie(cookie)

    return driver

def read_file():
    file_path = os.path.join(os.getcwd(), 'info.txt')
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    data = {}
    for line in lines:
        label, value = line.strip().split(':: ')
        data[label] = value
    return data


def check_for_element(driver, selector, click=False, xpath=False):
    try:
        if xpath:
            element = driver.find_element(By.XPATH, selector)
        else:
            element = driver.find_element(By.CSS_SELECTOR, selector)
        if click: 
            driver.execute_script("arguments[0].scrollIntoView();", element)
            element.click()
        return element
    except: return False


@eel.expose
def main(user_agent, cookies, link, proxy):
    driver = selenium_connect(link, proxy, user_agent, cookies)
    driver.get(link)
    try:
        check_for_element(driver, "//button[contains(@class, 'sc-aitciz-1') and contains(@class, 'hWHZkc')][2]", xpath=True, click=True)
    except: print("did not manage to click on 'Find seats for me'")
    input('Enter to quit()')
    driver.quit()

if __name__ == '__main__':
    # data = read_file()
    eel.init('front')
    eel.start('main.html', size=(600, 800))
   