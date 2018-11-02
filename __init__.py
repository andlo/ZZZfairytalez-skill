from mycroft import MycroftSkill, intent_file_handler
import requests
from bs4 import BeautifulSoup
import sys


class Fairytalez(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('fairytalez.intent')
    def handle_fairytalez(self, message):
        #self.speak_dialog('fairytalez')
        self.is_reading = True
        lines = get_story(self) 
        for line in lines:
            if self.is_reading == False:
                break
            wait_while_speaking()
            self.speak(line)
        self.is_reading = False

    def stop(self):
        self.is_reading = False

    def get_soup(url):
        try:
            return BeautifulSoup(requests.get(url).text,"html.parser")
        except Exception as SockException:
            print(SockException)
            sys.exit(1)
    
    def get_story(self):
        self.url = "https://fairytalez.com/the-little-mermaid/"
        self.url+=type+".html"
        soup = get_soup(self.url)
        lines = "".join([i.text for i in soup.select("#main > article > section > p")])
        return lines
    


    

def create_skill():
    return Fairytalez()



