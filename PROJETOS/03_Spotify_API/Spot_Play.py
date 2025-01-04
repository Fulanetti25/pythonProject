from selenium import webdriver
import time, sys
spot_url = sys.argv[1]
driver = webdriver.Chrome()
driver.get(spot_url)
time.sleep(10)
driver.close()