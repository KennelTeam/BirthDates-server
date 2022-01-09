from selenium.webdriver.chrome.service import Service

service = Service(
    executable_path='/home/nebolax/chrome_driver/chromedriver',)
service.start()
print(service.service_url)
while True:
    pass
