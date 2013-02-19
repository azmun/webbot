import collections

(PICK_RP, PICK_TRANSLATOR) = range(2)

ActionDialog = collections.namedtuple("ActionDialog", ["dialogID", "js"])

ActionDialogs = [ActionDialog(PICK_RP,
    r"""function(res)
        {
            var answer;
            promptStr = "";
            if (res.language == ENGLISH)
            {
                var RPs = englishRPs;
            }
            else if (res.language == SPANISH || res.language == BILINGUAL)
            {
                var RPs = spanishRPs
            }
            for (var i = 0; i < RPs.length; ++i)
            {
                promptStr += i;
                promptStr += ") ";
                promptStr += RPs[i].fullName;
                promptStr += "\n";
            }
            while (true)
            {
                answer = prompt(promptStr);
                if (!(answer == "" || isNaN(answer)) && answer % 1 === 0)
                {
                    if (+answer >= 0 && +answer < RPs.length)
                    {
                        return RPs[+answer].uID;
                    }
                }
            }
        }"""), ActionDialog(PICK_TRANSLATOR,
        r"""
        function (res)
        {
            return;
        }""")]

