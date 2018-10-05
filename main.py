import numpy as np
import cv2
import win32gui
import os
import time

import trivia
import util

PHONE_START_X = 900
PHONE_START_Y = 200
PHONE_HEIGHT = 880
PHONE_WIDTH = 580

HQ_PATH = '''
    C:/"Program Files"/BlueStacks/HD-RunApp.exe 
    -json "{""app_icon_url"": """", ""app_name"": ""HQ"", ""app_url"": """", ""app_pkg"": ""com.intermedia.hq""}"
'''

# SCREEN CONSTANTS
MAXIMIZE = (961, 59)
TOP_LEFT = (602, 150)
WIDTH = 400
HEIGHT = 500

"""
Handles a question
"""
def handle_question():
    image = util.take_screenshot()
    image = image[
        TOP_LEFT[1] : TOP_LEFT[1] + HEIGHT,
        TOP_LEFT[0] : TOP_LEFT[0] + WIDTH 
    ]
    """
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    """
    text = util.image_to_text(image)
    parsed = util.parse_text(text)
    
    if parsed is not None:
        quest, options = parsed
        qt = trivia.TriviaQuestion(quest, options)
        answer_index = qt.answer()
        
        util.do_click((800, 315 + answer_index * 60))
    


def main():
    """
    titles = [name for name in util.get_titles() if name != ""]
    print(titles)
    for title in titles:
        try:
            util.move_window((0,0, PHONE_HEIGHT, PHONE_WIDTH), title)
        except:
            pass
    #util.move_window((0,0, PHONE_HEIGHT, PHONE_WIDTH), "HQ")
    """
    
    util.track_position()
    
    os.system(HQ_PATH)
    time.sleep(30)
    util.do_click(MAXIMIZE)
    
    while True:
        # wait for question
        while True:
            if util.question_picture(util.take_screenshot()):
                break
            print("No picture found")
            time.sleep(1)
        
        
        # answer question
        handle_question()
        time.sleep(5)
    
    
    
    
    
if __name__ == "__main__":
    main()