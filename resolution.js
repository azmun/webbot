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
	elt.find(".keyword").change(_bind(i, changePreambularKeyword));
	elt.find(".content").change(_bind(i, changePreambularContent));
	elt.find(".deleteButton").click(_bind(i, deletePreambular));
}

function bindOperative(i, elt)
{
	elt.find('.insertBeforeButton').click(_bind(i, insertOperativeBefore));
	elt.find('.keyword').change(_bind(i, changeOperativeKeyword)); // may not exist but jquery is dgaf in that case
	elt.find('.content').change(_bind(i, changeOperativeContent));
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
	var toAdd = $('<p class="operative"><input type="hidden" class="level" /><input type="button" class="insertBeforeButton" value="Insert new clause here" /><input type="text" class="content" style="width:200px" /><input type="button" class="newSubclauseButton" value="Add new subclause" /></p>');
	toAdd.attr('margin-left', index * 10);
	var contentElement = toAdd.find('.content');
	contentElement.val(content);
	toAdd.find('.level').val(level);
	if (level == 0)
	{
		contentElement.before($('<input type="text" class="keyword" style="width:50px" />').val(keyword));
	}
	bindOperative(index, toAdd);
	return toAdd;
}

function newPreambular()
{
	if (!window.res)
	{
		_fuckup("window.res evaluates to false in newPreambular()");
		return;
	}
	var toAdd = getPreambularToAdd(window.res.preambulars.length, '', '');
	$('#newPreambularClauseButton').before(toAdd);
	window.res.preambulars.push({keyword: '', content: ''});
}

function insertPreambularBefore(index)
{
	if (!window.res)
	{
		_fuckup("window.res evaluates to false in insertPreambularBefore(" + index + ")");
		return;
	}
	if (index >= window.res.preambulars.length)
	{
		_fuckup("tried to insert preambular before " + index + "but length is " + res.preambulars.length);
		return;
	}
	var toAdd = getPreambularToAdd(index, '', '');
	$(".preambular").eq(index).before(toAdd);
	$(".preambular").gt(index).each(bindPreambular);
	window.res.preambulars.insert({keyword: '', content: ''});
}

function insertOperativeBefore(index)
{
	if (!window.res)
	{
		_fuckup("window.res evaluates to false in insertOperativeBefore(" + index + ")");
		return;
	}
	if (index >= window.res.operatives.length)
	{
		_fuckup("tried to insert operative before " + index + "but length is " + res.operatives.length);
		return;
	}
	var where = $(".operative").eq(index);
	var level = where.find('.level').val();
	var toAdd = getOperativeToAdd(index, level, '', '');
	where.before(toAdd);
	$(".operative").gt(index).each(bindOperative);
	var clauseObj = {keyword: '', content: ''};
	var op = window.res.operatives[index];
	clauseObj.stepUp = op.stepUp;
	clauseObj.stepDown = op.stepDown;
	op.stepUp = 0;
	op.stepDown = false;
}

function deletePreambular(index)
{
	if (!window.res)
	{
		_fuckup("window.res evaluates to false in deletePreambular(" + index + ")");
		return;
	}
	if (index >= window.res.preambulars.length)
	{
		_fuckup("tried to delete preambular at " + index + "but length is " + res.preambulars.length);
		return;
	}
	$(".preambular").eq(index).remove();
	$(".preambular").gt(index - 1).each(bindPreambular);
	window.res.preambulars.remove(index);
}

function deleteOperative(index)
{
	if (!window.res)
	{
		_fuckup("window.res evaluates to false in deleteOperative(" + index + ")");
		return;
	}
	var ops = window.res.operatives;
	if (index >= ops.length)
	{
		_fuckup("tried to delete operative at " + index + "but length is " + res.operatives.length);
		return;
	}
	var howManyToDelete = 1;
	var steps = 0;
	var oldSteps = -ops[index].stepUp;
	if (ops[index].stepDown)
	{
		oldSteps = 1;
	}
	for (var i = index + 1; i < ops.length; ++i)
	{
		if (ops[i].stepDown)
		{
			++steps;
		}
		else if (ops[i].stepUp)
		{
			steps -= ops[i].stepUp;
		}
		if (steps > 0)
		{
			++howManyToDelete;
		}
		else
		{
			break;
		}
	}

	$(".operative").gt(index - 1).lt(howManyToDelete).remove();
	$(".operative").gt(index - 1).each(bindOperative);
	ops.splice(index, howManyToDelete);
	if (index < ops.length)
	{
		var newSteps = oldSteps + steps;
		if (newSteps == 1)
		{
			ops[index].stepDown = true;
			ops[index].stepUp = 0;
		}
		else if (newSteps == 0)
		{
			ops[index].stepDown = false;
			ops[index].stepUp = 0;
		}
		else if (newSteps < 0)
		{
			ops[index].stepDown = false;
			ops[index].stepUp = -newSteps;
		}
	}
}

function populateResolution(resolution)
{
	window.res = resolution;
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
	var steps = 0;
	for (var i = 0; i < resolution.operatives.length; ++i)
	{
		var op = resolution.operatives[i];
		if (op.stepDown && op.stepUp)
		{
			_fuckup("stepdown and stepup set!");
			return;
		}
		if (i == 0 && op.stepDown)
		{
			_fuckup("stepdown at beginning of ops");
			return;
		}
		if (steps - op.stepUp < 0)
		{
			_fuckup("step up to negative");
			return;
		}
		if (op.stepDown)
		{
			++steps;
		}
		else if (op.stepUp > 0)
		{
			steps -= op.stepUp;
		}
		var toAdd = getOperativeToAdd(i, steps, op.keyword, op,content); //keyword may not exist, but it's dgaf
		$("#operatives").append(toAdd);
	}
	$("#operatives").append($('<input type="button" id="newOperativeClauseButton" value="Add new operative clause" />').click(_bind(-1, newOperativeIn)));
	resolution.sponsors.sort();
	$("#sponsorsBox").val(resolution.sponsors.join(', '));
	$("#sponsorsButton").removeAttr("disabled").click(changeSponsors);
}

function removeResolution()
{
	window.res = null;
	$("#preambulars").html("<p>No resolution selected.</p>");
	$("#operatives").empty();
	$("#sponsorsBox").val('');
	$("#sponsorsButton").attr("disabled", "disabled");
}
