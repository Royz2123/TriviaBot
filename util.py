import cv2
from matplotlib import pyplot as plt
import numpy as np
from PIL import ImageGrab
from PIL import Image
import pytesseract
import win32gui
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
import re

import time
import os
import ctypes

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/10.0'
headers = {'User-Agent': user_agent}
google_url = "https://www.google.com/search?q="
yahoo_url = "https://search.yahoo.com/search?p="
queries = 0


"""
Parse text into question and options
"""
def parse_text(text):
    quest, options = tuple(text.split("?", 1))
    options = options.split("\n")
        
    # Edit options and question
    options = [option for option in options if option != ""][:3]
    quest = quest.replace("\n", " ")
    
    return quest, options

"""
Most common element in a list
"""
def most_common(lst):
    return max(set(lst), key=lst.count)


"""
Create a query to google
"""
def google_query(text):
    q = urllib.parse.quote(text)
    query = ''.join([google_url, q])
    return query

"""
Get html response
"""
def get_response(query):
    # count queries sent
    global queries
    queries += 1
    print("Total queries: ", str(queries))

    # print(query)
    req = urllib.request.Request(query, headers=headers)
    response = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(response, 'html.parser')
    # removes all script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text().lower()
       
    
    
"""
Get titles of all the windows on the screen
"""
def get_titles():
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible
     
    titles = []
    def foreach_window(hwnd, lParam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            titles.append(buff.value)
        return True
    EnumWindows(EnumWindowsProc(foreach_window), 0)
     
    return titles

"""
A simple screen grabbing utility
"""
def take_screenshot():
    image = ImageGrab.grab()
    #np_image = image.convert('RGB')
    np_image = np.array(image)
    
    # save image for later use
    image.save("screenshots/screen_capture.jpg", "JPEG")
    image.save("screen_capture.jpg", "JPEG")

    # return image
    return np_image
    

"""
Image to test
"""
def image_to_text(image):
    # load the example image and convert it to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
     
    # check to see if we should apply thresholding to preprocess the
    # image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
     
    # make a check to see if median blurring should be done to remove
    # noise
    gray = cv2.medianBlur(gray, 3)
     
    # apply OCR to it
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, gray)
    text = pytesseract.image_to_string(Image.open(filename)) 
    os.remove(filename)
    
    # return text
    return text
    
    
"""
Move a window to pos. Not working with all windows for some reason
"""
def move_window(pos, wnd_name):
    wnd = win32gui.FindWindow(wnd_name, None)
    print(wnd)
    
    if len(pos) == 4:
        win32gui.MoveWindow(wnd, pos[0], pos[1], pos[2], pos[3], 1)
    if len(pos) == 2:
        win_size = wnd.get_bbox_size()
        win32gui.MoveWindow(wnd,pos[0],pos[1],win_size[0],win_size[1], 1)
    