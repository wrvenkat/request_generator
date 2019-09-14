#!/bin/bash
jython_path=~/Downloads/Jython/jython.jar;
java -jar "$jython_path" -m request_generator.html.dom.tests.simple_html_element &&\
java -jar "$jython_path" -m request_generator.html.dom.tests.simple_html_elements &&\
java -jar "$jython_path" -m request_generator.html.tests.html_request_builder &&\
java -jar "$jython_path" -m request_generator.html.jquery.tests.jquery_request_builder