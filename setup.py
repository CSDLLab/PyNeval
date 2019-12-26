from setuptools import setup

setup(name='pymets',
      version='1.0',
      description='pymets first edition',
      author='ZhangHan',
      author_email='benniehan98@gmail.com',
      url='https://github.com/bennieHan/PyMets.git',
      packages=['pymets.io', 'pymets.metric', 'pymets.metric.utils','pymets.model'],
      py_modules=['pymets'],
      install_requires=[
            'anytree>=2.7.2',
            'numpy>=1.17.3',
            'rtree>=0.9'
      ]
)