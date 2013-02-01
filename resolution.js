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
	elt.find(".insertBeforeButton").click(_bind(i, insertPreambularBefore));
	elt.find(".deleteButton").click(_bind(i, deletePreambular));
}

function bindOperative(i, elt)
{
	elt.find('.insertBeforeButton').click(_bind(i, insertOperativeBefore));
	elt.find('.newSubclauseButton').click(_bind(i, newOperativeIn));
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
	var toAdd = $('<p class="operative"><input type="button" class="insertBeforeButton" value="Insert new clause here" /><input type="text" class="content" style="width:200px" /><input type="button" class="newSubclauseButton" value="Add new subclause" /></p>');
	toAdd.data('level', level);
	toAdd.attr('margin-left', index * 10);
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
	var toAdd = getPreambularToAdd(window.res.preambulars.length, '', '');
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
		$('.operative').gt(parentIndex).each(function (i)
		{
			if ($(this).data('level') <= parentLevel)
			{
				addBeforeIndex = i;
				return false;
			}
		}
		if (addBeforeIndex == -1)
		{
			$('#newOperativeClauseButton').before(getOperativeToAdd($('.operative').length, parentLevel + 1, '', ''));
		}
		else
		{
			$('.operative').eq(addBeforeIndex).before(getOperativeToAdd(addBeforeIndex, parentLevel + 1, '', ''));
		}
	}
}

function insertPreambularBefore(index)
{
	var toAdd = getPreambularToAdd(index, '', '');
	$(".preambular").eq(index).before(toAdd);
	$(".preambular").gt(index).each(bindPreambular);
}

function insertOperativeBefore(index)
{
	var where = $(".operative").eq(index);
	var level = where.data('level');
	var toAdd = getOperativeToAdd(index, level, '', '');
	where.before(toAdd);
	$(".operative").gt(index).each(bindOperative);
}

function deletePreambular(index)
{
	$(".preambular").eq(index).remove();
	$(".preambular").gt(index - 1).each(bindPreambular);
}

function deleteOperative(index)
{
	var howManyToDelete = 1;
	var steps = 0;
	var oldLevel = $(".preambular").eq(index).data("level");
	$(".preambular").gt(index).each(
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
	});
	$(".operative").gt(index - 1).lt(howManyToDelete).remove();
	$(".operative").gt(index - 1).each(bindOperative);
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
	resolution.sponsors.sort();
	$("#sponsorsBox").val(resolution.sponsors.join(', '));
	$("#sponsorsButton").removeAttr("disabled").click(changeSponsors);
}

function removeResolution()
{
	$("#preambulars").html("<p>No resolution selected.</p>");
	$("#operatives").empty();
	$("#sponsorsBox").val('');
	$("#sponsorsButton").attr("disabled", "disabled");
}
