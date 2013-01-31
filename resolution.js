function _bind(i, f)
{
	return function() {
		f(i);
	}
}

function bindPreambular(index, elt)
{
	elt.find(".insertBeforeButton").click(_bind(i, insertPreambularBefore));
	elt.find(".keyword").change(_bind(i, changePreambularKeyword));
	elt.find(".content").change(_bind(i, changePreambularContent));
	elt.find(".deleteButton").click(_bind(i, deletePreambular));
}

function getPreambularToAdd(index, keyword, content)
{
	var toAdd = $('<p class="preambular"><input type="button" class="insertBeforeAction" value="Insert new clause here" /><input type="text" class="keyword" style="width:50px" /><input type="text" class="content" style="width:200px" /><input type="button" class="deleteButton" value="Delete clause" /></p>');
	toAdd.find(".keyword").val(keyword);
	toAdd.find(".content").val(content);
	bindPreambular(index, toAdd);
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
	$(".preambular").gt(index).each(function(i, e) {
		bindPreambular(i, e);
	});
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
		var toAdd = $("<p></p>");
		toAdd.css("margin-left", 10 * steps);
		var insertButton = $('<input type="button" value="Insert new clause here" />');
		insertButton.click(_bind(i, insertOperativeBefore));
		toAdd.append(insertButton);
		if (steps == 0)
		{
			var keyword = $('<input type="text" style="width:50px" />');
			keyword.change(_bind(i, changeOperativeKeyword));
			toAdd.append(keyword);
		}
		var content = $('<input type="text" style="width:200px" />');
		content.change(_bind(i, changeOperativeContent));
		toAdd.append(content);
		var addNew = $('<input type="button" value="Add new subclause" />');
		addNew.click(_bind(i, newOperativeIn));
		toAdd.append(addNew);
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
