#!/usr/bin/env python3

from spreadsheetToGraph import normalizeLanguage, normalizeTopic, normalizeName

def test_normalizeLanguage():
    assert normalizeLanguage("English") == 'en'

def test_normalizeTopic():
    assert normalizeTopic(3.2) == None

def test_normalizeName():
    name = "Jonathan Reeve"
    assert normalizeName("Jonathan Reeve") == ("Reeve", "Jonathan")
    assert normalizeName("Dr. Roland Barthes") == ("Barthes", "Roland")
