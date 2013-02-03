class ResolutionInfo:
    def __init__(self, ownerId, resolutionId, englishResolution, spanishResolution, committeeId, status, index, topic, comments, assigneeId = None):
        self.ownerId = ownerId
        self.resolutionId = resolutionId
        self.resolution = resolution
        self.committeeId = committeeId
        self.status = status
        self.index = index
        self.topic = topic
        self.assigneeId = assigneeId
        self.comments = comments
        self.originalAssigneeId = None
