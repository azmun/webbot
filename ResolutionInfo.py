import collections
from roman import toRoman
from ResolutionStatuses import isDraft


def ResolutionInfo(ownerId, resolutionId, englishResolution, spanishResolution, committeeId, status, index, topic, comments, assigneeId, originalAssigneeId, committeeAbbreviationEnglish, committeeAbbreviationSpanish):
    englishTag = "%s/%s/%s%d" % (committeeAbbreviationEnglish, toRoman(topic, True), "DRAFT" if isDraft(status) else "", index)
    spanishTag = "%s/%s/%s%d" % (committeeAbbreviationSpanish, toRoman(topic, True), "PREL" if isDraft(status) else "", index)
    return {"ownerId": ownerId, "resolutionId": resolutionId,
            "englishResolution": englishResolution, "spanishResolution": spanishResolution,
            "committeeId": committeeId, "status": status,
            "index": index, "topic": topic, "comments": comments,
            "assigneeId": assigneeId, "originalAssigneeId": originalAssigneeId,
            "englishTag": englishTag, "spanishTag": spanishTag}
