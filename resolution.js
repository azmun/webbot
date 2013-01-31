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

function insertPreambularBefore(index)
{
	if (!window.res)
	{
		_fuckup("window.res evaluates to false in insertPreambularBefore(" + index + ")");
		return;
	}
	if (index >= res.preambulars.length)
	{
		_fuckup("tried to insert preambular before " + index + "but length is " + res.preambulars.length);
		return;
	}
	var toAdd = getPreambularToAdd(index, '', '');
	$(".preambular").eq(index).before(toAdd);
	$(".preambular").gt(index).each(bindPreambular);
}

function insertOperativeBefore(index)
{
	if (!window.res)
	{
		_fuckup("window.res evaluates to false in insertOperativeBefore(" + index + ")");
		return;
	}
	if (index >= res.operatives.length)
	{
		_fuckup("tried to insert operative before " + index + "but length is " + res.operatives.length);
		return;
	}
	var where = $(".operative").eq(index);
	var level = where.find('.level').val();
	var toAdd = getOperativeToAdd(index, level, '', '');
	where.before(toAdd);
	$(".operative").gt(index).each(bindOperative);
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
	var newClauseButton = $('<input type="button" value="Insert new preambular clause" />');
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
	$("#operatives").append($('<input type="button" value="Add new operative clause" />').click(_bind(-1, newOperativeIn)));
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
