# get iframe reference
# arg 1, arg 2 - iframe id index
IFRAME_REF_STMT_TEXT    = """var iframe0 = document.getElementById('iframe0');"""

# Creates a compatible XHR request object
# See https://www.html5rocks.com/en/tutorials/cors/#toc-cross-domain-from-chrome-extensions
# for more information on the functions/statements below
CREATE_XHR_FUNCTION_HDR         =   """function createCORSRequest(method, url) {"""
CREATE_XHR_FUNCTION_STMT_1      =   """var xhr = new XMLHttpRequest();"""
CREATE_XHR_FUNCTION_IF_1        =   """if ("withCredentials" in xhr) {"""
CREATE_XHR_FUNCTION_IF_1_STMT_1 =   """// Check if the XMLHttpRequest object has a "withCredentials" property."""
CREATE_XHR_FUNCTION_IF_1_STMT_2 =   """// "withCredentials" only exists on XMLHTTPRequest2 objects."""
CREATE_XHR_FUNCTION_IF_1_STMT_3 =   """xhr.open(method, url, true);"""
CREATE_XHR_FUNCTION_IF_2        =   """else if (typeof XDomainRequest != "undefined") {"""
CREATE_XHR_FUNCTION_IF_2_STMT_1 =   """// Otherwise, check if XDomainRequest."""
CREATE_XHR_FUNCTION_IF_2_STMT_2 =   """// XDomainRequest only exists in IE, and is IE's way of making CORS requests."""
CREATE_XHR_FUNCTION_IF_2_STMT_3 =   """xhr = new XDomainRequest();"""
CREATE_XHR_FUNCTION_IF_2_STMT_4 =   """xhr.open(method, url);"""
CREATE_XHR_FUNCTION_IF_2_STMT_5 =   """}"""
CREATE_XHR_FUNCTION_IF_3        =   """else"""
CREATE_XHR_FUNCTION_IF_3_STMT_1 =   """// Otherwise, CORS is not supported by the browser."""
CREATE_XHR_FUNCTION_IF_3_STMT_2 =   """xhr = null;"""
CREATE_XHR_FUNCTION_RETURN_STMT =   """return xhr;"""
CREATE_XHR_FUNCTION_FOOTER      =   """}"""

#xhr onreadystatechange with write to iframe
XHR_ONREADYSTATECHANGE_FUNCTION_HDR             = """function onreadystatechangeTrigger(xhr) {"""
XHR_ONREADYSTATECHANGE_FUNCTION_IF_1_START      = """if (xhr.readyState === xhr.DONE) {"""
XHR_ONREADYSTATECHANGE_FUNCTION_IF_1_IF_1       = """if (xhr.status === 0)"""
XHR_ONREADYSTATECHANGE_FUNCTION_IF_1_IF_1_STMT  = """iframe0.src = \"data:text/html;charset=utf-8,\"+'ERROR: Unable to read response status.';"""
XHR_ONREADYSTATECHANGE_FUNCTION_IF_1_IF_2       = """else"""
XHR_ONREADYSTATECHANGE_FUNCTION_IF_1_IF_2_STMT  = """iframe0.src = \"data:text/html;charset=utf-8,\"+xhr.responseText;"""
XHR_ONREADYSTATECHANGE_FUNCTION_IF_1_END        = """}"""
XHR_ONREADYSTATECHANGE_FUNCTION_FOOTER          = """}"""

# arg 1, arg 4, arg 5 - xhr object name index, arg 2 - method, arg 3 - URL
CREATE_XHR_STMT_TEXT_1  =   """var xhr{} = createCORSRequest('{}', '{}');"""
CREATE_XHR_STMT_TEXT_2  =   """if (!xhr{})"""
CREATE_XHR_STMT_TEXT_3  =   """throw new Error('CORS not supported');"""
CREATE_XHR_STMT_TEXT_4  =   """xhr{}.onreadystatechange = function(){{ onreadystatechangeTrigger(xhr"""+"""{}); }};"""

# arg 1 - xhr object name index
XHR_WITH_CREDS_TEXT     =  """xhr{}.withCredentials = true;"""

# XHR add header
# arg 1 - xhr object name index, arg 2 - header name, arg 3 - header value
XHR_HDR_STMT_TEXT       =   """xhr{}.setRequestHeader('{}', '{}');"""

# arg 1 - xhr object name index, arg 2 - the object to be sent as POST, '' if nothing to be sent in body
XHR_SEND                =   """xhr{}.send({});"""

# arg 1 - the formatted value of XHR_SEND, arg 2 - timout value
XHR_TIMEOUT             =   3000
XHR_SEND_TIMEOUT        =   """setTimeout(function(){{ {} }}, {});"""

#sendXHR function
SEND_XHR_FUNCTION_HEADER_TEXT   =   """function sendXHR() {"""
SEND_XHR_FUNCTION_FOOTER_TEXT   =   """}"""
SEND_XHR_FUNCTION_NAME          =   """sendXHR"""

# FormData API for multipart/form-data API
#See: https://stackoverflow.com/questions/9395911/send-a-file-as-multipart-through-xmlhttprequest
# https://developer.mozilla.org/en-US/docs/Web/API/FormData/Using_FormData_Objects

# arg 1 - FormData object index
FORM_DATA_API_TEXT  = """var formData{} = new FormData();"""

# arg 1 - input element id, arg 2 - decoded file variable name, arg 3 - file name
# arg 4 - content-type
XHR_FILE_ASSIGNMENT_STMT_1 = """var files{} = getFiles({}, '{}', '{}');"""
XHR_FILE_ASSIGNMENT_STMT_2 = """var files{} = getFiles({}, {});"""

# arg 1 - FormData object index, arg 2 - param name
# arg 3 - File array object/param value or object
FORM_DATA_FILE_APPEND_TEXT  = """formData{}.append("{}", files{}[0]);"""
FORM_DATA_PARAM_APPEND_TEXT = """formData{}.append("{}", "{}");"""