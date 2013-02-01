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
	return ["Bahrain", "USA", "UK", "Russian Federation", "France", "India", "Québec câliss", "The Federal Republic of Cascadia and Alaska"];
}

function populateResolution(resolution)
{
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
	var possibleSponsors = getPossibleSponsorsByCommittee(resolution.committeeId);
	possibleSponsors.sort();
	if (!possibleSponsors || !(possibleSponsors.length))
	{
		_fuckup("No possible sponsors found in committee: " + resolution.committeeId);
		return;
	}
	for (var i = 0; i < possibleSponsors.length; ++i)
	{
		var checkbox = $('<input type="checkbox" />').data("country", possibleSponsors[i]);
		if ($.inArray(possibleSponsors[i], sponsors) != -1)
		{
			checkbox.attr("checked", "checked");
		}
		$("#sponsors").append(checkbox);
		$("#sponsors").append(possibleSponsors[i]);
		$("#sponsors").append("<br />");
	}
}

function removeResolution()
{
	$("#preambulars").html("<p>No resolution selected.</p>");
	$("#operatives").empty();
	$("#sponsors").empty();
}

$(document).ready(function() {
	populateResolution({operatives: [], preambulars: [], committeeId: 0});
});
