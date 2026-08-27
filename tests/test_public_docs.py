from pathlib import Path
import re


def docs_text():
    paths=[Path('README.md'),Path('START-HERE.md'),*Path('docs').rglob('*.md')]
    return '\n'.join(p.read_text(errors='ignore') for p in paths)


def test_obsolete_generic_service_names_are_absent():
    t=docs_text()
    for token in ['virtual-io','plant-runtime','conduit-capture']:
        assert token not in t


def test_current_domains_are_present_in_course():
    t=docs_text().lower()
    for token in ['cargo','power management','propulsion','vessel coordinator','modbus tcp','opc ua']:
        assert token in t
