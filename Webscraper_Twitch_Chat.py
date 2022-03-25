from email import message
import json
from pickletools import read_int4
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

stream_cat = stream + " Category"
print(stream)

links = []
elems = driver.find_elements_by_xpath("//a[@href]")
for elem in elems:
    pair = {}
    pair['link'] = elem.get_attribute("href")
    pair['name'] = elem.get_attribute("aria-label")
    links.append(pair)
correct_link_dict = (next(x for x in links if x["name"] == (stream_cat)))
correct_link = correct_link_dict.get('link')
print(correct_link)
#Go to your category
driver.get(correct_link)
page_load = WebDriverWait(driver, 15).until(
EC.presence_of_element_located((By.ID, "dropdown-search-input"))
)

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
stream_links = driver.find_elements_by_xpath("//a[@href]")
for streams in stream_links:
    streams.get_attribute("href")
    links.append(streams)

links[24].click()

4#Make sure chat is loaded in - wait for enough messages with time.sleep
page_load = WebDriverWait(driver, 30).until(
EC.presence_of_element_located((By.CLASS_NAME, 'chat-line__message'))
)
chat_list = []
messages = {}

for i in range(2):
    print("start collection")
    time.sleep(10)
    #Store data
    stream_data = driver.page_source
    #Extract divs
    soup = BeautifulSoup(stream_data, 'lxml')
    chats_selector = soup.find_all('div', class_='chat-line__message')
    channel_info = soup.find('div', class_='channel-info-content')

    #Extract time and viewer count
    stream_time = channel_info.find('span', class_=re.compile('live-time')).text
    chat_list.append(stream_time)
    
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

with open("twitch_chat_json", "w") as outfile:
    outfile.write(json)


driver.close()
