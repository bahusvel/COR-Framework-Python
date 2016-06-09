#!/usr/bin/env python

from setuptools import setup

setup(
	name='cor',
	version='5.0',
	description='Distributed modular computing framework that runs anywhere',
	author='Denis Lavrov',
	author_email='bahus.vel@gmail.com',
	url='https://github.com/bahusvel/COR-Framework-Python',
	packages=['cor', 'cor.protocol'],
	package_data={'cor.protocol': ['*.proto']},
	install_requires=['py3-protobuffers>=3.0.0a4'],
	provides=['cor'],
	keywords=['distributed', 'modular', 'microservices']
)
