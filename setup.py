try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
readme_file = os.path.join(os.path.dirname(__file__),
                           'README.txt')
long_description = open(readme_file).read()

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent']

setup(author='Daniel Benamy',
      author_email='dbenamy@igicom.com',
      classifiers=classifiers,
      description='Cron for working on projects that use crontabs.',
      long_description=long_description,
      name='devcron',
      py_modules=['devcron'],
      scripts=['devcron.py'],
      url='https://bitbucket.org/dbenamy/devcron/',
      version='0.1',
     )
