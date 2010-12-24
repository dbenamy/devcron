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

setup(name='devcron',
      version='0.1',
      py_modules=['devcron'],
      classifiers=classifiers,
      description='Cron for developing projects that use crontabs.',
      long_description=long_description,
      author='Daniel Benamy',
      author_email='dbenamy@igicom.com',
      url='https://bitbucket.org/dbenamy/devcron/',
      license='MIT',
     )
