(RESOLUTION_VALID, NOT_ENOUGH_CLAUSES, NO_SPONSORS, KEYWORDS_MISSING) = range(4)
class Resolution:
    def __init__(self):
        self.preambulars = []
        self.operatives = []
        #List of strings
        self.sponsors = []

    def printToConsole(self):
        print 'PREAMBULARS:'
        for pre in self.preambulars:
            print "%s%s %s" % (" ", pre.keyword, pre.content)
        print 'OPERATIVES:'
        for op in self.operatives:
            if op.level == 0:
                print "%s%s %s" % (" ", op.keyword, op.content)
            else:
                print "%s%s" % (" " * (level + 1), op.content)

    def areClauesEqual(self, right):
        def clausesEqualRecursive(leftClause, rightClause):
            if leftClause.content != rightClause.content:
                return False
            if leftClause.numSubclauses() != rightClause.numSubclauses():
                return False
            for leftSubclause, rightSubclause in zip(leftClause.getSubclauses(), rightClause.getSubclauses()):
                if not clausesEqualRecursive(leftSubclause, rightSubclause):
                    return False
            return True
        if len(self.preambulars) != len(right.preambulars) or len(self.operatives) != len(right.operatives):
            return False
        for sP, rP in zip(self.preambulars, right.preambulars):
            if sP.keyword != rP.keyword or sP.content != rP.content:
                return False
        for sO, rO in zip(self.operatives, right.operatives):
            if sO.level != rO.level:
                return False
            if sO.level == 0 and sO.keyword != rO.keyword:
                return False
            if sO.content != rO.content:
                return False
        return True

    # Checks if two resolutions are the same.
    def isEqual(self, right):
        if self.sponsors != right.sponsors:
            return False
        return self.areClauesEqual(right)
        
    def getValidationStatus(self):
        if len(self.preambulars) == 0 or len(self.operatives) == 0:
            return NOT_ENOUGH_CLAUSES
        if len(self.sponsors) == 0:
            return NO_SPONSORS
        for clause in self.preambulars:
            if not clause.keyword:
                return KEYWORDS_MISSING
        for clause in self.operatives:
            if clause.level == 0 and not clause.keyword:
                return KEYWORDS_MISSING
        return RESOLUTION_VALID
