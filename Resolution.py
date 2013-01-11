(RESOLUTION_VALID, NOT_ENOUGH_CLAUSES, NO_SPONSORS, KEYWORDS_MISSING) = range(4)
def getEmptyResolution():
    return {"preambulars": [], "operatives": [], "sponsors": []}

def printToConsole(res):
    print 'PREAMBULARS:'
    for pre in res["preambulars"]:
        print "%s%s %s" % (" ", pre["keyword"], pre["content"])
    print 'OPERATIVES:'
    for op in res["operatives"]:
        if op["level"] == 0:
            print "%s%s %s" % (" ", op["keyword"], op["content"])
        else:
            print "%s%s" % (" " * (level + 1), op["content"])
            
# Checks if two resolutions are the same.
def isEqual(res, right):
    if res["sponsors"] != right["sponsors"]:
        return False
    if len(res["preambulars"]) != len(right["preambulars"]) or len(res["operatives"]) != len(res["operatives"]):
        return False
    for l, r in zip(res["preambulars"], right["preambulars"]):
        if l["keyword"] != r["keyword"] or l["content"] != r["content"]:
            return False
    for l, r in zip(res["operatives"], right["operatives"]):
        if l["level"] != r["level"] or l["content"] != r["content"]:
            return False
        if l["level"] == 0 and l["keyword"] != r["keyword"]:
            return False
    return True
    
def getValidationStatus(res):
    if len(res["preambulars"]) == 0 or len(res["operatives"]) == 0:
        return NOT_ENOUGH_CLAUSES
    if len(res["sponsors"]) == 0:
        return NO_SPONSORS
    for clause in res["preambulars"]:
        if not clause.keyword:
            return KEYWORDS_MISSING
    for clause in res["operatives"]:
        if clause.level == 0 and not clause.keyword:
            return KEYWORDS_MISSING
    return RESOLUTION_VALID
