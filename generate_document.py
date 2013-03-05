from localization import get_str
import string 

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
        return lower_roman(indx)



def generate_document(res, lang, topic_name, committee_name):
    preams_outline = string.join([u'<text:p text:style-name="preams"><text:span text:style-name="clause_keyword">%s </text:span><text:span text:style-name="clause_body">%s,</text:span></text:p>' % (clause["keyword"], clause["content"]) for clause in res["preambulars"]], u'\n')
    max_level = -1
    last_level = -1
    current_indices = []
    ops = []
    for idx, clause in enumerate(res["operatives"]):
        for i in range(len(current_indices), clause["level"] + 1):
            current_indices.append(0)
        if last_level > clause["level"]:
            current_indices = current_indices[:clause["level"] + 1]
        elif last_level == clause["level"]:
            ++current_indices[clause["level"]]
        last_level = clause["level"]
        if last_level > max_level:
            max_level = last_level
        index = current_indices[last_level]
        if "keyword" in clause:
            ops.append(u'<text:p text:style-name="ops-%d">%s. <text:span text:style-name="clause_keyword">%s </text:span><text:span text:style-name="clause_body">%s%s</text:span></text:p>' % (clause["level"], get_level_index(clause["level"], index), clause["keyword"], clause["content"], get_op_separator(res["operatives"], idx)))
    ops_outline = string.join(ops, u'\n')
    styles = u'<style:style style:family="text" style:name="clause_keyword"><style:text-properties fo:font-style="italic" style:font-name-complex="Times New Roman"/></style:style>\n<style:style style:family="text" style:name="clause_body"><style:text-properties fo:font-style:"normal" style:font-name-complex="Times New Roman"</style>\n<style style:family="paragraph" style:name="preams"><style:paragraph-properties fo:margin-left="0.5in" fo:margin-bottom="0.14in"/></style>'
    styles += strings.join([u'<style:style style:family="paragraph" style:name="ops-%d"><style:paragraph-properties fo:margin-left="%fin" fo:margin-bottom="0.14in"/></style>'], u'\n')
#FIXME: need two separate names for sponsors (one for sort order and one for full name) ???
    countries = string.join(res["sponsors"], ', ')

