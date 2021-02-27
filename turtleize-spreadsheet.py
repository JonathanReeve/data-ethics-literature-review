#!/usr/bin/env python3

"""
This parses the Tech Ethics Curriculum spreadsheet CSV and attempts
to transform it into a Turtle RDF graph.

Usage: python turtleize-spreadsheet.py

"""

import pandas as pd

df = pd.read_csv('tech-ethics-courses.csv')

preamble = """
@prefix ccso: https://w3id.org/ccso/ccso#
@prefix dc: http://purl.org/dc/elements/1.1/
"""


def turtleize(i, row):
    return f"""
{i} a ccso:Course
  ccso:hasSyllabus {row['SYLLABUS ']}
  ccso:offeredBy "{row['DEPARTMENT']}"
  ccso:csName "{row['COURSE TITLE']}"
  ccso:hasInstructor {row['INSTRUCTOR']}
  ccso:courseURL {row['COURSE DESCRIPTION - URL']}

"{row['DEPARTMENT']}" ccso:memberOf "{row['UNIVERSITY']}"
"{row['INSTRUCTOR']}" ccso:worksFor "{row['UNIVERSITY']}"
"""

# print(df.keys())

for i, row in df.iterrows():
    print(turtleize(i, row))

# TODO:
"""
{syllabus} ccso:academicYear ?infer this?
  ccso:hasLM {text}

{text} dc:title {textTitle}

{university} ccso:address ?get this from website?
"""
