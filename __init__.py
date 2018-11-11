from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.parse import match_one

import requests
from bs4 import BeautifulSoup


class Fairytalez(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('fairytalez.intent')
    def handle_fairytalez(self, message):
        response = self.get_response('fairytalez')
        self.speak_dialog('let_me_think', data={"story": response})
        index = self.get_index("https://fairytalez.com/fairy-tales/")
        result = match_one(response, list(index.keys()))

        if result[1] < 0.8:
            self.speak_dialog('that_would_be', data={"story": result[0]})
            response = self.ask_yesno('is_it')
            if not response:
                self.speak_dialog('no_story')
                return
        self.speak_dialog('i_know_that', data={"story": result[0]})
        # self.log.info(result + " " + result[0])
        self.settings['story'] = result[0]
        self.tell_story(index.get(result[0]), 0)

    @intent_file_handler('continue.intent')
    def handle_continue(self, message):
        if self.settings.get('story') is None:
            self.speak_dialog('no_story_to_continue')
        else:
            story = self.settings.get('story')
            self.speak_dialog('continue', data={"story": story})
            index = self.get_index("https://fairytalez.com/fairy-tales/")
            self.tell_story(index.get(story), self.settings.get('bookmark'))

    def tell_story(self, url, bookmark):
        self.is_reading = True
        self.settings['bookmark'] = bookmark
        lines = self.get_story(url)
        for line in lines[bookmark:]:
            if not self.is_reading:
                return
            self.speak(line, wait=True)
            self.settings['bookmark'] += 1
        self.is_reading = False
        self.settings['bookmark'] = 0
        self.settings['story'] = None

    def stop(self):
        if self.is_reading:
            self.is_reading = False
            return True

    def get_soup(self, url):
        try:
            return BeautifulSoup(requests.get(url).text, "html.parser")
        except Exception as SockException:
            self.log.error(SockException)

    def get_story(self, url):
        soup = self.get_soup(url)
        lines = [a.text.strip() for a in soup.find(id="main").find_all("p")[1:]]
        lines = [l for l in lines if not l.startswith("{") and not l.endswith("}")]
        return lines

    def get_index(self, url):
        soup = self.get_soup(url)
        index = {}
        for link in soup.find(id="main").find_all('a'):
            index.update({link.text[2:]: link.get("href")})
        return index


def create_skill():
    return Fairytalez()
