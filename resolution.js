Array.prototype.insert = function (index, item) {
	this.splice(index, 0, item);
};
// Array Remove - By John Resig (MIT Licensed)
Array.remove = function (array, from, to) {
	var rest = array.slice((to || from) + 1 || array.length);
	array.length = from < 0 ? array.length + from : from;
	return array.push.apply(array, rest);
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
	var newRes = {preambulars: [], operatives: [], committeeId: cr.committeeId, resolutionID: cr.resolutionID, sponsors: [], index: cr.index, status: cr.status, comments: $("#comments").val()}
	$(".preambular.").each(function ()
			{
				var kw = $(this).find(".keyword").val();
				var ct = $(this).find(".content").val();
				newRes.preambulars.push({keyword: kw, content: ct});
			});
	$(".operative").each(function ()
			{
				var kw = $(this).find(".keyword").val();
				var ct = $(this).find(".content").val();
				var level = $(this).data("level);
				if (typeof kw == "undefined")
				{
					kw = null;
				}
				newRes.operatives.push({keyword: kw, content: ct, level: level});
			});
	$(".sponsor").each(function ()
			{
				if ($(this).attr("checked"))
				{
					newRes.sponsors.push($(this).data('country'));
				}
			});
	window.currentRes = newRes;
}

function performResolutionAction(action)
{
	reconstructCurrentResolution();
	for (var i = 0; i < action.verifications.length; ++i)
	{
		if (! _verifications[action.verifications[i]]())
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
	if (!action.expectToKeep)
	{
		forgetResolution(window.currentResolution.resolutionId);
	}
	sendActionMessage(window.currentResolution, action.identifier, param);
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
	var toAdd = $('<p class="preambular"><input type="button" class="insertBeforeButton" value="Insert new clause here" /><input type="text" class="keyword" style="width:50px" /><input type="text" class="content" style="width:200px" /><input type="button" class="deleteButton" value="Delete clause" /></p>');
	toAdd.find(".keyword").val(keyword);
	toAdd.find(".content").val(content);
	bindPreambular(index, toAdd);
	return toAdd;
}

function getOperativeToAdd(index, level, keyword, content)
{
	var toAdd = $('<p class="operative"><input type="button" class="insertBeforeButton" value="Insert new clause here" /><input type="text" class="content" style="width:200px" /><input type="button" class="newSubclauseButton" value="Add new subclause" /><input type="button" class="deleteButton" value="Delete clause (and all subclauses") /></p>');
	toAdd.data('level', level);
	toAdd.css('margin-left', level * 10);
	var contentElement = toAdd.find('.content');
	contentElement.val(content);
	if (level == 0)
	{
		contentElement.before($('<input type="text" class="keyword" style="width:50px" />').val(keyword));
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
	window.currentRes = resolution;
	$("#preambulars").empty();
	$("#operatives").empty();
	for (var i = 0; i < resolution.preambulars.length; ++i)
	{
		var toAdd = getPreambularToAdd(i, resolution.preambulars[i].keyword, resolution.preambulars[i].content);
		$("#preambulars").append(toAdd);
	}
	var newClauseButton = $('<input type="button" id="newPreambularClauseButton" value="Insert new preambular clause" />');
	newClauseButton.click(newPreambular);
	$("#preambulars").append(newClauseButton);
	for (var i = 0; i < resolution.operatives.length; ++i)
	{
		var op = resolution.operatives[i];
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
		var toAdd = getOperativeToAdd(i, op.level, op.keyword, op,content); //keyword may not exist, but it's dgaf
		$("#operatives").append(toAdd);
	}
	$("#operatives").append($('<input type="button" id="newOperativeClauseButton" value="Add new operative clause" />').click(_bind(-1, newOperativeIn)));
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
		var checkbox = $('<input class="sponsor" type="checkbox" />').data("country", possibleSponsors[i]);
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
	for (var i = 0; i < resolution.actions.length; ++i)
	{
		$("#actions").append($('<input type="button" />').val(resolution.actions[i].displayName).click(_bind(resolution.actions[i], performResolutionAction)));
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
	window.currentResolution = null;
	$("#preambulars").html("<p>No resolution selected.</p>");
	$("#operatives").empty();
	$("#sponsors").empty();
	$("#comments").val('');
	$("#comments").attr("disabled", "disabled");
}

function buildResolutionsTree(resolutions, order)
{
    var first;
    var second;
    var topLevel = [];
    var firstLevel;
    var secondLevel;
    for (var i = 0; i < resolutions.length; ++i)
    {
        var res = resolutions[i];
        var firstChanged = false;
        var secondChanged = false;
        if (order.length > 0)
        {
            newFirst = res[order[0]];
            firstChanged = newFirst != first;
            first = newFirst;
            if (order.length > 1)
            {
                newSecond = res[order[1]];
                secondChanged = newSecond != second;
                second = newSecond;
            }
        }
        if (firstChanged)
        {
            firstLevel = {"title": res[order[0]], "children": [], "isFolder": true};
            topLevel.push(firstLevel);
            secondChanged = order.length > 1;
        }
        if (secondChanged)
        {
            secondLevel = {"title": res[order[1]], "children": [], "isFolder": true};
            firstLevel.children.push(secondLevel);
        }
        var whereToAdd;
        if (order.length > 1)
        {
            whereToAdd = secondLevel.children;
        }
        else if (order.length == 1)
        {
            whereToAdd = firstLevel.children;
        }
        else
        {
            whereToAdd = topLevel;
        }
        whereToAdd.push({"title": getResolutionTag(res), "resolution": res});
    }
}

$(document).ready(function() {
    var tree = buildResolutionsTree(resolutions, sortOrder);
    $("#menu").dynatree({
        children: tree,
        onActivate: function(node) {
            populateResolution(node.data.resolution);
        }
    });
});

