"""
skill fairytalez
Copyright (C) 2018  Andreas Lorensen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import time

import requests
from bs4 import BeautifulSoup
from ovos_utils.parse import match_one
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill
from quebra_frases import sentence_tokenize


class Fairytalez(OVOSSkill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_reading = False

    @intent_handler('fairytalez.intent')
    def handle_fairytalez(self, message):
        if message.data.get("tale") is None:
            response = self.get_response('fairytalez', num_retries=0)
            if response is None:
                return
        else:
            response = message.data.get("tale")
        self.speak_dialog('let_me_think', data={"story": response})
        index = self.get_index("https://fairytalez.com/fairy-tales/")
        result = match_one(response, list(index.keys()))

        if result[1] < 0.8:
            self.speak_dialog('that_would_be', data={"story": result[0]}, wait=True)
            response = self.ask_yesno('is_it_that')
            if response != 'yes':
                self.speak_dialog('no_story')
                return
        self.speak_dialog('i_know_that', data={"story": result[0]}, wait=True)
        # self.log.info(result + " " + result[0])
        self.settings['story'] = result[0]
        self.tell_story(index.get(result[0]), 0)

    @intent_handler('continue.intent')
    def handle_continue(self, message):
        if self.settings.get('story') is None:
            self.speak_dialog('no_story_to_continue')
        else:
            story = self.settings.get('story')
            self.speak_dialog('continue', data={"story": story}, wait=True)
            index = self.get_index("https://fairytalez.com/fairy-tales/")
            self.tell_story(index.get(story),
                            self.settings.get('bookmark') - 1)

    def tell_story(self, url, bookmark):
        self.is_reading = True
        self.settings['bookmark'] = bookmark
        if bookmark == 0:
            title = self.get_title(url)
            author = self.get_author(url)
            self.speak_dialog('title_by_author',
                              data={
                                  'title': title,
                                  'author': author
                              }, wait=True)
        lines = self.get_story(url)
        for line in lines[bookmark:]:
            self.settings['bookmark'] += 1
            if self.is_reading is False:
                break

            for sentens in sentence_tokenize(line):
                if self.is_reading is False:
                    break
                else:
                    self.speak(sentens, wait=True)
        if self.is_reading is True:
            self.is_reading = False
            self.settings['bookmark'] = 0
            self.settings['story'] = None
            time.sleep(2)
            self.speak_dialog('from_fairytalez')

    def stop(self):
        self.log.info('stop is called')
        if self.is_reading is True:
            self.is_reading = False
            return True
        else:
            return False

    def get_soup(self, url):
        try:
            return BeautifulSoup(requests.get(url).text, "html.parser")
        except Exception as SockException:
            self.log.error(SockException)

    def get_story(self, url):
        soup = self.get_soup(url)
        lines = [
            a.text.strip() for a in soup.find(id="main").find_all("p")[1:]
        ]
        lines = [
            l for l in lines if not l.startswith("{") and not l.endswith("}")
        ]
        return lines

    def get_title(self, url):
        soup = self.get_soup(url)
        title = [a.text.strip() for a in soup.findAll("h1")][0]
        return title

    def get_author(self, url):
        soup = self.get_soup(url)
        author = [
            a.text.strip()
            for a in soup.findAll("div", {"class": "author-name"})
        ][0]
        return str(author).split("  ")[0]

    def get_index(self, url):
        soup = self.get_soup(url)
        index = {}
        for link in soup.find(id="main").find_all('a'):
            index.update({link.text[2:]: link.get("href")})
        return index
