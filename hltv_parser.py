import datetime
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver as WebDriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import config
from domain.match import Match
from domain.team import Team
from domain.match_stars import MatchStars

# delays in sec with weight
DELAYS = {
    1: 13,
    2: 19,
    3: 25,
    5: 35,
    8: 45,
    13: 60,
    21: 60,
    34: 55,
    55: 45,
    89: 40,
    144: 35,
    233: 30,  # 11
    377: 20,
    610: 16,
    987: 14,
    1597: 12,
    2584: 10,
    4181: 6,  # 17
    6765: 4,
    10946: 2,
    17711: 1
}
DELAYS_MSEC = [delay / 1000 for delay, _ in DELAYS.items()]
DELAYS_MSEC_WEIGHTS = list(DELAYS.values())

# we don't need low delays in case when there is no page loading
DELAYS_SAME_PAGE = {delay: DELAYS[delay] for delay, weight in DELAYS.items() if 100 < delay < 2000}
DELAYS_SAME_PAGE_MSEC = [delay / 1000 for delay, _ in DELAYS_SAME_PAGE.items()]
DELAYS_SAME_PAGE_MSEC_WEIGHTS = list(DELAYS_SAME_PAGE.values())


def delay():
    # time_to_sleep = random.choices(DELAYS_MSEC, DELAYS_MSEC_WEIGHTS, k=1)[0]
    # time.sleep(time_to_sleep)
    pass


def delay_same_page():
    # time_to_sleep = random.choices(DELAYS_SAME_PAGE_MSEC, DELAYS_SAME_PAGE_MSEC_WEIGHTS, k=1)[0]
    # time.sleep(time_to_sleep)
    pass


def goto(driver, url: str):
    delay()
    driver.get(url)


def create_driver() -> WebDriver:
    # proxy = get_random_proxy()

    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'eager'
    # options.add_argument(f'--proxy-server={proxy}')
    # options.headless = True

    # print(f"INFO creating webdriver with proxy '{get_random_proxy()}'...")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_window_size(1024, 768)

    return driver


def close_driver(driver):
    driver.close()


def get_upcoming_matches(driver: WebDriver = None) -> List[Match]:
    # cur_driver = driver if driver else create_driver()
    cur_driver = create_driver()

    out = list()

    cur_driver.get(config.BASE_URL)

    match_elem_list = cur_driver.find_elements(By.XPATH, "//h1[contains(@class, 'todaysMatches')]/following-sibling::div/a")

    # parse each match
    for match_elem in match_elem_list:
        team1_elem = match_elem.find_element(By.XPATH, ".//div[@class='teamrow'][1]/span")
        team2_elem = match_elem.find_element(By.XPATH, ".//div[@class='teamrow'][2]/span")

        div_elem = match_elem.find_element(By.XPATH, ".//div")
        stars_count = int(div_elem.get_attribute('stars'))

        try:
            time_elem = match_elem.find_element(By.XPATH, ".//div/div[@class='middleExtra']")
        except NoSuchElementException:
            # match already in progress
            continue

        # time is stored in microseconds
        time_utc = int(time_elem.get_attribute('data-unix')) / 1000

        match_url = match_elem.get_attribute('href')

        out.append(Match(Team(team1_elem.text), Team(team2_elem.text),
                         datetime.datetime.fromtimestamp(time_utc),
                         match_url))

    # was created at the beginning of the function, so clean-up for ourselves
    # if driver is None:
    #     close_driver(cur_driver)

    return out

    # return [Match(Team('Navi'), Team('NiP'), datetime.datetime.utcnow(), Stars.ONE),
    #         Match(Team('Navi'), Team('NiP'), datetime.datetime.utcnow(), Stars.ONE)]
