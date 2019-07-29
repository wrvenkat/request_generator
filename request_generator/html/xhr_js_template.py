# get iframe reference
# arg 1, arg 2 - iframe id index
IFRAME_REF_STMT_TEXT    = """var iframe0 = document.getElementById('iframe0');"""

# Creates a compatible XHR request object
# See https://www.html5rocks.com/en/tutorials/cors/#toc-cross-domain-from-chrome-extensions
# for more information on the functions/statements below
CREATE_XHR_FUNCTION_TEXT1 =  """function createCORSRequest(method, url) {\r\n"""+\
                            """\tvar xhr = new XMLHttpRequest();\r\n"""+\
                            """\tif ("withCredentials" in xhr) {\r\n"""+\
                            """\t\t// Check if the XMLHttpRequest object has a "withCredentials" property.\r\n"""+\
                            """\t\t// "withCredentials" only exists on XMLHTTPRequest2 objects.\r\n"""+\
                            """\t\txhr.open(method, url, true);\r\n"""+\
                            """\t} else if (typeof XDomainRequest != "undefined") {\r\n"""+\
                            """\t\t// Otherwise, check if XDomainRequest.\r\n"""+\
                            """\t\t// XDomainRequest only exists in IE, and is IE's way of making CORS requests.\r\n"""+\
                            """\t\txhr = new XDomainRequest();\r\n"""+\
                            """\t\txhr.open(method, url);\r\n"""+\
                            """\t} else {\r\n"""+\
                            """\t\t// Otherwise, CORS is not supported by the browser.\r\n"""+\
                            """\t\txhr = null;\r\n"""+\
                            """\t}\r\n"""+\
                            """\treturn xhr;"""
CREATE_XHR_FUNCTION_TEXT2 = """}"""

#xhr onreadystatechange with write to iframe
XHR_ONREADYSTATECHANGE_FUNCTION_TEXT1 =  """function onreadystatechangeTrigger(xhr) {\r\n"""+\
                                        """\tif (xhr.readyState === xhr.DONE) {\r\n"""+\
                                        """\t\tif (xhr.status === 0)\r\n"""+\
                                        """\t\t\tiframe0.src = \"data:text/html;charset=utf-8,\"+'ERROR: Unable to read response status.';\r\n"""+\
                                        """\t\telse\r\n"""+\
                                        """\t\t\tiframe0.src = \"data:text/html;charset=utf-8,\"+xhr.responseText;\r\n"""+\
                                        """\t}"""
XHR_ONREADYSTATECHANGE_FUNCTION_TEXT2 = """}"""

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