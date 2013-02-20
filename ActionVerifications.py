import collections

(VERIFY_FULL_RESOLUTION, VERIFY_USER_SURE, VERIFY_NO_OUTSTANDING_AMENDMENTS, VERIFY_USER_SURE_AND_ADDED_COMMENTS, VERIFY_RESOLUTIONS_MATCH, YOU_HAD_BETTER_BE_REAL_FUCKING_SURE_ABOUT_THIS) = range(6)

ActionVerification = collections.namedtuple("ActionVerification", ["verificationID", "js", "python"])

ActionVerifications = [ActionVerification(VERIFY_FULL_RESOLUTION,
        r"""function ()
            {
              var cr = window.currentRes;
              if (cr.preambulars.length == 0)
              {
                alert("A valid resolution must have at least one preambular clause.");
                return false;
              }
              if (cr.operatives.length == 0)
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
        lambda ri: len(ri.res.preambulars) > 0 and len(ri.res.operatives) > 0 and len(ri.res.sponsors) > 0),
    ActionVerification(VERIFY_USER_SURE,
        r"""function ()
            {
              return confirm("Are you sure you want to perform this action? Please verify that you entered everything correctly.");
            }""",
        lambda ri: True),
    #FIXME: Make this legit once we implement amendments.
    ActionVerification(VERIFY_NO_OUTSTANDING_AMENDMENTS, "function() { return true; }", lambda ri: True),
    ActionVerification(VERIFY_USER_SURE_AND_ADDED_COMMENTS,
        r"""function()
            {
              if (!cr.comments)
              {
                alert("If you are rejecting this resolution, please add some comments describing what is wrong with it.");
                return false;
              }
              return confirm("Are you sure you want to perform this action? Please verify that you entered everything correctly.");
            }""",
        lambda ri: bool(ri.comments)),
    #FIXME: Make this legit once we ipmlement translation
    ActionVerification(VERIFY_RESOLUTIONS_MATCH, "function () { return true; }", lambda ri: True),
    ActionVerification(YOU_HAD_BETTER_BE_REAL_FUCKING_SURE_ABOUT_THIS,
        r"""function ()
            {
              alert("WARNING! The draft resolution and all amendments were already approved, so there should be no need to modify the resolution. If you reject it, please add comments. It will be sent to the head of Conference Services for review.");
              return confirm("Are you sure you want to reject this resolution?");
            }""",
        lambda ri: True)]

def verify(verificationID, ri):
    for verificatonTuple in ActionVerifications:
        if verificationTuple[0] == verificationID:
            return verificationTuple[2](ri)
    return True #FIXME : This is a big WTF, log it.
