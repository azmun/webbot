from languages import *
from ResolutionStatuses import *
Reverse = {"language": {ENGLISH: "ENGLISH", SPANISH: "SPANISH", BILINGUAL: "BILINGUAL"},
        "status": {NEW_DRAFT: "NEW_DRAFT", RETURNED_DRAFT: "RETURNED_DRAFT",
            DRAFT_BEING_PROCESSED: "DRAFT_BEING_PROCESSED",
            ACCEPTED_DRAFT_WAITING_FOR_PRINTING: "ACCEPTED_DRAFT_WAITING_FOR_PRINTING",
            ACCEPTED_DRAFT_BEING_TRANSLATED: "ACCEPTED_DRAFT_BEING_TRANSLATED",
            PRINTED_DRAFT: "PRINTED_DRAFT",
            PASSED_RESOLUTION_BEING_PROCESSED: "PASSED_RESOLUTION_BEING_PROCESSED",
            PASSED_RESOLUTION_WAITING_FOR_PRINTING: "PASSED_RESOLUTION_WAITING_FOR_PRINTING",
            PRINTED_FINAL_RESOLUTION: "PRINTED_FINAL_RESOLUTION",
            FAILED_RESOLUTION: "FAILED_RESOLUTION",
            SERIOUS_WTF: "SERIOUS_WTF"}}
All = {}
for _, d in Reverse.iteritems():
    for k, v in d.iteritems():
        All[v] = k
