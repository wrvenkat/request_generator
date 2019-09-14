#!/bin/bash
jython_path=/mnt/Academics/Current/Present/Python/Jython/jython-standalone-2.7.0.jar;
java -jar "$jython_path" -m request_generator.html.dom.tests.simple_html_element &&\
java -jar "$jython_path" -m request_generator.html.tests.html_request_builder &&\
java -jar "$jython_path" -m request_generator.html.jquery.tests.jquery_request_builder