from languages import *
import dblayer
(VERIFY_FULL_RESOLUTION, VERIFY_USER_SURE, VERIFY_USER_SURE_AND_ADDED_COMMENTS, VERIFY_RESOLUTIONS_MATCH, YOU_HAD_BETTER_BE_REAL_FUCKING_SURE_ABOUT_THIS, VERIFY_ONLY_ONE_IF_BILINGUAL) = range(6)

def _verifyResolutionsMatch(ri):
    if not ("englishResolution" in ri and "spanishResolution" in ri):
        return False
    (eng, span) = (ri["englishResolution"], ri["spanishResolution"])
    if not len(eng["preambulars"]) == len(span["preambulars"]):
        return False
    if not len(eng["operatives"]) == len(span["operatives"]):
        return False
    for ec, sc in zip(eng["operatives"], span["operatives"]):
        if ec["level"] != sc["level"]:
            return False
    return True

def _clausesFull(ri, lang):
    if lang == ENGLISH:
        if not "englishResolution" in ri:
            return False
        loc = ri["englishResolution"]
    elif lang == SPANISH:
        if not "spanishResolution" in ri:
            return False
        loc = ri["spanishResolution"]
    if (not loc) or (not "preambulars" in loc) or (not "operatives" in loc) or (not loc["preambulars"]) or (not loc["operatives"]):
        return False
    return True

def _verifyResolutionFull(ri):
    lang = dblayer.getCommitteeLanguage(ri["committeeId"])
    if lang == BILINGUAL:
        if not (_clausesFull(ri, SPANISH) or _clausesFull(ri, ENGLISH)):
            return False
    elif lang == ENGLISH:
        if not _clausesFull(ri, ENGLISH):
            return False
    elif lang == SPANISH:
        if not _clausesFull(ri, SPANISH):
            return False
    if not "sponsors" in ri or not ri["sponsors"]:
        return False
    return True

ActionVerifications = [{"verificationID": VERIFY_FULL_RESOLUTION,
    "js": r"""function ()
            {
              var cr = window.currentRes;
              var loc = getLocalizedRes(cr);
              if (loc.preambulars.length == 0)
              {
                alert("A valid resolution must have at least one preambular clause.");
                return false;
              }
              if (loc.operatives.length == 0)
              {
                alert("A valid resolution must have at least one operative clause.");
                return false;
              }
              if (cr.sponsors.length == 0)
              {
                alert("A valid resolution must have at least one sponsor.");
                return false;
              }
              return true;
            }""",
            "python": _verifyResolutionFull},
    {"verificationID": VERIFY_USER_SURE,
        "js": r"""function ()
            {
              return confirm("Are you sure you want to perform this action? Please verify that you entered everything correctly.");
            }""",
            "python": lambda ri: True},
    {"verificationID": VERIFY_USER_SURE_AND_ADDED_COMMENTS,
        "js": r"""function()
            {
              var cr = window.currentRes;
              var loc = getLocalizedRes(cr);

              if (!cr.comments)
              {
                alert("If you are rejecting this resolution, please add some comments describing what is wrong with it.");
                return false;
              }
              return confirm("Are you sure you want to perform this action? Please verify that you entered everything correctly.");
            }""",
            "python": lambda ri: bool(ri["comments"])},
    {"verificationID": VERIFY_RESOLUTIONS_MATCH, 
        "js": r"""function ()
        {
            var cr = window.currentRes;
            var eng = cr.englishResolution;
            var span = cr.spanishResolution;
            if (!eng || !span)
            {
                _fuckup("VERIFY_RESOLUTIONS_MATCH called but both languages don't exist.");
                return false;
            }
            if (eng.preambulars.length != span.preambulars.length)
            {
                alert("The translation is not correct: one version has more preambular clauses than the other.");
                return false;
            }
            if (eng.operatives.length != span.operatives.length)
            {
                alert("The translation is not correct: one version has more operative clauses than the other.");
                return false;
            }
            for (var i = 0; i < eng.operatives.length; ++i)
            {
                if (eng.operatives[i].level != span.operatives[i].level)
                {
                    alert("The translation is not correct: operative clause " + (i + 1) + " is at a different subclause level.");
                    return false;
                }
            }
            return true;
        }""", "python": _verifyResolutionsMatch },
    {"verificationID": VERIFY_ONLY_ONE_IF_BILINGUAL,
        "js": r"""function()
            {
                var cr = window.currentRes;
                if (getLang(cr) == BILINGUAL)
                {
                    var test = function(loc) { if (!loc) return true; return loc.operatives.length == 0 && loc.preambulars.length == 0; };
                    var ret = test(cr.englishResolution) || test(cr.spanishResolution);
                    if (!ret)
                    {
                        alert("You have entered clauses in both English and Spanish. Please only fill in one and let Conference Services headquarters handle the translation.");
                    }
                    return ret;
                }
                return true;
            }""",
            #FIXME
            "python": lambda ri: True},
    {"verificationID": YOU_HAD_BETTER_BE_REAL_FUCKING_SURE_ABOUT_THIS,
        "js": r"""function ()
            {
              alert("WARNING! The draft resolution and all amendments were already approved, so there should be no need to modify the resolution. If you reject it, please add comments. It will be sent to the head of Conference Services for review.");
              return confirm("Are you sure you want to reject this resolution?");
            }""",
            "python": lambda ri: True}]

def verify(verificationID, ri):
    for verification in ActionVerifications:
        if verification["verificationID"] == verificationID:
            return verification["python"](ri)
    return True #FIXME : This is a big WTF, log it.
