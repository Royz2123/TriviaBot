import numpy as np
import cv2
import win32gui

import trivia
import util

PHONE_START_X = 900
PHONE_START_Y = 200
PHONE_HEIGHT = 880
PHONE_WIDTH = 580

def main():
    """"
    titles = [name for name in util.get_titles() if name != ""]
    print(titles)
    util.move_window((0,0, PHONE_HEIGHT, PHONE_WIDTH), "Notepad++")
    """
    
    image = util.take_screenshot()
    image = image[
        PHONE_START_Y : PHONE_START_Y + PHONE_HEIGHT, 
        PHONE_START_X : PHONE_START_X + PHONE_WIDTH
    ]
    
   
    cv2.imshow("Image", image)
    cv2.waitKey(0)
     
    
    text = util.image_to_text(image)
    quest, options = util.parse_text(text)
    qt = trivia.TriviaQuestion(quest, options)
    qt.answer()
    
    
def print_windows():
    win32gui.EnumWindows(callback, extra)
    
    
    
if __name__ == "__main__":
    main()