# request_generator
request_parser is an object tree builder and code generator for raw HTTP requests.  

request_parser builds object tree and generate code from it for specific languages/frameworks like HTML form, jQuery or XHR. The tree is built from an [`HttpRequest`](https://github.com/wrvenkat/request_parser) object.

## Details
### DOM
A basic unit in an object tree is a `Tag` object defined in the module `tag.py` under the `dom` package. A `Tag` object can be used to define a building unit for any object model. For example, this might be a statement in a programming language like Java or Python or an HTML element.  

The `Tag` class defines basic navigation, search, modification and code generation methods for an object tree.

Specializations and extensions of a `Tag` is possible by inherting to change the behavior. Examples of these are the `simple_html_element.py` and `simple_html_elements.py` modules that extend and specialize `Tag` for generating an HTML element object tree.

### builders
The [`builders`](https://github.com/wrvenkat/request_generator/blob/master/request_generator/builders.py) module enumerates the available build types in the `Type` class.

### request_generator
The [`request_generator`](https://github.com/wrvenkat/request_generator/blob/master/request_generator/request_generator.py) module's `RequestGenerator` class defines the `genereate_request(requests=None, type=None, target_type=None, auto_submit=None)` method which is a single-point entry to build an object-tree and generate the code in a single call.  
`requests`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- an array of `HttpRequest` objects  
`type`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- one of the build types from `Type`  
`target_type`&nbsp;- one of the value from `TargetType` from `html_request_builder` module
`auto_submit`&nbsp;- `True` or `False` if auto submit of request is desired

### request_builder
The [`request_builder`](https://github.com/wrvenkat/request_generator/blob/master/request_generator/request_builder.py) module defines the `RequestBuilder` class which serves as the definition of a minimum API any request builder class needs to provide.

### HTML and jQuery
#### HTML form request and XHR request
The `html_request_builder` module inside `html` package defines the `HtmlRequestBuilder` class. This class implements the `RequestBuilder` interface from `request_builder` module.

This `HtmlRequestBuilder` class implements a builder-generator for form-based and XHR based object tree building and code generation. These two types are listed in the `Type` as `form_request = 0` and `xhr_request = 1`.  

#### jQuery request

#### Encoder
The `html.dom` package has an `Encoder` class that implements to help with proper output encoding during HTML/JS object tree building to prevent context escaping in generated code.