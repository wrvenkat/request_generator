#!/bin/bash
jython_path=~/Downloads/Jython/jython.jar;
git clone https://github.com/wrvenkat/request_parser.git &&
pwd &&\
mv request_parser/request_parser ../ &&\
java -jar "$jython_path" -m request_generator.html.dom.tests.simple_html_element &&\
java -jar "$jython_path" -m request_generator.html.tests.html_request_builder &&\
java -jar "$jython_path" -m request_generator.html.jquery.tests.jquery_request_builder