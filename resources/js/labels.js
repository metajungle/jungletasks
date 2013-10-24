
function add_label_new() {
    var label = prompt("Add label", "");
    if (label != null && label != "") {
        label = jQuery.trim(label);
        api_label_add(label);
    }
}

/*
 * ==========
 * GENERAL
 * ==========
 */

function add_label() {
    var label = prompt("Add label", "");
    if (label != null && label != "") {
        label = jQuery.trim(label);
        /* validate */
        var ret = label_validate(label);
        if (ret != 1) {
            alert(ret);
            return false;
        }

        /* update DB */
        api_label_add(label);
    }

    return false;
}

/**
 * Validates a label name.
 *
 * Returns 1 if label validates, String with error otherwise
 *
 * @param label String
 */

function label_validate(label) {
    label = jQuery.trim(label);
    /* check for special names */
    if (label.toLowerCase() == "priority") {
        return 'Priority is a system label and cannot be used.';
    }
    /* check contents */
    /*
    var regexp = /^(\w|' '|[:_-?!])+$/;
    if (!regexp.test(label)) {
	return 'Only alphanumeric, space and :_-?! characters allowed.';
    }
    */

    /* check that the label does not already exist */
    if (dom_label_name_exists(label)) {
        return 'The given label name already exists.';
    }

    return 1;
}


/* 
 * ==========
 * AJAX API
 * ==========
 */

/**
 * Adds a label
 *
 * @param l_text Label text
 */

function api_label_add(l_text) {
    if (l_text != "") {
        $.post(getHostName() + url_tasks_api_label_add, {
                'label': l_text
            },
            function(data, status) {
                if (status == 'success' && data != 'False') {
                    l_id = data.l_id;
                    /* update DOM */
                    dom_label_add(l_id, l_text);
                }
            }
        );
    }
}

/**
 * Saves label information (currently: color and hidden status)
 *
 * @param l_id Label ID
 */

function dom_label_save(l_id) {
    /* get hidden status */
    hidden = dom_label_get_hidden_status(l_id);
    /* get color */
    color = dom_label_get_color(l_id);
    /* update DB */
    $.post(getHostName() + url_tasks_api_label_save, {
            'l_id': l_id,
            'color': color,
            'hidden': hidden ? 'True' : 'False'
        },
        function(data, status) {
            if (status == 'success' && data != 'False') {
                /* set status message */
                ajax_display_status('Label saved');
            }
        }
    );
}

/**
 * Renames a label
 *
 * @param l_id Label ID
 * @param l_text Label text
 */

function api_label_rename(l_id, l_text) {
    $.post(getHostName() + url_tasks_api_label_rename, {
            'l_id': l_id,
            'label': l_text
        },
        function(data, status) {
            if (status == 'success' && data != 'False') {
                /* do nothing */
            }
        }
    );
}


/**
 * Deletes a label
 *
 * @param l_id Label ID
 */

function api_label_delete(l_id) {
    $.post(getHostName() + url_tasks_api_label_delete, {
            'l_id': l_id
        },
        function(data, status) {
            if (status == 'success' && data != 'False') {
                /* nothing */
            }
        }
    );
}

/**
 * Saves color information for ALL labels
 */

function api_labels_save() {
    var data = new Array();
    $("table#label_list tr").each(function() {
        var id = $(this).attr("id");
        var l_id = id.substring("label".length, id.length);
        var color = util_hex_color($(this).find("input").val());
        data.push({
            'id': l_id,
            'color': color
        });
    });
    /* update DB */
    $.post(getHostName() + url_tasks_api_labels_save, {
            'json': JSON.stringify(data)
        },
        function(data, status) {
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
 * Adds a label
 *
 * @param l_id Label ID
 * @param l_text Label text
 */

function dom_label_add(l_id, l_text) {
    var table = $("table#label_list");
    var tr = '<tr id="label' + l_id + '" data-label_id="\'' + l_id + '\'">' +
        '<td class="label_name">' + l_text + '</td>' +
        '<td class="label_color">' +
        '<input id="labelcolor' + l_id + '" ' +
        'type="text" ' +
        'name="labelcolor' + l_id + '" ' +
        'value="#ffff99" /> ' +
        '</td>' +
        '<td><a href="#" onclick="return dom_label_rename(\'' + l_id + '\');"><img class="task_icon" src="/resources/icons/pencil.png" alt="Rename" /></a></td>' +
        '<td class="label_trash">' +
        '<a href="#" onClick="return dom_label_delete(\'' + l_id + '\');"><img src="/resources/icons/trash.png" alt="Delete" /></a></td>' +
        '<td><span style="font-weight: bold;">0</span> (0 total)</td>' +
        '<td class="status_hidden">' +
        '<input  type="checkbox" name="label' + l_id + '_hidden" ' +
        'id="label' + l_id + '_hidden" />' +
        '<label for="label' + l_id + '_hidden">Hidden</label>' +
        '</td>' +
        '</tr>';
    table.append(tr);

    /* activate color picker */
    table.find("tr#label" + l_id).find("input[type=text]").colorPicker();
    /* activate hidden status function */
    table.find("tr#label" + l_id).find("input[type=checkbox]").button().click(function() {
        dom_label_save(l_id);
    });

    if (dom_empty_labels_text_exists()) {
        dom_empty_labels_text_remove();
        dom_add_highlighter_hide();
    }
}

/**
 * Renames a label
 *
 * @param l_id Label ID
 */

function dom_label_rename(l_id) {
    /* get new name */
    var old_label = dom_label_get(l_id);
    var label = prompt("New label name", old_label);

    /* validate */
    var ret = label_validate(label);
    if (ret != true) {
        alert(ret);
        return false;
    }

    if (label != null && label != "") {
        /* update DOM */
        dom_label_set(l_id, label);
        /* update DB */
        api_label_rename(l_id, label);
    }

    /* return false to prevent standard browser action */
    return false;
}

/**
 * Deletes a label
 *
 * @param l_id Label ID
 */

function dom_label_delete(l_id) {

    /* confirm */
    var l = dom_label_get(l_id);
    var ret = confirm('Are you sure you want to delete the label "' + l + '"');
    /* confirm returns: 1 = OK; 0 = Cancel */
    if (ret != 1)
        return false;

    var tr = $("tr#label" + l_id);
    if (tr.length > 0) {
        /* update DOM */
        tr.remove();
        /* update DB */
        api_label_delete(l_id);
    }

    /* re-introduce 'there are no labels' text? */
    if (dom_label_table_is_empty()) {
        dom_label_add_empty_text();
        dom_add_highlighter_show();
    }

    /* return false to prevent standard browser action */
    return false;
}

/**
 * Sets a label name
 *
 * @param l_id Label ID
 * @param l_text Label text
 */

function dom_label_set(l_id, l_text) {
    $("table#label_list tr#label" + l_id + " td.label_name").html(l_text);
}

/**
 * Gets a label name
 *
 * @param l_id Label ID
 */

function dom_label_get(l_id) {
    return $("table#label_list tr#label" + l_id + " td.label_name").html();
}

/**
 * Adds empty labels text
 */

function dom_label_add_empty_text() {
    var p = '<p style="font-weight: bold;">There are no labels here.</p>' +
        '<p style="font-style: italic;">' +
        'Add a label by clicking \'add\' in the top-right corner.' +
        '</p>';
    $("span.labels_empty_holder").append(p);
}

/**
 * Checks if the table of labels is empty
 *
 * @returns True if it is empty, False otherwise
 */

function dom_label_table_is_empty() {
    return $("table#label_list tr").length <= 0;
}

/**
 * Checks to see if there is 'empty labels' text
 * in the DOM
 *
 * @returns True if this is the case, False otherwise
 */

function dom_empty_labels_text_exists() {
    return $("span.labels_empty_holder p").length > 0;
}

/**
 * Removes 'empty labels' text
 */

function dom_empty_labels_text_remove() {
    $("span.labels_empty_holder p").remove();
}

function dom_add_highlighter_show() {
    $("span#add-highlighter").removeClass('hidden');
    $("span#add-highlighter").addClass('visible');
}

/**
 * Hide the 'add' highlighter
 */

function dom_add_highlighter_hide() {
    $("span#add-highlighter").removeClass('visible');
    $("span#add-highlighter").addClass('hidden');
}

/**
 * Returns True if the given label name already exists
 *
 * @param label String
 */

function dom_label_name_exists(label) {
    var exists = false;
    $("table#label_list td.label_name").each(function() {
        var name = jQuery.trim($(this).text());
        if (name.toLowerCase() == label.toLowerCase()) {
            exists = true;
        }
    });
    return exists;
}

/**
 * Returns the color set for the given Label ID in the DOM
 *
 * @param l_id Label ID
 */

function dom_label_get_color(l_id) {
    var tr = dom_util_get_label_tr(l_id);
    if (tr) {
        var color = tr.find("input").attr('value');
        /* strip the '#' in front of the value */
        color = (color.charAt(0) == "#") ? color.substring(1) : color;
        return color;
    }
    return false;
}

/**
 * Returns the label table row for a given label ID
 *
 * @param l_id Label ID
 * @returns The jQuery <tr> object if it exists, false otherwise
 */

function dom_util_get_label_tr(l_id) {
    var tr = $("table#label_list tr#label" + l_id);
    if (tr.length <= 0)
        return false;
    return tr;
}

/**
 * Returns the labels current 'hidden' status in the DOM
 * (a checkbox)
 *
 * Returns true if the label is 'hidden', false otherwise
 *
 * @param l_id Label ID
 */

function dom_label_get_hidden_status(l_id) {
    var tr = dom_util_get_label_tr(l_id);
    if (tr) {
        if (tr.find("td.status_hidden input").attr('checked'))
            return true;
    }
    /* default */
    return false;
}
