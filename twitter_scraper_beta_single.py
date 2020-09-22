from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementNotSelectableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

import logging
import traceback
import sys

import time

from chromedriver_path import *


def run_sel(query_name,url):
    '''
    url: the url to scrape
    '''

    try:

        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
        user_agent_rotator = UserAgent(sofware_names=software_names,operating_systems=operating_systems,limit=100)

        # set chrome_options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")

        chrome_path = chromedriver_path()

        driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)

        # get the site
        driver.get(url)


        driver.implicitly_wait(10)

        # try:
        #     WebDriverWait(driver, time_to_wait).until(
        #     EC.presence_of_element_located((By.CLASS_NAME,'_li')))
        # finally:

        driver.maximize_window()

        elements = driver.find_elements_by_css_selector('.css-901oao.css-16my406.r-1qd0xha.r-ad9z0x.r-bcqeeo.r-qvutc0')

        output_dict = {}

        store = []

        for i in elements:
            if (i.text != '') and ('@' in i.text):
                store.append(i.text)

        print(store)

        output_dict['query_name'] = query_name
        output_dict['handles_found'] = store

        output_dict['error_log'] = None

        # create dictionary with three lists

        driver.close()

    except ElementNotSelectableException:
        output_dict['error_log'] = "ElementNotSelectableException"
        output_dict['query_name'] = query_name
        output_dict['handles_found'] = None


    except (WebDriverException, KeyboardInterrupt, TimeoutException, NewConnectionError, MaxRetryError) as e:
        output_dict['error_log'] = "Error"

        output_dict['handles_found'] = None
        output_dict['query_name'] = query_name

    return(output_dict)


if __name__ == '__main__':
    query_name = '이낙연'
    url = 'https://twitter.com/search?q=국회의원%20'+query_name+'&src=typed_query&f=user'
    output = run_sel(query_name,url)
