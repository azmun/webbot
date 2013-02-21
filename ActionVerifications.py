(VERIFY_FULL_RESOLUTION, VERIFY_USER_SURE, VERIFY_USER_SURE_AND_ADDED_COMMENTS, VERIFY_RESOLUTIONS_MATCH, YOU_HAD_BETTER_BE_REAL_FUCKING_SURE_ABOUT_THIS) = range(5)

ActionVerifications = [{"verificationID": VERIFY_FULL_RESOLUTION,
    "js": r"""function ()
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
            "python": lambda ri: len(ri.res.preambulars) > 0 and len(ri.res.operatives) > 0 and len(ri.res.sponsors) > 0},
    {"verificationID": VERIFY_USER_SURE,
        "js": r"""function ()
            {
              return confirm("Are you sure you want to perform this action? Please verify that you entered everything correctly.");
            }""",
            "python": lambda ri: True},
    {"verificationID": VERIFY_USER_SURE_AND_ADDED_COMMENTS,
        "js": r"""function()
            {
              if (!cr.comments)
              {
                alert("If you are rejecting this resolution, please add some comments describing what is wrong with it.");
                return false;
              }
              return confirm("Are you sure you want to perform this action? Please verify that you entered everything correctly.");
            }""",
            "python": lambda ri: bool(ri.comments)},
    {"verificationID": VERIFY_RESOLUTIONS_MATCH, "js": "function () { return true; }", "python": lambda ri: True},
    {"verificationID": YOU_HAD_BETTER_BE_REAL_FUCKING_SURE_ABOUT_THIS,
        "js": r"""function ()
            {
              alert("WARNING! The draft resolution and all amendments were already approved, so there should be no need to modify the resolution. If you reject it, please add comments. It will be sent to the head of Conference Services for review.");
              return confirm("Are you sure you want to reject this resolution?");
            }""",
            "python": lambda ri: True}]

def verify(verificationID, ri):
    for verificatonTuple in ActionVerifications:
        if verificationTuple[0] == verificationID:
            return verificationTuple[2](ri)
    return True #FIXME : This is a big WTF, log it.
