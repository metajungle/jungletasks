
/*
 * ==========
 * GENERAL
 * ==========
 */

/**
 * Save the labels for the active task 
 */
function task_labels_save() {
    
    /* get the task id from the data- attribute */
    var t_id = $("ul#folders li.user-defined-labels").metadata().task;
    
    /* get label ids */
    var l_ids = new Array();
    $("ul#folders li.label-edit").each(function() {
	/* if it is active then we will use the label */
	if ($(this).hasClass('label-edit-active')) {
	    var l_id = $(this).metadata().label_id;
	    l_ids.push(l_id);
	}
    });

    var data = { 't_id' : t_id, 'l_ids' : l_ids }

    /* get priority */
    var pri = dom_get_set_priority();
    if (pri != false) {
	/* add priority to data list set to backend */
	data['priority'] = pri;
    }

    /* save to db */
    $.post(getHostName() + url_tasks_api_task_labels_save,
	   { 'json' : JSON.stringify(data) }, 
	   function (data, status) {
	       if (status == 'success' && data != 'False') {
		   /* do nothing */
	       }
	   }
	  );

    /* update the DOM with metadata */
    dom_task_labels_save(t_id, l_ids);

    /* update the DOM with mini labels */
    dom_task_minilabels_save(t_id, l_ids);

    /* update DOM with priority information */
    if (pri != false)
	dom_task_priority_update(t_id, pri); 

    /* restore the labels */
    dom_label_task_clearup();
}

/**
 * TODO: To write  
 *
 */ 
function bookmarklet_task_add() {

    var task = $("textarea#id_task").val();

    /* get label ids */
    var l_ids = new Array();
    $("span.form-label-wrapper span.form-label").each(function() {
	/* if it is active then we will use the label */
	if ($(this).hasClass('label-edit-active')) {
	    var l_id = $(this).metadata().label_id;
	    l_ids.push(l_id);
	}
    });

    var data = { 'task' : task, 'l_ids' : l_ids }

    /* get priority */
    var pri = $("select#id_priority option:selected").val();
    if (pri != false) {
	/* add priority to data list set to backend */
	data['priority'] = pri;
    }

    /* save to db */
    $.post(getHostName() + url_tasks_api_task_add, 
	   { 'json' : JSON.stringify(data) }, 
	   function (data, status) {
	       if (status == 'success' && data != 'False') {
		   /* do nothing */
		   window.close();
	       }
	   }
	  );
}

/* 
 * ==========
 * AJAX API
 * ==========
 */

/**
 * Adds a task
 *
 * @param t_text Task text
 */
function api_task_add(t_text) {
    if (t_text != "") {
	$.post(getHostName() + url_tasks_api_task_add, 
	       { 'task' : t_text }, 
	       function (data, status) {
		   if (status == 'success' && data != 'False') {
		       /* TODO: update DOM */
		   }
	       }
	      );
    }
}

/**
 * Toggles done/not done status of a task
 */

function api_task_toggle_done(t_id) {
    $.post(getHostName() + url_tasks_api_task_toggle, 
	   { 'task_id' : t_id }, 
	   function (data, status) {
	       if (status == 'success' && data != 'False') {
		   /* nothing */
	       }
	   }
	  );
}

/**
 * Saves the due date for a task 
 * 
 * @param t_id Task ID
 */
function api_task_save_due_date(t_id) {
    /* get date (in form: 2011/12/31) */
    var tr = dom_util_get_task_tr(t_id);
    var date = tr.find("input.due-date-holder").val();
    /* update DB */
    $.post(getHostName() + url_tasks_api_task_date_save, 
	   { 't_id' : t_id,
	     'date' : date }, 
	   function (data, status) {
	       if (status == 'success' && data != 'False') {
		   /* nothing */
	       }
	   }
	  );
}


/*
 * =============
 * DOM functions
 * =============
 */

/**
 * Edit a task
 *
 * NOTE: this function is not used anymore and can be removed 
 * 
 * @param t_id Task ID
 */
function dom_task_edit(t_id) {
    
    var td = $("table.task_table tr#task" + t_id + " td.task a.task_text");
    /* get old task text */
    var old = jQuery.trim(td.text());
    /* ask for updated text */
    var t_text = prompt("Edit task", old);
    /* prompt returns null if cancel was pressed */
    if (t_text == null)
	return; 
    /* trim */
    t_text = jQuery.trim(t_text);
    /* remove from DOM or update DOM */
    if (t_text == "") {
	/* remove task from DOM, it will be deleted in the backend */
	dom_task_delete(t_id);
    } else {
	/* update DOM */
	td.text(t_text);
    }

    /* update DB */
    $.post(getHostName() + url_tasks_api_task_edit, 
	   { 't_id' : t_id, 
	     't_text' : t_text }, 
	   function (data, status) {
	       if (status == 'success' && data != 'False') {
		   /* do nothing */
	       }
	   }
	  );
}

/**
 * Toggles a task between 'done' and 'not done'
 *
 * @param t_id Task ID
 */
function dom_task_toggle(t_id) {

    var tr = dom_util_get_task_tr(t_id);

    if (tr == false)
	return;

    var done = dom_task_done(t_id);

    /* update DOM */
    if (done) {
	/* mark it as not done */
	tr.addClass(css_task_not_done);
	tr.removeClass(css_task_done);
    } else {
	/* mark it as done */
	tr.addClass(css_task_done);
	tr.removeClass(css_task_not_done);
    }

    /* update 'edit button' */
    dom_task_toggle_disable_edit(t_id);

    /* update backend */
    api_task_toggle_done(t_id);

    return false;
}

/**
 * Updates the 'edit button' on a task 
 *
 * This function enables/disables the edit button
 * according to the status of the DOM when the
 * function is called
 *
 * @param t_id Task ID
 */
function dom_task_toggle_disable_edit(t_id) {
    /* get current status */
    var a = $("tr#task" + t_id + " a.task_edit");
    if (a != null) {
	if (dom_task_done(t_id)) {
	    /* hide */
	    a.hide();
	} else {
	    /* show */
	    a.show();
	}
    }
}

/**
 * Returns true if the taks ID is completed, false otherwise
 *
 * @param t_id Task ID
 */
function dom_task_done(t_id) {
    var tr = dom_util_get_task_tr(t_id);
    if (tr == false)
	return false;
    return tr.hasClass(css_task_done);
}


/**
 * Deletes a task from the task table 
 *
 * @param t_id Task ID
 */
function dom_task_delete(t_id) {
    
    var no_trs = $("table.task_table tr#task" + t_id).length;

    if (no_trs > 1) {
	/* we simply need to remove the <tr> from the DOM */
	var tr = dom_util_get_task_tr(t_id);
	if (tr != false)
	    tr.remove();
    } else {
	/* we will remove the last task currently displayed in the DOM */
	/* TODO: we should do something else here */
	var tr = dom_util_get_task_tr(t_id);
	if (tr != false)
	    tr.remove();
    }

}


/*
 * ------------------
 * Labels assignments
 * ------------------
 */

/**
 * Brings up the labeling tools 
 *
 * @param t_id Task ID
 */
function dom_label_task(t_id) {

    /* clear up label tools (from perhaps a previous session) */
    dom_label_task_clearup();

    var names = new Array();
    
    /* iterate user-defined labels  */
    $("ul#folders li.label").each(function() {
	/* extract label id */
	var l_id = $(this).metadata().label_id;
	/* extract label names */
	var label = $(this).find("a").text();
	names.push({ 'l_id' : l_id, 'label' : label});
	/* hide label */
	$(this).hide();
    });

    /* hide system labels */
    $("ul#folders li.system-label-part").each(function() {
	/* hide */
	$(this).hide();
    });

    /* store the task id in a data- attribute */
    $("ul#folders li.user-defined-labels").attr('data-task', t_id);

    /* construct labeling tools */
    var dom = '';
    for (var i = 0; i < names.length; i++) {
	var li = 
	    '<li class="label-edit hand" ' + 
	    'data-label_id="' + '\'' + names[i].l_id + '\'' + '" ' + 
	    'onClick="return dom_label_toggle(\'' + names[i].l_id + '\');" ' + 
	    '>' + 
	    names[i].label + 
	    '</li>';
	dom += li;
    }

    /* get priority */
    var high = dom_task_is_high_priority(t_id); 
    var pri = 'priority-normal';
    if (high)
	pri = 'priority-high';

    /* add 'priority' label */
    var pri = 
	'<li class="label-edit hand priority ' + pri + '" ' +
	'onClick="return dom_label_priority_toggle();"' + 
	'>' + 
	'&nbsp;' + 
	'</li>';
    dom += pri;

    /* insert labeling tools into DOM */
    $("ul#folders li.user-defined-labels").after(dom);

    /* get active labels for this task */
    var l_ids = dom_util_get_task_tr(t_id).metadata().labels;

    /* mark active labels active */
    $("ul#folders li.label-edit").each(function() {
	var l_id = $(this).metadata().label_id;
	if (includes(l_ids, l_id)) {
	    $(this).addClass('label-edit-active');
	}
    });

    /* show 'save' and 'cancel' buttons */
    $("ul#folders li.labeling-buttons").show();

    return false;
}

/**
 * TODO
 *
 * @param l_id Label ID
 * @param labels DOM Array with "data-label_id=[label id]" metadata
 */
function dom_label_toggle_generic(l_id, labels) {

    labels.each(function() {
	var id = $(this).metadata().label_id;
	if (l_id == id) {
	    if ($(this).hasClass('label-edit-active')) {
		$(this).removeClass('label-edit-active');
	    } else {
		$(this).addClass('label-edit-active');
	    }
	}
    });
    
    return false;
}

/**
 * Toggles a label during task creation 
 *
 * @param l_id Label ID
 */
function dom_label_new_task_toggle(l_id) {
    /* toggle */
    var labels = $("form.form-add-task span.form-label");
    var ret = dom_label_toggle_generic(l_id, labels);

    /* add hidden post fields */
    var holder = $("span#form-hidden-holder");
    /* remove old */
    holder.find("input[name='labels']").remove();
    /* create hidden field that matches selected labels */
    var l_ids = [];
    labels.each(function() {
	var l_id = $(this).metadata().label_id;
	if (dom_label_is_active(l_id)) {
	    l_ids.push(l_id);
	}
    });
    var hidden = '<input type="hidden" name="labels" value="' + 
	l_ids.toString() + 
	'" />';
    holder.append(hidden);

    return ret;
}


/**
 * Toogles a label during task labeling
 * 
 * @param l_id Label ID 
 */
function dom_label_toggle(l_id) {
    var labels = $("ul#folders li.label-edit");
    return dom_label_toggle_generic(l_id, labels);
}

/**
 * Returns True if the label is 'active', False otherwise
 *
 * @param l_id Label ID
 */
function dom_label_is_active(l_id) {
    var ret = false;
    $("form.form-add-task span.form-label").each(function() {
	var id = $(this).metadata().label_id;
	if (l_id == id) {
	    if ($(this).hasClass('label-edit-active'))
		ret = true;
	}
    });
    return ret;
}

/**
 * Toggles the 'priority' label during task labeling
 */
function dom_label_priority_toggle() {
    $("ul#folders li.priority").each(function() {
	if ($(this).hasClass('priority-normal')) {
	    /* make priority 'high' */
	    $(this).removeClass('priority-normal');
	    $(this).addClass('priority-high');
	} else {
	    /* make priority 'normal' */
	    $(this).removeClass('priority-high');
	    $(this).addClass('priority-normal');
	}
    });
    
    return false;
}

/**
 * Returns the current priority setting
 * 
 * @returns 'HIG' if 'high', 'NOR' otherwise, 
 *          or False if priorty cannot be found
 */
function dom_get_set_priority() {
    var pri = false;
    $("ul#folders li.priority").each(function() {
	if ($(this).hasClass('priority-high')) {
	    pri = 'HIG';
	} else {
	    pri =  'NOR';
	}
    });
    return pri;
}

/**
 * Clears up the labeling tools and restores the 
 * user-defined labels 
 */
function dom_label_task_clearup() {
    /* remove labeling tools */
    $("ul#folders li.label-edit").remove();
    /* hide 'save' and 'cancel' buttons */
    $("ul#folders li.labeling-buttons").hide();
    /* restore labels */
    $("ul#folders li.label").each(function() {
	/* show label */
	$(this).show();
    });
    /* restore system labels */
    $("ul#folders li.system-label-part").each(function() {
	/* show */
	$(this).show();
    });
}

/**
 * Updates the DOM with metadata 
 *
 * The given task is updated with its label IDs
 *
 * @param t_id Task ID
 * @param l_ids Array of Label IDs
 */
function dom_task_labels_save(t_id, l_ids) {
    var tr = dom_util_get_task_tr(t_id);
    if (tr.length > 0) {
	var data = new Array();
	for (var i = 0; i < l_ids.length; i++) {
	    data.push(l_ids[i]);
	}
	var labels = "[";
	for (var i = 0; i < data.length; i++) {
	    labels += ("'" + data[i] + "'");
	    if (i < (data.length - 1))
		labels += ",";
	}
	labels += "]";
	/* set the data- attribute */
	tr.attr('data-labels', labels);
    }
}

/**
 * Updates the DOM with by setting the appropriate 
 * mini labels for the task that has been edited 
 *
 * @param t_id Task ID
 * @param l_ids Array of Label IDs
 */
function dom_task_minilabels_save(t_id, l_ids) {
    
    /* clear previous mini labels */
    var ul = dom_util_get_task_tr(t_id).find('ul.label-crumbs');
    ul.find('li').remove();

    /* set current mini labels */
    for (var i = 0; i < l_ids.length; i++) {
	/* get label name */
	var name = dom_util_get_label_name(l_ids[i]);
	if (name != null) {
	    var li = '<li><span class="label-small">' + name + '</span></li>';
	    ul.append(li);
	}
    }
}

/**
 * Updates the DOM with priority information 
 *
 * @param t_id Task ID
 * @param pri 'HIG' or 'NOR'
 */
function dom_task_priority_update(t_id, pri) {

    if (pri != 'HIG' && pri != 'NOR')
	return false;

    var tr = dom_util_get_task_tr(t_id);

    /* clear */
    tr.removeClass('priority-high');

    if (pri == 'HIG') {
	tr.addClass('priority-high');
    }
}

/**
 * Checks if a task in the task table is marked as a high
 * priority task
 *
 * @param t_id Task ID
 * @returns True if it is high priority, False otherwise
 */
function dom_task_is_high_priority(t_id) {
    var tr = dom_util_get_task_tr(t_id); 
    if (tr != false) {
	return tr.hasClass('priority-high');
    }
    return false;
}

/**
 * Returns the task table row for a given task ID
 *
 * @param t_id Task ID
 * @returns The jQuery <tr> object if it exists, false otherwise
 */
function dom_util_get_task_tr(t_id) {
    var tr = $("table.task_table tr#task" + t_id);
    if (tr.length <= 0)
	return false;
    return tr;
}

/**
 * Returns the label name if there is one, null otherwise 
 *
 * @param l_id Label ID
 */
function dom_util_get_label_name(l_id) {
    var name = null;
    $("ul#folders li").each(function() {
	id = $(this).metadata().label_id;
	if (id == l_id) {
	    var n = jQuery.trim($(this).text());
	    var regexp = /^(.)+\s\((\d)+\)$/;
	    /* the label names are coming from the 'folders', 
	     * and if they have numbers after them indicating 
	     * number of tasks, it must be removed
	     */
	    if (regexp.test(n)) {
		name = n.substring(0, n.indexOf('('));
	    } else {
		name = n;
	    }
	}
    });
    return name;
}