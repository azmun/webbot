from languages import *
#FIXME with real spanish words
str = {"SUBMITTED_BY": ("SUBMITTED BY", "SPANISH TEXT"), "SUBMITTED_TO": ("SUBMITTED TO", "DIRIGIDO A"), "TOPIC_OF": ("TOPIC OF THE RESOLUTION", "TEMA DE LA RESOLUCIÓN"), "ST": ('st', 'a'), 'ARIZONA_MODEL_UNITED_NATIONS': ("Arizona Model United Nations", "Modelo de las Naciones Unidas de Arizona"), 'ANNUAL_CONFERENCE': ("Annual Conference", "Conferencia Anual")}
def get_str(name, lang):
    if lang == ENGLISH:
        return strs[name][0]
    if lang == SPANISH:
        return strs[name][1]
