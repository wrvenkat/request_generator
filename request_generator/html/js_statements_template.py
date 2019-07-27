AUTO_SUBMIT_JS_STMT_TEMPLATE = """setTimeout( function() {{ document.getElementById('{}').submit(); }}, {});"""

#used to generate the file assignment to file type input
MULTI_PART_ENCODED_FILE_NAME    = 'file{}_encoded'
MULTI_PART_DECODED_FILE_NAME    = 'file{}_decoded'

#used to construct the file assignment to file type input
MULTI_PART_FILE_JS_ENCODED_STMT         = """var {} = '{}';"""
MULTI_PART_FILE_JS_DECODED_STMT         = """var {} = window.atob({});"""
MULTI_PART_FILE_INPUT_ASSIGNMENT_STMT_1 = """fileToUpload{}.files = getFile({}, '{}', '{}');"""
MULTI_PART_FILE_INPUT_ASSIGNMENT_STMT_2 = """fileToUpload{}.files = getFile({}, {});"""

#used to generate getFile JS function
GET_FILE_FUNCTION_HEADER        = 'function getFile(file_content, file_name, content_type) {'
GET_FILE_FUNCTION_FOOTER        = '}'
JS_COMMENT                      = '\t// Firefox < 62 workaround exploiting https://bugzilla.mozilla.org/show_bug.cgi?id=1422655'
DATA_TRANSFER_JS_CLIPBOARD_STMT = """\tconst dataTransfer = new ClipboardEvent('').clipboardData || """
DATA_TRANSFER_JS_STMT           = '\tnew DataTransfer(); // specs compliant (as of March 2018 only Chrome)'
IF_CONDN                        = '\tif (content_type != undefined)'
IF_TRUE                         = '\t\tdataTransfer.items.add(new File([file_content], file_name, {type : content_type}));'
ELSE_STMT                       = '\telse'
IF_FALSE                        = '\t\tdataTransfer.items.add(new File([file_content], file_name));'
RETURN_STMT                     = '\treturn dataTransfer.files;'