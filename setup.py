# coding: utf-8
from setuptools import setup, find_packages

__author__ = 'damirazo <me@damirazo.ru>'


setup(
    name='Petrovich',
    version='0.1.5',
    description=u'Библиотека для склонения кириллических ФИО по падежам',
    url='https://github.com/damirazo/petrovich',
    author='damirazo',
    author_email='me@damirazo.ru',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Localization',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Russian',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='petrovich python',
    packages=find_packages(),
)
