from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
from typing import TypedDict, List
from pathlib import Path
import os

cwd = Path().resolve()
result_path = cwd.joinpath('result')

LOGIN_URL = "https://login.itb.ac.id/cas/login?service=https%3A%2F%2Fakademik.itb.ac.id%2Flogin%2FINA"
BASE_URL = "https://akademik.itb.ac.id"
USERNAME = ""  # NIM
PASSWORD = ""  # password


class Url(TypedDict):
    faculty: str
    code: str
    url: str


target = {
    "FMIPA": [101, 102, 103, 105, 108],
    "SITH": [104, 106, 112, 114, 115, 119],
    "SF": [107, 116],
    "FTTM": [121, 122, 123, 125],
    "FITB": [120, 128, 129, 151],
    "FTI": [130, 133, 134, 143, 144, 145],
    "STEI": [132, 135, 180, 181, 182, 183],
    "FTMD": [131, 136, 137],
    "FTSL": [150, 153, 155, 157, 158],
    "SAPPK": [152, 154],
    "FSRD": [170, 172, 173, 174, 175],
    "SBM": [190, 192]
}

URLS: List[Url] = []

for k, v in target.items():
    for code in v:
        URLS.append(Url(faculty=k, code=str(
            code), url=f"https://akademik.itb.ac.id/app/mahasiswa:{USERNAME}/kurikulum/struktur?fakultas={k}&prodi={code}&th_kur=2019"))

driver = webdriver.Chrome(service=ChromeService(
    ChromeDriverManager().install()))

print("LOGGING IN")

driver.get(LOGIN_URL)

username_input = driver.find_element(by=By.ID, value="username")
username_input.send_keys(USERNAME)

password_input = driver.find_element(by=By.ID, value="password")
password_input.send_keys(PASSWORD)

submit = driver.find_element(by=By.NAME, value="submit")
submit.click()

print("DONE LOGIN")

for url in URLS:
    driver.get(url["url"])

    path = result_path.joinpath(f"{url['faculty']}-{url['code']}")
    wpath = path.joinpath('wajib')
    ppath = path.joinpath('pilihan')

    if not os.path.exists(path):
        os.mkdir(path)

    if not os.path.exists(wpath):
        os.mkdir(wpath)

    if not os.path.exists(ppath):
        os.mkdir(ppath)

    with open(path.joinpath(f"{url['faculty']}-{url['code']}.html").__str__(),  "w", encoding="utf-8") as w:
        w.write(driver.page_source)

    wajib = driver.find_element(by=By.ID, value="wajib")
    wajib_elmts = wajib.find_elements(by=By.TAG_NAME, value="a")
    wajib_urls: set[str] = set()

    for el in wajib_elmts:
        link = el.get_attribute('href')
        if link is not None:
            wajib_urls.add(link)

    pilihan = driver.find_element(by=By.ID, value="pilihan")
    pilihan_elmts = pilihan.find_elements(by=By.TAG_NAME, value="a")
    pilihan_urls: set[str] = set()

    for el in pilihan_elmts:
        link = el.get_attribute('href')
        if link is not None:
            pilihan_urls.add(link)

    for wajib_url in wajib_urls:
        driver.get(wajib_url)
        subject_id = wajib_url.split('/')[-2]

        with open(path.joinpath(f"wajib/{subject_id}.html").__str__(), "w", encoding="utf-8") as w:
            w.write(driver.page_source)

    for pilihan_url in pilihan_urls:
        driver.get(pilihan_url)
        subject_id = pilihan_url.split('/')[-2]

        with open(path.joinpath(f"pilihan/{subject_id}.html").__str__(), "w", encoding="utf-8") as w:
            w.write(driver.page_source)
