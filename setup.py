# coding=utf-8

"""
MIT License

Copyright (c) 2018 Tiny Bees

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
from setuptools import setup

from eclients import __version__

setup(name='eclients',
      version=__version__,
      description='基础封装库',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      author='TinyBees',
      author_email='a598824322@qq.com',
      url='https://github.com/tinybees/eclients',
      packages=['eclients', 'eclients.tinylibs', 'eclients.jsonrpc'],
      entry_points={},
      # requires=['aelog', 'pymongo', 'requests', 'marshmallow', 'ujson', 'flask', "flask-sqlalchemy"],
      install_requires=['aelog>=1.0.3',
                        'pymongo>=3.8.0',
                        'requests>=2.21.0',
                        'marshmallow>=3.0.0rc3',
                        'ujson',
                        'flask>=1.0.2',
                        'sqlalchemy>=1.2.12,<=1.3.23',
                        'flask-sqlalchemy>=2.3.2',
                        'redis>=3.0.0',
                        'pymysql>=0.9.2',
                        'PyYAML>=3.13',
                        'boltons>=18.0.1'],
      python_requires=">=3.5",
      keywords="mongo, redis, http, crud, session",
      license='MIT',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: Chinese (Simplified)',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: MacOS :: MacOS X',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7']
      )
