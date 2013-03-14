Array.prototype.insert = function (index, item) {
	this.splice(index, 0, item);
};

function _bind(i, f)
{
	return function() {
		f(i);
	}
}
function isInt(value)
{
    var er = /^[0-9]+$/;
    return ( er.test(value) ) ? true : false;
}

function reconstructCurrentResolution(lang)
{
    var cr = window.currentRes;
    var newRes = {englishResolution: {preambulars: [], operatives: []}, spanishResolution: {preambulars: [], operatives: []}, committeeId: cr.committeeId, resolutionId: cr.resolutionId, sponsors: [], index: cr.index, status: cr.status, comments: $("#comments").val()}
    var localizedRes;
    if (lang === ENGLISH)
    {
        localizedRes = newRes.englishResolution;
        // Don't clobber the other one.
        newRes.spanishResolution = cr.spanishResolution;
    }
    else if (lang === SPANISH)
    {
        localizedRes = newRes.spanishResolution;
        // Don't clobber the other one.
        newRes.englishResolution = cr.englishResolution;
    }
	$(".preambular").each(function ()
			{
				var kw = $(this).find(".keyword").val();
				var ct = $(this).find(".content").val();
				localizedRes.preambulars.push({keyword: kw, content: ct});
			});
	$(".operative").each(function ()
			{
				var kw = $(this).find(".keyword").val();
				var ct = $(this).find(".content").val();
				var level = $(this).data("level");
				if (typeof kw == "undefined")
				{
					kw = null;
				}
				localizedRes.operatives.push({keyword: kw, content: ct, level: level});
			});
	$(".sponsor").each(function ()
			{
				if ($(this).prop("checked"))
				{
					newRes.sponsors.push($(this).data('country'));
				}
			});
	window.currentRes = newRes;
}

function getLang(res)
{
    return committees[res.committeeId].language;
}

function sendActionMessage(res, action, param)
{
    var toSend = {};
    toSend["englishResolution"] = res.englishResolution;
    toSend["spanishResolution"] = res.spanishResolution;
    toSend["id"] = res.resolutionId;
    toSend["comments"] = res.comments;
    toSend["action"] = action;
    toSend["param"] = param;
    toSend["sponsors"] = res.sponsors;
    $.post('/action', JSON.stringify(toSend), function(data) {
       if (! data.Success) {
           alert("An error has occurred! Please tell conference services.\nError: " + data.Error);
       }
    }, 'json').fail(function(_, textStatus, errorThrown)
        {
            alert(textStatus);
        });
}

function forgetResolution(resolutionId)
{
	if (window.currentRes.resolutionId == resolutionId)
	{
		removeResolution();
	}
	for (var i = 0; i < resolutions.length; ++i)
	{
		if (resolutions[i].resolutionId == resolutionId)
		{
			resolutions.splice(i, 1);
			rebuildTree();
			return;
		}
	}
}

function buildFunc(str)
{
	return eval('function foo() { return ' + str + '; }; foo();');
}

function getCheckedLanguage()
{
    return Number($('#languageChoice input[name=language]:checked').val());
}

function performResolutionAction(action)
{
	reconstructCurrentResolution(getCheckedLanguage());
	for (var i = 0; i < action.verifications.length; ++i)
	{
		var f = buildFunc(_verifications[action.verifications[i]]);
		if (! f())
		{
			return;
		}
	}
	var param = null;
	if (action.dialog !== null)
	{
		var f = buildFunc(_actionDialogs[action.dialog]);
		var dialogResult = f(window.currentRes);
		if (!dialogResult.OK)
		{
			return;
		}
		param = dialogResult.param;
	}
	sendActionMessage(window.currentRes, action.actionID, param);
	if (!action.expectToKeep)
	{
		forgetResolution(window.currentRes.resolutionId);
	}
}

function bindPreambular(i, elt)
{
	elt.find(".insertBeforeButton").off("click").on("click", _bind(i, insertPreambularBefore));
	elt.find(".deleteButton").off("click").on("click", _bind(i, deletePreambular));
}

function bindOperative(i, elt)
{
	elt.find('.insertBeforeButton').off("click").on("click", _bind(i, insertOperativeBefore));
	elt.find('.newSubclauseButton').off("click").on("click", _bind(i, newOperativeIn));
	elt.find('.deleteButton').off("click").on("click", _bind(i, deleteOperative));
}

function getPreambularToAdd(index, keyword, content)
{
	var toAdd = $('<div class="preambular"><input type="button" class="insertBeforeButton" value="Insert new clause here"></input><input type="text" class="keyword" style="width:100px"></input><textarea class="content" rows="6" cols="30"></textarea><input type="button" class="deleteButton" value="Delete clause"></input></div>');
	toAdd.find(".keyword").val(keyword);
	toAdd.find(".content").val(content);
	bindPreambular(index, toAdd);
	return toAdd;
}

function getOperativeToAdd(index, level, keyword, content)
{
	var toAdd = $('<div class="operative"><input type="button" class="insertBeforeButton" value="Insert new clause here"></input><textarea class="content" rows="6" cols="30" ></textarea><input type="button" class="newSubclauseButton" value="Add new subclause"></input><input type="button" class="deleteButton" value="Delete clause (and all subclauses")></input></div>');
	toAdd.data('level', level);
	toAdd.css('margin-left', level * 10);
	var contentElement = toAdd.find('.content');
	contentElement.val(content);
	if (level == 0)
	{
		contentElement.before($('<input type="text" class="keyword" style="width:100px"></input>').val(keyword));
	}
	bindOperative(index, toAdd);
	return toAdd;
}

function newPreambular()
{
	var toAdd = getPreambularToAdd($('.preambular').length, '', '');
	$('#newPreambularClauseButton').before(toAdd);
}

function newOperativeIn(parentIndex)
{
	if (parentIndex < 0) // adding new top-level clause
	{
		$('#newOperativeClauseButton').before(getOperativeToAdd($('.operative').length, 0, '', ''));
	}
	else
	{
		var parentLevel = $('.operative').eq(parentIndex).data('level');
		var addBeforeIndex = -1;
		$('.operative').slice(parentIndex + 1).each(function (i)
		{
			if ($(this).data('level') <= parentLevel)
			{
				addBeforeIndex = parentIndex + 1 + i;
				return false;
			}
		});
		if (addBeforeIndex == -1)
		{
			$('#newOperativeClauseButton').before(getOperativeToAdd($('.operative').length, parentLevel + 1, '', ''));
		}
		else
		{
			$('.operative').eq(addBeforeIndex).before(getOperativeToAdd(addBeforeIndex, parentLevel + 1, '', ''));
			$('.operative').slice(addBeforeIndex + 1).each(function (i) {
				bindOperative(addBeforeIndex + 1 + i, $(this));
			});
		}
	}
}

function insertPreambularBefore(index)
{
	var toAdd = getPreambularToAdd(index, '', '');
	$(".preambular").eq(index).before(toAdd);
	$(".preambular").slice(index + 1).each(function (i) {
		bindPreambular(index + 1 + i, $(this));
	});
}

function insertOperativeBefore(index)
{
	var where = $(".operative").eq(index);
	var level = where.data('level');
	var toAdd = getOperativeToAdd(index, level, '', '');
	where.before(toAdd);
	$(".operative").slice(index + 1).each(function (i) {
		bindOperative(index + 1 + i, $(this));
	});
}

function deletePreambular(index)
{
	$(".preambular").eq(index).remove();
	$(".preambular").slice(index).each(function (i) {
		bindPreambular(index + i, $(this));
	});
}

function deleteOperative(index)
{
	var howManyToDelete = 1;
	var oldLevel = $(".operative").eq(index).data("level");
	$(".operative").slice(index + 1).each(
		function ()
		{
			if ($(this).data("level") > oldLevel)
			{
				++howManyToDelete;
			}
			else
			{
				return false;
			}
		}
	);
	$(".operative").slice(index, index + howManyToDelete).remove();
	$(".operative").slice(index).each(function (i) {
		bindOperative(index + i, $(this));
	});
}

function getPossibleSponsorsByCommittee(committeeId, lang)
{
    return committees[committeeId].countries;
}

function languageChanged(lang)
{
    if (getLang(window.currentRes) !== BILINGUAL)
    {
        return;
    }
    var oldLang;
    if (lang === ENGLISH)
    {
        oldLang = SPANISH;
    }
    if (lang === SPANISH)
    {
        oldLang = ENGLISH;
    }
    // save any changes from the currently selected language
    reconstructCurrentResolution(oldLang);
    // populate the window with the new one
    populateResolution(window.currentRes);
}

function getActualLang(res)
{
    lang = getLang(res);
    if (lang !== BILINGUAL)
    {
        return lang;
    }
    return getCheckedLanguage();
}

function getLocalizedRes(res)
{
    lang = getActualLang(res);
    if (lang === ENGLISH)
    {
        return res.englishResolution;
    }
    if (lang === SPANISH)
    {
        return res.spanishResolution;
    }
}

function populateResolution(resolution)
{
    var lang = getLang(resolution);
    var actualLang;
    if (lang == BILINGUAL)
    {
        $('#languageChoice input[name=language]').each(function() {
            $(this).removeAttr('disabled');
        });
        actualLang = getCheckedLanguage();
    }
    else
    {
        $('#languageChoice input[name=language]').each(function() {
            $(this).attr('disabled', 'disabled');
            if (Number($(this).val() === lang))
            {
                $(this).attr('checked', 'checked');
            }
        });
        actualLang = lang;
    }
    var localizedRes;
    if (actualLang == ENGLISH)
    {
        localizedRes = resolution.englishResolution;
    }
    else if (actualLang == SPANISH)
    {
        localizedRes = resolution.spanishResolution;
    }
    else
    {
        _fuckup("What is actual lang??");
    }
	window.currentRes = resolution;
        $("#generateFormattedVersion").off("click").on("click", function() {
            var resolution = window.currentRes;
            window.location.href = "/generate?id=" + resolution.resolutionId + "&language=" + actualLang;
        });
        $("#generateFormattedVersion").removeAttr("disabled");
	$("#preambulars").empty();
	$("#operatives").empty();
    $("#sponsors").empty();
	for (var i = 0; i < localizedRes.preambulars.length; ++i)
	{
		var toAdd = getPreambularToAdd(i, localizedRes.preambulars[i].keyword, localizedRes.preambulars[i].content);
		$("#preambulars").append(toAdd);
	}
	var newClauseButton = $('<input type="button" id="newPreambularClauseButton" value="Insert new preambular clause"></input>');
	newClauseButton.click(newPreambular);
	$("#preambulars").append(newClauseButton);
	for (var i = 0; i < localizedRes.operatives.length; ++i)
	{
		var op = localizedRes.operatives[i];
		if (i == 0 && op.level != 0)
		{
			_fuckup("nonzero level: " + op.level +" at beginning of ops");
			return;
		}
		if (op.level < 0)
		{
			_fuckup("negative level: " + op.level);
			return;
		}
		var toAdd = getOperativeToAdd(i, op.level, op.keyword, op.content); //keyword may not exist, but it's dgaf
		$("#operatives").append(toAdd);
	}
	$("#operatives").append($('<input type="button" id="newOperativeClauseButton" value="Add new operative clause"></input>').click(_bind(-1, newOperativeIn)));
	var sponsorIds = $.map(resolution.sponsors, function (val) {
            return val.id;
        });
	var possibleSponsors = getPossibleSponsorsByCommittee(resolution.committeeId);
	possibleSponsors.sort(function(a, b) {
            if (actualLang == ENGLISH)
            {
                return a["englishName"] > b["englishName"];
            }
            if (actualLang == SPANISH)
            {
                return a["spanishName"] > b["spanishName"];
            }
        });
	if (!possibleSponsors || !(possibleSponsors.length))
	{
		_fuckup("No possible sponsors found in committee: " + resolution.committeeId);
		return;
	}
	for (var i = 0; i < possibleSponsors.length; ++i)
	{
                var sponsorName;
                if (actualLang == ENGLISH)
                {
                       sponsorName = possibleSponsors[i].englishName;
                }
                if (actualLang == SPANISH)
                {
                       sponsorName = possibleSponsors[i].spanishName; 
                }
		var checkbox = $('<input class="sponsor" type="checkbox"></input>').data("country", possibleSponsors[i]);
		if ($.inArray(possibleSponsors[i].id, sponsorIds) != -1)
		{
			checkbox.attr("checked", "checked");
		}
		$("#sponsors").append(checkbox);

		$("#sponsors").append(sponsorName);
		$("#sponsors").append("<br />");
	}
	$("#comments").removeAttr("disabled");
	$("#comments").val(resolution.comments);
	$("#actions").empty();
    var actions = resolutionActions[resolution.resolutionId]
	for (var i = 0; i < actions.length; ++i)
	{
		$("#actions").append($('<input type="button"></input>').val(actions[i].displayName).click(_bind(actions[i], performResolutionAction)));
	}
}

function isDirty()
{
    //FIXME also fix newResolution
    return false;
}

function newResolution(committee)
{
    if (isDirty())
    {
        //FIXME
    }
    window.location.replace("/new_resolution")
}

function removeResolution()
{
	window.currentRes = null;
        $("#generateFormattedVersion").attr("disabled", "disabled");
	$("#preambulars").html("<p>No resolution selected.</p>");
	$("#operatives").empty();
	$("#sponsors").empty();
	$("#comments").val('');
	$("#comments").attr("disabled", "disabled");
}

function getResolutionTag(res, lang)
{
    if (lang === ENGLISH)
    {
        return res["englishTag"];
    }
    if (lang === SPANISH)
    {
        return res["spanishTag"];
    }
    //lol 2 ez
}

function buildResolutionsTree(resolutions, order, howManyLevels)
{
    // If there are no resolutions, bail.
    if (resolutions.length == 0)
    {
        return [];
    }
    // Otherwise, set currentLevelElements to [null, ..., null] (howManyLevels times)
    var currentLevelElements = [];
    for (var i = 0; i < howManyLevels; ++i)
    {
        currentLevelElements.push(null);
    }
    // Set levelParents[0] = root of tree
    var levelParents = [];
    levelParents.push([]);
    // Now for each resolution res:
    for (var i = 0; i < resolutions.length; ++i)
    {
        res = resolutions[i];
        // let c be the minimum of howManyLevels and the 
        // smallest value such that currentLevelElements[c] differs from
        // res[order[c]].
        var c = 0;
        while (c < howManyLevels)
        {
            if (currentLevelElements[c] !== res[order[c]])
            {
                break;
            }
            ++c;
        }
        for (var j = c; j < howManyLevels; ++j)
        {
            var titleValue;
            if (order[j] in window.reverseEnums)
            {
                titleValue = window.reverseEnums[order[j]][res[order[j]]];
            }
            else
            {
                titleValue = res[order[j]];
            }
            // make a new item based on order[j] and add it to levelParents[j]
            var item = {"title": order[j] + ": " + titleValue, "children": [], "isFolder": true};
            levelParents[j].push(item);
            // set levelParents[j+1] to that item
            levelParents[j + 1] = item.children;
        }
        // now add the res tag to the highest levelParents.
        levelParents[levelParents.length - 1].push({"title": getResolutionTag(res), "resolution": res});
        
        // make currentLevelElements[x] be resolutions[order[x]] for each x
        for (var x = 0; x < howManyLevels; ++x)
        {
            currentLevelElements[x] = res[order[x]];
        }
    }
    return levelParents[0];
}

function rebuildTree()
{
    var tree = buildResolutionsTree(resolutions, sortOrder, sortOrder.length >= 2 ? 2 : sortOrder.length);
    $("#menu").dynatree({
        children: tree,
        onActivate: function(node) {
            populateResolution(node.data.resolution);
        }
    });
}

$(document).ready(function() {
	rebuildTree();
        $('#languageChoice input[name=language]').change(function () {
            languageChanged(getCheckedLanguage());
        });
});

