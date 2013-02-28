(PICK_RP, PICK_TRANSLATOR) = range(2)

ActionDialogs = [{"dialogID": PICK_RP,
        "js": r"""function(res)
        {
            var answer;
            promptStr = "";
            //FIXME
            if (getLang(res) == ENGLISH)
            {
                var RPs = englishRPs;
            }
            else
            {
                var RPs = spanishRPs
            }
            for (var i = 0; i < RPs.length; ++i)
            {
                promptStr += i;
                promptStr += ") ";
                promptStr += RPs[i]._fullName;
                promptStr += "\n";
            }
            while (true)
            {
                answer = prompt(promptStr);
                if (!(answer == "" || isNaN(answer)) && answer % 1 === 0)
                {
                    if (+answer >= 0 && +answer < RPs.length)
                    {
                        return {'param': RPs[+answer]._uId, 'OK': true};
                    }
                }
            }
        }"""}, {"dialogID": PICK_TRANSLATOR,
            "js": r"""
        function (res)
        {
            return;
        }"""}]

