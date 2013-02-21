import collections


def ResolutionInfo(ownerId, resolutionId, englishResolution, spanishResolution, committeeId, status, index, topic, comments, assigneeId, originalAssigneeId):
    return {"ownerId": ownerId, "resolutionId": resolutionId,
            "englishResolution": englishResolution, "spanishResolution": spanishResolution,
            "committeeId": committeeId, "status": status,
            "index": index, "topic": topic, "comments": comments,
            "assigneeId": assigneeId, "originalAssigneeId": originalAssigneeId}
