# coding: utf-8
from languages import *
#FIXME with real spanish words
strs = {"SUBMITTED_BY": (u"SUBMITTED BY", u"SPANISH TEXT"), "SUBMITTED_TO": (u"SUBMITTED TO", u"DIRIGIDO A"), "TOPIC_OF": (u"TOPIC OF THE RESOLUTION", u"TEMA DE LA RESOLUCIÓN"), "ST": (u'st', u'a'), 'ARIZONA_MODEL_UNITED_NATIONS': (u"Arizona Model United Nations", u"Modelo de las Naciones Unidas de Arizona"), 'ANNUAL_CONFERENCE': (u"Annual Conference", u"Conferencia Anual"), 'DRAFT': (u'DRAFT', u'PREL')}
def get_str(name, lang):
    if lang == ENGLISH:
        return strs[name][0]
    if lang == SPANISH:
        return strs[name][1]
