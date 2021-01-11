from selenium import webdriver

BASE_URL = 'https://www.google.com/maps'

def getChromeDriver(options):
    return webdriver.Chrome('./chromedriver', chrome_options=options)

def getChromeOptions():
    return webdriver.ChromeOptions()

def setIgnoreCertificateError(options):
    options.add_argument('--ignore-certificate-error')

def setBrowserIncognito(options):
    options.add_argument('--incognito')

def setHeadless(options):
    options.add_argument('--headless')