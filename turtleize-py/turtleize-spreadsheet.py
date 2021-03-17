#!/usr/bin/env python3

"""
This parses the Tech Ethics Curriculum spreadsheet CSV and attempts
to transform it into a Turtle RDF graph.

Usage: python turtleize-spreadsheet.py

"""

import pandas as pd
import rdflib

df = pd.read_csv('tech-ethics-courses.csv')

preamble = """
@prefix ccso: https://w3id.org/ccso/ccso#
@prefix dc: http://purl.org/dc/elements/1.1/
"""


def toList(instructors):
    if type(instructors) != str:
        return [instructors]
    # Handle 'Inst A and Inst B'
    if ' and ' in instructors:
        instructors = instructors.replace(' and ', ', ')
    if ',' in instructors:
        return [inst.strip() for inst in instructors.split(',')]
    return [instructors]


def turtleize(i, row):
    # Handle multiple instructors
    instList = toList(row['INSTRUCTOR'])
    instructors = "  \n".join([f"ccso:hasInstructor \"{inst}\"" for inst in instList])
    worksFors = "\n".join([f"\"{inst}\" ccso:worksFor \"{row['UNIVERSITY']}\"" for inst in instList])
    return f"""
{i} a ccso:Course
  ccso:hasSyllabus "{row['SYLLABUS ']}"
  ccso:offeredBy "{row['DEPARTMENT']}"
  ccso:csName "{row['COURSE TITLE']}"
  {instructors}
  ccso:courseURL "{row['COURSE DESCRIPTION - URL']}"

"{row['DEPARTMENT']}" ccso:memberOf "{row['UNIVERSITY']}"
{worksFors}
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
