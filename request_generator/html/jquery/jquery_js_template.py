#Templates required to generate jQuery/Ajax requests

JQUERY_INCLUDE_SRC  =   """https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"""

JQUERY_DOCUMENT_ONREADY_HDR     =   """$(function(){"""
JQUERY_DOCUMENT_ONREADY_FOOTER  =   """});"""

SUBMIT_AJAX_REQUEST_HDR         =   """const submitAjaxRequest = function(url=undefined, method='GET', data='', contentType='application/octet-stream', successFunction){"""
SUBMIT_AJAX_REQUEST_IF_1_START  =   """if (url == undefined) {"""
SUBMIT_AJAX_REQUEST_IF_1_STMT_1 =   """alert('No URL provided!');"""
SUBMIT_AJAX_REQUEST_IF_1_STMT_2 =   """return;"""
SUBMIT_AJAX_REQUEST_IF_1_END    =   """}"""
SUBMIT_AJAX_REQUEST_FOOTER      =   """}"""

AJAX_BLOCK_HDR          =   """$.ajax({"""
AJAX_BLOCK_URL          =   """url: url,"""
AJAX_BLOCK_TYPE         =   """type: method,"""
AJAX_BLOCK_DATA         =   """data: data,"""
AJAX_BLOCK_CONTENT_TYPE =   """contentType: contentType,"""
AJAX_BLOCK_PROCESS_DATA =   """processData: false,"""
AJAX_BLOCK_SUCCESS      =   """success: successFunction"""
AJAX_BLOCK_FOOTER       =   """});"""

AJAX_BLOCK_SUCCESS_FUNCTION_HDR     =   """const successFunction = function(responseData) {"""
AJAX_BLOCK_CONSOLE_LOG              =   """console.log(responseData);"""
AJAX_BLOCK_SUCCESS_FUNCTION_FOOTER  =   """}"""

#arg 1  -   iframe ID
AJAX_BLOCK_SUCCESS_FUNCTION_IFRAME_SRC_SET  =   """$('#{}').attr('src', 'data:text/html'+responseData);"""
AJAX_BLOCK_SUCCESS_FUNCTION_NEW_TAB_CALL    =   """loadInNewTab(responseData);"""

#Submit button bind
#arg 1  -   button ID
AJAX_SUBMIT_BUTTON_BIND_HDR     =   """$('#{}').bind('click', function() {{"""
AJAX_SUBMIT_BUTTON_BIND_FOOTER  =   """});"""

#create request statement templates
#arg 1 - index, arg 2 - URL of the request
AJAX_REQUEST_URL_STMT           =   """url{} = '{}';"""
#arg 1 - index, arg 2 - Method of the request
AJAX_REQUEST_METHOD_STMT        =   """method{} = '{}';"""
#arg 1 - index, arg 2 - content type of the request
AJAX_REQUEST_CONTENT_TYPE_STMT  =   """contentType{} = '{}';"""
#arg 1 - index, arg 2 - data of the request
AJAX_REQUEST_DATA_STMT_VALUE    =   """data{} = '{}';"""
#arg 1 - index, arg 2 - object name that represents the data of the request
AJAX_REQUEST_DATA_STMT_OBJ      =   """data{} = {};"""

#submitRequest statemtnt
#args  - index of the request
AJAX_SUBMIT_REQUEST_CALL    =   """submitAjaxRequest(url{}, method{}, data{}, contentType{},successFunction);"""

#timeout template
#arg 1 - submitRequest call, arg 2 - timeout value
AJAX_REQUEST_TIMEOUT    =   """setTimeout(function() {{ {} }}, {});"""

#jQuery auto-submit
JQUERY_CLICK_BUTTON     =   """document.getElementById('{}').click();"""
