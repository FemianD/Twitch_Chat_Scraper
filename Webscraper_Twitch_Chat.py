from email import message
import json
from threading import local
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import re
import time

#Lets start! What do you want to scrape?
stream = input("Which game do you want to scrape?" )

#driver = webdriver.Chrome()
s=Service('C:\Program Files (x86)\chromedriver.exe')
driver = webdriver.Chrome(service=s)
driver.get("https://www.twitch.tv/")

#Going to your game or stream!
page_load = WebDriverWait(driver, 15).until(
EC.presence_of_element_located((By.CLASS_NAME, 'common-centered-column'))
)
time.sleep(2)
input_search = driver.find_element(By.XPATH,'(//input[@type="search"])[1]')
input_search.send_keys(stream)
time.sleep(2)

#search_button = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/nav/div/div[2]/div/div/div/div/div[1]/div/button/div/div')
#search_button.click()

all_search_results = []
result_links = driver.find_elements_by_xpath("//a[@href]")
print(result_links)
for links in result_links:
    print(links.get_attribute("href"))
    all_search_results.append(links)
time.sleep(2)

all_search_results[6].click()
time.sleep(2)
#Filter english tag
filter = driver.find_element(By.ID, "dropdown-search-input")
print(filter)
filter.send_keys("English")
time.sleep(2)
tags=[]
tag_content = driver.find_elements(By.CLASS_NAME, "simplebar-content")
for tag in tag_content:
    tags.append(tag)
tags[2].click()
time.sleep(2)

#Click on stream
links = []
elems = driver.find_elements_by_xpath("//a[@href]")
for elem in elems:
    print(elem.get_attribute("href"))
    links.append(elem)

links[24].click()

#Make sure chat is loaded in - wait for enough messages with time.sleep
page_load = WebDriverWait(driver, 30).until(
EC.presence_of_element_located((By.CLASS_NAME, 'chat-line__message'))
)
chat_list = []
messages = {}

for i in range(2):
    print("start collection")
    time.sleep(10)
    stream_time_dict = {}
    #Store data
    stream_data = driver.page_source
    #Extract divs
    soup = BeautifulSoup(stream_data, 'lxml')
    chats_selector = soup.find_all('div', class_='chat-line__message')
    channel_info = soup.find('div', class_='channel-info-content')

    #Extract time and viewer count
    stream_time = channel_info.find('span', class_=re.compile('live-time')).text
    stream_time_dict['stream_time'] = stream_time
    chat_list.append(stream_time_dict)
    #viewer_count = channel_info.find('p', class_=re.compile('"animated-channel-viewers-count"')).text
    #chat_list.append(viewer_count)
    
    #Extract chat outputs to list
    for chat_selector in chats_selector:
        chats = {}
        #ID
        id_span = chat_selector.find('span', class_=re.compile('chat-author__display-name')).text
        chats['id'] = hash(id_span)

        #Message
        chat_span = chat_selector.find('span', class_='text-fragment')
        try:
            chats['message'] = chat_selector.find('span', class_=re.compile('text-fragment')).text      
        except:
            chats['message'] = "N/A"     

        #Badge(s)
        badge_list = []
        try:
            badge_divs = chat_selector.find_all('img', class_='chat-badge')
            for badge_div in badge_divs:
                badge = badge_div['alt']
                badge_list.append(badge)  
            chats['badge(s)'] = badge_list
        except:
            chats['badge(s)'] = "N/A"
        #Emote(s)
        emote_list = []
        try:
            emote_divs = chat_selector.find_all('img', class_='chat-image chat-line__message--emote')
            for emote_div in emote_divs:
                emote = emote_div['alt']
                emote_list.append(emote)
        except:
            emote_list.append("No emote")
        
        chats['emote(s)'] = emote_list
        chat_list.append(chats)
        messages['messages'] = chat_list
    print("1 minute loop is done!")

json = json.dumps(messages, indent=4)
print(json)
print("Stream scraping is done!")

driver.close()
