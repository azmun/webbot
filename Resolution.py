class Clause:
    def __init__(self, content):
        self.content = content
        self.subclauses = []
        self.parent = None
        self.depth = 1
        self.clauseIndex = 1
    def getTerminator(self): #perversion of OOP, but fuck OOP anyway
        if isinstance(self, PreambularMainClause):
            return "," 
        if self.isLastInDocument():
            return "."
        if len(self.subclauses) > 0:
            return ":"
        return ";"
    def __isLastRecursive(self):
        if isinstance(self, OperativeMainClause) and len(self.parent.operatives) == self.clauseIndex:
            return True
        if (not isinstance(self, MainClause)) and len(self.parent.subclauses) == self.clauseIndex and self.parent.__isLastRecursive():
            return True
        return False
    def isLastInDocument(self):
        return len(self.subclauses) == 0 and self.__isLastRecursive()
    def getSubclauses(self):
        return self.subclauses
    def numSubclauses(self):
        return len(self.subclauses)
    def numSiblings(self):
        return len(self.parent.subclauses)
    # Sets the depths of this clause and all subclauses, with this clause having the given depth.
    def setDepths(self, depth):
        self.depth = depth
        for clause in self.subclauses:
            clause.setDepths(depth + 1)
    def insertSubclause(self, clauseIndex, clause):
        self.subclauses.insert(clauseIndex - 1, clause)
        clause.clauseIndex = clauseIndex
        clause.setDepths(self.depth + 1)
        clause.parent = self
        for subclause in self.subclauses[clauseIndex:]: # Every clause after the one we just added
            subclause.clauseIndex += 1
    def getDisplayName(self):
        return "%s %s" % (Utilities.outlineStyleNumber(self.depth, self.clauseIndex), self.content.strip())
    
class MainClause(Clause):
    def __init__(self, keyword, content):
        Clause.__init__(self, content)
        self.keyword = keyword
        
class PreambularMainClause(MainClause):
    def __init__(self, keyword, content):
        MainClause.__init__(self, keyword, content)
    def getDisplayName(self):
        return "%s %s" % (self.keyword.strip(), self.content.strip())
    def numSiblings(self):
        return len(self.parent.preambulars)

class OperativeMainClause(MainClause):
    def __init__(self, keyword, content):
        MainClause.__init__(self, keyword, content)
    def getDisplayName(self):
        return "%s %s %s" % (Utilities.outlineStyleNumber(self.depth, self.clauseIndex), self.keyword.strip(), self.content.strip())
    def numSiblings(self):
        return len(self.parent.preambulars)

(RESOLUTION_VALID, NOT_ENOUGH_CLAUSES, NO_SPONSORS, KEYWORDS_MISSING) = range(4)
class Resolution:
    def toOdtOutline(res):
        def getOperRecursive(clause, depth):
            has_children = len(clause.subclauses) > 0
            if has_children:
                start_list = u'''<text:list>'''
                end_list = u'''</text:list>'''
            else:
                start_list = u''
                end_list = u''
            if depth == 1:
                return u'''<text:list-item><text:p text:style-name="P3"><text:span text:style-name="T2">''' + clause.keyword + u''' </text:span><text:span text:style-name="T1">''' + clause.content + clause.getTerminator() + u'''</text:span></text:p>''' + start_list + u''.join([getOperRecursive(child, depth + 1) for child in clause.subclauses])+end_list + u'''</text:list-item>'''
            if depth == 2:
                return u'''<text:list-item><text:p text:style-name="P5"><text:span text:style-name="T1">''' + clause.content + clause.getTerminator() + u'''</text:span></text:p>''' + start_list + u''.join([getOperRecursive(child, depth + 1) for child in clause.subclauses])+ end_list + u'''</text:list-item>'''
            return u'''<text:list-item><text:p text:style-name="P7"><text:span text:style-name="T1">''' + clause.content + clause.getTerminator() + u'''</text:span></text:p></text:list-item>'''
        ret = u''''''
        for pream in res.preambulars:
            ret += u'''<text:p text:style-name="P9"><text:span text:style-name="T2">''' + pream.keyword + u''' </text:span><text:span text:style-name="T1">''' + pream.content + pream.getTerminator() + u'''</text:span></text:p>'''
        ret += u'''<text:list text:style-name="WWNum1">'''
        for oper in res.operatives:
            ret += getOperRecursive(oper, 1)
        ret += u'''</text:list>'''
        return ret
    
    def __init__(self):
        self.preambulars = []
        self.operatives = []
        #List of strings
        self.sponsors = []

    def printToConsole(self):
        def printRecursive(clause, depth):
            if depth == 1:
                print "%s%s %s" % (" " * depth, clause.keyword, clause.content)
            else:
                print "%s%s" % (" " * depth, clause.content)
            for subClause in clause.getSubclauses():
                printRecursive(subClause, depth + 1)
        print 'PREAMBULARS:'
        for preambularClause in self.preambulars:
            printRecursive(preambularClause, 1)
        print 'OPERATIVES:'
        for operativeClause in self.operatives:
            printRecursive(operativeClause, 1)

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
        selfClauses = self.preambulars + self.operatives
        rightClauses = right.preambulars + right.operatives
        for selfClause, rightClause in zip(selfClauses, rightClauses):
            if selfClause.keyword != rightClause.keyword:
                return False
            if not clausesEqualRecursive(selfClause, rightClause):
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
            if not clause.keyword:
                return KEYWORDS_MISSING
        return RESOLUTION_VALID

    def insertOperative(self, clauseIndex, clause):
        self.operatives.insert(clauseIndex - 1, clause)
        clause.setDepths(1)
        clause.clauseIndex = clauseIndex
        clause.parent = self
        clauseIndex = 1
        for operativeClause in self.operatives:
            operativeClause.clauseIndex = clauseIndex
            clauseIndex += 1

    def insertPreambular(self, clauseIndex, clause):
        self.preambulars.insert(clauseIndex - 1, clause)
        clause.setDepths(1)
        clause.clauseIndex = clauseIndex
        clause.parent = self
        clauseIndex= 1
        for preambularClause in self.preambulars:
            preambularClause.clauseIndex = clauseIndex
            clauseIndex += 1

    def removeClause(self, clause):
        if clause.parent is self:
            if isinstance(clause, PreambularMainClause):
                self.preambulars.remove(clause)
                clauseIndex = 1
                for preambularClause in self.preambulars:
                    preambularClause.clauseIndex = clauseIndex
                    clauseIndex += 1
            elif isinstance(clause, OperativeMainClause):
                self.operatives.remove(clause)
                clauseIndex = 1
                for operativeClause in self.operatives:
                    operativeClause.clauseIndex = clauseIndex
                    clauseIndex += 1
        else:
            # clause.parent is some other clause
            clause.parent.subclauses.remove(clause)
            clauseIndex = 1
            for subclause in clause.parent.subclauses:
                subclause.clauseIndex = clauseIndex
                clauseIndex += 1

    def numPreambulars(self):
        return len(self.preambulars)

    def numOperatives(self):
        return len(self.operatives)
        
    
        
