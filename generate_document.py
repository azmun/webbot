from localization import get_str
from google.appengine.ext.webapp import template
from roman import toRoman
import string 
import pdb
from languages import *



def get_op_separator(ops, index):
    assert(index < len(ops) and index >= 0)
    if index == len(ops) - 1:
        return u'.'
    if ops[index + 1]["level"] > ops[index]["level"]:
        return u':'
    return u';'

def get_level_index(lvl, indx):
    if lvl % 3 == 0:
        return u'%d' % indx
    if lvl % 3 == 1:
        return [u'', u'a', u'b', u'c', u'd', u'e', u'f', u'g', u'h', u'j', u'k', u'l', u'm', u'n', u'o', u'p', u'q', u'r', u's', u't', u'v', u'w', u'x', u'y', u'z'][indx]
    if lvl % 3 == 2:
        return toRoman(indx, False)

def generate_document(res, lang, topic_name, committee_salutation_name, committee_abbr, res_index, topic_index, isDraft, sponsors):
    salutation = u'<text:p text:style-name="preams"><text:span text:style-name="clause_keyword">%s,</text:span></text:p>' % committee_salutation_name
    preams_outline = string.join([u'<text:p text:style-name="preams"><text:span text:style-name="clause_keyword">%s </text:span><text:span text:style-name="clause_body">%s,</text:span></text:p>' % (clause["keyword"], clause["content"]) for clause in res["preambulars"]], u'\n')
    max_level = -1
    last_level = -1
    current_indices = []
    ops = []
    for idx, clause in enumerate(res["operatives"]):
        for i in range(len(current_indices), clause["level"] + 1):
            current_indices.append(1)
        if last_level > clause["level"]:
            current_indices = current_indices[:clause["level"] + 1]
            current_indices[clause["level"]] += 1
        elif last_level == clause["level"]:
            current_indices[clause["level"]] += 1
        last_level = clause["level"]
        if last_level > max_level:
            max_level = last_level
        index = current_indices[last_level]
        if clause["level"] == 0:
            ops.append(u'<text:p text:style-name="ops-%d">%s. <text:span text:style-name="clause_keyword">%s </text:span><text:span text:style-name="clause_body">%s%s</text:span></text:p>' % (clause["level"], get_level_index(clause["level"], index), clause["keyword"], clause["content"], get_op_separator(res["operatives"], idx)))
        else:
            ops.append(u'<text:p text:style-name="ops-%d">%s. <text:span text:style-name="clause_body">%s%s</text:span></text:p>' % (clause["level"], get_level_index(clause["level"], index), clause["content"], get_op_separator(res["operatives"], idx)))

    ops_outline = string.join(ops, u'\n')
    styles = u'<style:style style:family="text" style:name="clause_keyword"><style:text-properties fo:font-style="italic" style:font-name-complex="Times New Roman"/></style:style>\n<style:style style:family="text" style:name="clause_body"><style:text-properties fo:font-style="normal" style:font-name-complex="Times New Roman"/></style:style>\n<style:style style:family="paragraph" style:name="preams"><style:paragraph-properties fo:margin-left="0.5in" fo:margin-bottom="0.14in"/></style:style>'
    styles += string.join([u'<style:style style:family="paragraph" style:name="ops-%d"><style:paragraph-properties fo:margin-left="%fin" fo:margin-bottom="0.14in"/></style:style>' % (idx, 0.5 * (idx + 1)) for idx in range(max_level + 1)], u'\n')
    if lang == ENGLISH:
        sponsors = [{"name": s["englishName"], "longName": s["englishLongName"]} for s in sponsors]
    elif lang == SPANISH:
        sponsors = [{"name": s["spanishName"], "longName": s["spanishLongName"]} for s in sponsors]
#FIXME: need two separate names for sponsors (one for sort order and one for full name) ???
    names = [s["longName"] for s in sorted(sponsors, key=lambda d: d["name"])]
    countries = string.join(names, ', ')
    tagline = u'%s/%s/%s%d' % (committee_abbr, toRoman(topic_index, True), get_str('DRAFT', lang) if isDraft else u'', res_index)
    templateValues = {
        'styles': styles,
        'azmun': get_str('ARIZONA_MODEL_UNITED_NATIONS', lang),
        'st': get_str('ST', lang),
        'annual_conference': get_str('ANNUAL_CONFERENCE', lang),
        'tagline': tagline,
        'subj_of': get_str('TOPIC_OF', lang),
        'sub_to': get_str('SUBMITTED_TO', lang),
        'sub_by': get_str('SUBMITTED_BY', lang),
        'outline': u'%s\n%s\n%s' % (salutation, preams_outline, ops_outline),
        'topic': topic_name,
        'committee': committee_salutation_name,
        'countries': countries
        }
    return template.render('2013/template.fodt', templateValues)

