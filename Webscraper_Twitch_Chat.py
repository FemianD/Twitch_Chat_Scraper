import json
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
inputElement = driver.find_element(By.XPATH,'(//input[@type="search"])[1]')
inputElement.send_keys(stream)
time.sleep(2)
search_results = []
searches = driver.find_elements_by_xpath("//a[@href]")
for search in searches:
    print(search.get_attribute("href"))
    search_results.append(search)
search_results[5].click()
time.sleep(2)

#Filter english tag
inputElement = driver.find_element(By.ID, "dropdown-search-input")
print(inputElement)
inputElement.send_keys("English")
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

for i in range(3):
    print("start collection")
    time.sleep(30)

    #Store data
    stream_data = driver.page_source

    #Extract divs
    soup = BeautifulSoup(stream_data, 'lxml')
    chats_selector = soup.find_all('div', class_='chat-line__message')
    channel_info = soup.find('div', class_='channel-info-content')

    #Extract time and viewer count
    stream_time = channel_info.find('span', class_=re.compile('live-time')).text
    chat_list.append(stream_time)
    #viewer_count = channel_info.find('p', class_=re.compile('"animated-channel-viewers-count"')).text
    #chat_list.append(viewer_count)

    #Extract chat outputs to list
    for chat_selector in chats_selector:
        chats = {}

        #ID
        id_span = chat_selector.find('span', class_=re.compile('chat-author__display-name')).text
        chats['Id'] = hash(id_span)

        #Message
        chat_span = chat_selector.find('span', class_='text-fragment')
        try:
            chats['Message'] = chat_selector.find('span', class_=re.compile('text-fragment')).text      
        except:
            chats['Message'] = "N/A"     
        
        #Badge(s)
        badge_list = []
        try:
            badge_divs = chat_selector.find_all('img', class_='chat-badge')
            for badge_div in badge_divs:
                badge = badge_div['alt']
                badge_list.append(badge)  
        except:
            chats['Badge(s)'] = "N/A"
        chats['Badge(s)'] = badge_list
        #Emote(s)
        emote_list = []
        try:
            emote_divs = chat_selector.find_all('img', class_='chat-image chat-line__message--emote')
            for emote_div in emote_divs:
                emote = emote_div['alt']
                emote_list.append(emote)
        
        except:
            emote_list.append("No emote")
        chats['Emote(s)'] = emote_list

        chat_list.append(chats)
    print(chat_list)
    print("1 minute loop is done!")

json = json.dumps(chat_list)
print(json)
print("Stream scraping is done!")

driver.close()
