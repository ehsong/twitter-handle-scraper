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

from tqdm import tqdm
import pandas as pd

from timesc import *
import json

from multiprocessing.dummy import Pool
from multiprocessing import cpu_count

import numpy as np


def run_sel(member_dict): # need row_id to push
    '''
    url: the url to scrape
    '''

    delays = [7, 4, 6, 2, 10, 13]

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

        # url
        url = 'https://twitter.com/search?q=국회의원%20'+member_dict['member']+'&src=typed_query&f=user'
        print('Querying handle of '+member_dict['member']+'..')

        # get the site
        driver.get(url)

        driver.implicitly_wait(10)

        # try:
        #     WebDriverWait(driver, time_to_wait).until(
        #     EC.presence_of_element_located((By.CLASS_NAME,'_li')))
        # finally:

        driver.maximize_window()

        elements = driver.find_elements_by_css_selector('.css-901oao.css-16my406.r-1qd0xha.r-ad9z0x.r-bcqeeo.r-qvutc0')

        # output_dict = {}

        store = []

        for i in elements:
            if i.text != '':
                store.append(i.text)

        handles = []

        for item in store:
            if '@' in item:
                handles.append(item)

        remove = ['Log in', 'Sign up', 'Top', 'Latest', 'People', 'Photos', 'Videos', 'People', 'Follow']
        store_cleaned = [i for i in store if i not in remove]

        des = []

        for item in store_cleaned:
            if '@' in item:
                pos_1 = store_cleaned.index(item)
                try:
                    des.append(store_cleaned[pos_1+1])
                except IndexError:
                    des.append('')

        # member_dict['query_name'] = query_name
        member_dict['handles_found'] = handles
        member_dict['profile_text'] = des

        member_dict['error_log'] = None

        # create dictionary with three lists

        driver.close()

    except ElementNotSelectableException:
        member_dict['error_log'] = "ElementNotSelectableException"
        # member_dict['query_name'] = query_name
        member_dict['handles_found'] = None
        member_dict['profile_text'] = None


    except (WebDriverException, KeyboardInterrupt, TimeoutException) as e:
        member_dict['error_log'] = "Error"

        member_dict['handles_found'] = None
        # member_dict['query_name'] = query_name
        member_dict['profile_text'] = None

    delay = np.random.choice(delays)
    time.sleep(delay)

    return(member_dict)


if __name__ == '__main__':
    def open_json(filename):
        with open(filename) as f:
            output = json.load(f)
        return(output)

    member_dict_list = open_json("21st_congress_names.json")

    # use multiprocessing to iterate
    n = cpu_count()-1
    with Pool(n) as p:
        results = p.map(run_sel,member_dict_list)

    df = pd.DataFrame(results)
    print(df.head())
