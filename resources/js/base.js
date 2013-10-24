/**
 * URLs
 */
var url_tasks_api_task_add = "api/task/add/";
var url_tasks_api_task_edit = "api/task/edit/";
var url_tasks_api_task_toggle = "api/task/toggle/";
var url_tasks_api_task_labels_save = "api/task/labels/save/";
var url_tasks_api_task_date_save = "api/task/date/save/";

var url_tasks_api_label_add = "api/label/add/";
var url_tasks_api_label_rename = "api/label/rename/";
var url_tasks_api_label_delete = "api/label/del/";
var url_tasks_api_labels_save = "api/labels/save/";
var url_tasks_api_label_save = "api/label/save/";

/**
 * CSS class names
 */
var css_task_done = "task_done";
var css_task_not_done = "task_not_done";

/**
 * Displays status information
 * 
 * @param msg
 */
function ajax_display_status(msg) {
    var m = 
	'<img src="/resources/icons/yes_smaller.png" class="ajax-status-image" alt="Success" />' + msg;
    $('#ajax_status').show().html(m).delay(2000).fadeOut(1000);
}

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

/**
 * Returns the host name
 *
 */
function getHostName() {
  var host = document.location.hostname;
  var port = document.location.port;
  var protocol = document.location.protocol;
  if (port.length <= 0)
    port = "";
  else
    port = ":" + port;
  return protocol + '//' + host + port + '/'; 
}

function useHttp(address) {
  if (address.substring(0, 5) == "https") {
    return "http" + address.substring("https".length);
  }
  // default 
  return address;
}

function trim(str) {
  return str.replace(/^\s+|\s+$/g, '');
}

/**
 * Validates an email address
 *
 * @param value
 * @used
 */
function isValidEmail(value) { 
    return /.+@.+\..+/.test(value);
}

