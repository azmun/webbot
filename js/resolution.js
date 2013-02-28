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

function reconstructCurrentResolution()
{
	var cr = window.currentRes;
	var newRes = {englishResolution: {preambulars: [], operatives: []}, spanishResolution: {preambulars: [], operatives: []}, committeeId: cr.committeeId, resolutionId: cr.resolutionId, sponsors: [], index: cr.index, status: cr.status, comments: $("#comments").val()}
    var lang = getLang(cr);
    //FIXME: bilingual
    var localizedRes;
    if (lang == ENGLISH)
    {
        localizedRes = newRes.englishResolution;
    }
    else
    {
        localizedRes = newRes.spanishResolution
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
    if (getLang(res) == ENGLISH)
    {
        toSend["englishResolution"] = res.englishResolution;
    }
    //FIXME: BILINGUAL
    else
    {
        toSend["spanishResolution"] = res.spanishResolution;
    }
    toSend["id"] = res.resolutionId;
    toSend["comments"] = res.comments;
    toSend["action"] = action;
    toSend["param"] = param;
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

function getLocalizedRes(resolution)
{
	//HUGE WTF FIXME
	if (getLang(resolution) == ENGLISH)
	{
		return resolution.englishResolution;
	}
	else
	{
		return resolution.spanishResolution;
	}
}

function performResolutionAction(action)
{
	reconstructCurrentResolution();
	for (var i = 0; i < action.verifications.length; ++i)
	{
		var f = eval('function foo() { return ' + _verifications[action.verifications[i]] + '; }; foo();');
		if (! f())
		{
			return;
		}
	}
	var param = null;
	if (action.dialog)
	{
		var dialogResult = _actionDialogs[action.dialog]();
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
	var toAdd = $('<p class="preambular"><input type="button" class="insertBeforeButton" value="Insert new clause here"></input><input type="text" class="keyword" style="width:50px"></input><input type="text" class="content" style="width:200px"></input><input type="button" class="deleteButton" value="Delete clause"></input></p>');
	toAdd.find(".keyword").val(keyword);
	toAdd.find(".content").val(content);
	bindPreambular(index, toAdd);
	return toAdd;
}

function getOperativeToAdd(index, level, keyword, content)
{
	var toAdd = $('<p class="operative"><input type="button" class="insertBeforeButton" value="Insert new clause here"></input><input type="text" class="content" style="width:200px"></input><input type="button" class="newSubclauseButton" value="Add new subclause"></input><input type="button" class="deleteButton" value="Delete clause (and all subclauses")></input></p>');
	toAdd.data('level', level);
	toAdd.css('margin-left', level * 10);
	var contentElement = toAdd.find('.content');
	contentElement.val(content);
	if (level == 0)
	{
		contentElement.before($('<input type="text" class="keyword" style="width:50px"></input>').val(keyword));
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

function getPossibleSponsorsByCommittee(committeeId)
{
	//FIXME: fake.
	return ["Bahrain", "USA", "UK", "Russian Federation", "France", "India", "Québec", "Spain"];
}

function populateResolution(resolution)
{
    //FIXME: Bilingual
    var localizedRes;
    if (getLang(resolution) == ENGLISH)
    {
        localizedRes = resolution.englishResolution;
    }
    else
    {
        localizedRes = resolution.spanishResolution;
    }
	window.currentRes = resolution;
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
	var sponsors = resolution.sponsors
	var possibleSponsors = getPossibleSponsorsByCommittee(resolution.committeeId);
	possibleSponsors.sort();
	if (!possibleSponsors || !(possibleSponsors.length))
	{
		_fuckup("No possible sponsors found in committee: " + resolution.committeeId);
		return;
	}
	for (var i = 0; i < possibleSponsors.length; ++i)
	{
		var checkbox = $('<input class="sponsor" type="checkbox"></input>').data("country", possibleSponsors[i]);
		if ($.inArray(possibleSponsors[i], sponsors) != -1)
		{
			checkbox.attr("checked", "checked");
		}
		$("#sponsors").append(checkbox);
		$("#sponsors").append(possibleSponsors[i]);
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
	$("#preambulars").html("<p>No resolution selected.</p>");
	$("#operatives").empty();
	$("#sponsors").empty();
	$("#comments").val('');
	$("#comments").attr("disabled", "disabled");
}

function getResolutionTag(res)
{
    //FIXME
    return "" + res.topic + "/" + res.index;
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
            // make a new item based on order[j] and add it to levelParents[j]
            var item = {"title": order[j] + ": " + res[order[j]], "children": [], "isFolder": true};
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
});

