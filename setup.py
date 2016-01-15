# To use a consistent encoding
from codecs import open
import os
from setuptools import setup

readme_file = os.path.join(os.path.dirname(__file__),
                           'README.md')
long_description = open(readme_file, encoding='utf-8').read()

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',

    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
]

setup(author='Daniel Benamy',
      author_email='daniel@benamy.info',
      classifiers=classifiers,
      description='Cron for working on projects that use crontabs.',
      long_description=long_description,
      name='devcron',
      py_modules=['devcron'],
      scripts=['devcron.py'],
      url='https://bitbucket.org/dbenamy/devcron/',
      version='0.2',
      entry_points={
          'console_scripts': [
              'devcron=devcron:main',
          ],
      })
