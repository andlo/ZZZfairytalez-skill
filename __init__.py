from mycroft import MycroftSkill, intent_file_handler


class Fairytalez(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('fairytalez.intent')
    def handle_fairytalez(self, message):
        self.speak_dialog('fairytalez')


def create_skill():
    return Fairytalez()

