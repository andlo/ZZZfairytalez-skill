from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.parse import match_one

import requests
from bs4 import BeautifulSoup
import sys


class Fairytalez(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('fairytalez.intent')
    def handle_fairytalez(self, message):
        response = self.get_response('fairytalez')
        self.speak_dialog('let_me_think', data={"story":response})
        index = self.get_index("https://fairytalez.com/fairy-tales/")
        result = match_one(response, list(index.keys()))
        if result[1] < 0.8:
            self.speak_dialog('that_would_be', data={"story":result[0]})
        else:
            self.speak_dialog('i_know_that', data={"story":result[0]})
        
        self.log.info(result)
        self.log.info(index.get(result[0]))
        self.tell_story(index.get(result[0]))

    def tell_story(self, url):
        self.is_reading = True
        lines = self.get_story(url) 
        for line in lines:
            if self.is_reading == False:
                break
            self.speak(line, wait=True)
        self.is_reading = False

    def stop(self):
        self.is_reading = False

    def get_soup(url):
        try:
            return BeautifulSoup(requests.get(url).text,"html.parser")
        except Exception as SockException:
            print(SockException)

    def get_story(self, url):
        soup = BeautifulSoup(requests.get(url).text,"html.parser")
        # ignore first entry, its just garbage
        # Already a member? Sign in. Or Create a free Fairytalez account in less than a minute.
        lines = [a.text.strip() for a in soup.find(id="main").find_all("p")[1:]]
        # you might want to also remove {Note: You can read an illustrated version of this story, plus other mermaid tales, in our collection Mermaid Tales: The Little Mermaid and 14 Other Illustrated Mermaid Stories, now available for Amazon Kindle.}
        # i just checked if line starts and ends with { , this may depend on the
        #  story so using the index is bad idea, but filtering everything
        # betwene {} should be safe
        lines = [l for l in lines if not l.startswith("{") and not l.endswith("}")]
        return lines

    def get_index(self, url):
        soup = BeautifulSoup(requests.get(url).text,"html.parser")
        index = {}
        for link in soup.find(id="main").find_all('a'):
            #index.append([link.text[2:], link.get("href")])
            index.update({link.text[2:] : link.get("href")})
        return index

def create_skill():
    return Fairytalez()



