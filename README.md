# request_generator
request_parser is an object tree builder and code generator for raw HTTP requests.  

request_parser builds an object tree and generates code from it for specific languages/frameworks like HTML form, jQuery or XHR. The tree is built using an [`HttpRequest`](https://github.com/wrvenkat/request_parser) object.  
Travis status: [![Build Status](https://travis-ci.org/wrvenkat/request_generator.svg?branch=master)](https://travis-ci.org/wrvenkat/request_generator)

## Getting Started
To use request_generator, make sure to have [request_parser](https://github.com/wrvenkat/request_parser) installed or present in `PYTHONPATH`.

Clone the request_generator repository and use it as follows,  
```python
from io import BytesIO

from request_parser.http.request import HttpRequest

from request_generator.html.html_request_builder import RequestBuilder, TargetType
from request_generator.html.jquery.jquery_request_builder import JQueryRequestBuilder
from request_generator.builders import Type

def parse_and_build(requests=None):
    # create an array of HttpRequest objects
    http_requests = []
    for request in requests:
        # create an iterable object out of request bytes
        request_stream = BytesIO(request)
        # create an HttpRequest object for the request
        http_request = HttpRequest(request_stream=request_stream)
        http_requests.append(http_request)

    # parse all the HttpRequest object
    for http_request in http_requests:
        http_request.parse()

    # build an HTML request builder
    html_builder = HtmlRequestBuilder(requests=http_requests)
    # build object tree for from-based request and target as iframe with auto submit to true
    html_builder.build(type=Type.form_request, target_type=TargetType.iframe, auto_submit=auto_submit)
    # generate code
    html_code = html_builder.generate()

    # build a jQuery request builder
    jquery_builder = HtmlRequestBuilder(requests=http_requests)
    # build object tree for jQuery based request and target as iframe with auto submit to true
    jquery_builder.build(target_type=TargetType.iframe, auto_submit=auto_submit)
    # generate code
    jquery_html_code = jquery_builder.generate()
```

## Package and Module Details
### dom
A basic unit in an object tree is a `Tag` object defined in the `tag` module under the `dom` package. A `Tag` object can be used to define a building unit for any type of object tree. For example, this might be a statement in a programming language like Java or Python or an HTML element.  

`Tag` class defines basic navigation, search, modification and code generation methods for an object tree. This `Tag` class is created by forking [beautifulsoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)'s [`PageElement`](https://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/view/head:/bs4/element.py).

Specializations and extensions of a `Tag` is possible by inherting it to change the behavior. The `SimpleHTMLElement` from [`simple_html_element`](https://github.com/wrvenkat/request_generator/blob/master/request_generator/html/dom/simple_html_element.py) for example, forms the basic unit in an HTML object tree. This `SimpleHTMLElement` is further customized in [`simple_html_elements`](https://github.com/wrvenkat/request_generator/blob/master/request_generator/html/dom/simple_html_elements.py) module to create other HTML elements like `IFrame`, `Img`, `Input` etc that make up an HTML object tree.

### builders
The [`builders`](https://github.com/wrvenkat/request_generator/blob/master/request_generator/builders.py) module enumerates the available build types in the `Type` class.

### request_generator
The [`request_generator`](https://github.com/wrvenkat/request_generator/blob/master/request_generator/request_generator.py) module's `RequestGenerator` class defines the `genereate_request(requests=None, type=None, target_type=None, auto_submit=None)` method which is a single-point entry to build an object-tree and generate the code in a single call.  

|     |             |
| ------------- |-------------
|`requests`     | an array of `HttpRequest` objects
|`type`         | one of the build types from `Type`
|`target_type`  | one of the value from `TargetType` from `html_request_builder` module
|`auto_submit`  | `True` or `False` if auto submit of request is desired

### request_builder
The [`request_builder`](https://github.com/wrvenkat/request_generator/blob/master/request_generator/request_builder.py) module defines the `RequestBuilder` class which defines a minimum API any request builder implementation needs to provide.  

|     |
| ------------- |
|`build(*args, **kwargs)`
|`generate(*args, **kwargs)`

### utils
The `utils.utils` module contains the function `get_abs_path(*dirs)` which returns the absolute path constructed by appending a list of `dirs` one after another under the `request_generator` module.

### html.*
* `html.dom.*` - DOM/object tree implementation for HTML
* `html.html_request_builder` - HTML request builder/generator
* `html.js_statements_template` - template code for JS statements
* `html.xhr_js_template` - template code for XHR JS statements
* `html.jquery.jquery_request_builder` - jQuery request builder/generator
* `html.jquery.jquery_js_template` - jQuery statements template

## Building Requests
### HTML and jQuery
#### HTML form request and XHR request
`html.html_request_builder` module defines the `HtmlRequestBuilder` class. This class implements the `RequestBuilder` interface for a builder-generator for form-based and XHR based HTML code. These two types are listed in the `Type` as `form_request = 0` and `xhr_request = 1`.  

|     |             |
| -------------        |-------------
|`build(type=Type.form_request, target_type=TargetType.iframe, auto_submit=False)`             | `type`, the request type - form based request (`Type.form_request`) and XHR based request (`Type.xhr_request`)<br>`target_type`, where responses should be loaded - iframe (`TargetType.iframe`) and new tab (`TargetType.new_tab`)<br>`auto_submit`, when `True` generate JavaScript code to submit requests when page is loaded
|`generate()`      | generate code from the object tree built

**Usage**
```python
# build an HTML request builder
html_builder = HtmlRequestBuilder(requests=http_requests)
# build object tree for from-based request and target as iframe with auto submit to true
# TargetType.new_tab for loading responses in new tab
builder.build(type=Type.form_request, target_type=TargetType.iframe, auto_submit=auto_submit)
# generate code
html_code = html_builder.generate()
```

#### jQuery request
`html.jquery.jquery_request_builder` module defines the `JQueryRequestBuilder` class. This class inherits `HtmlRequestBuilder` for a builder-generator for jQuery based HTML code. This type is listed in the `Type` as `jquery_request = 2`.  

|     |             |
| -------------        |-------------
|`build(target_type=TargetType.iframe, auto_submit=False)`             | `target_type`, where responses should be loaded - iframe (`TargetType.iframe`) and new tab (`TargetType.new_tab`)<br>`auto_submit`, when `True` generate JavaScript code to submit requests when page is loaded
|`generate()`      | generate code from the object tree built

**Usage**
```python
# build an HTML request builder
jquery_builder = JQueryRequestBuilder(requests=http_requests)
# build object tree for from-based request and target as iframe with auto submit to true
# TargetType.new_tab for loading responses in new tab
jquery_builder.build(target_type=TargetType.iframe, auto_submit=auto_submit)
# generate code
jquery_code = jquery_builder.generate()
```

#### Encoder
The `html.dom` package has an `Encoder` class that implements encoding methods based on [OWASP's XSS Prevention Cheatsheet](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.md) to help with proper output encoding during HTML/JS object tree building. This helps prevent context escaping in generated code.