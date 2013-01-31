class ResolutionInfo:
    def __init__(self, resolutionId, englishResolution, spanishResolution, committeeId, status, index, topic, assigneeId = None):
        self.resolutionId = resolutionId
        self.resolution = resolution
        self.committeeId = committeeId
        self.status = status
        self.index = index
        self.topic = topic
        self.assigneeId = assigneeId
        self.originalAssigneeId = None
