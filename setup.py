from setuptools import setup

setup(name='pyneval',
      version='0.0.10',
      description='pyneval first edition',
      author='ZhangHan',
      author_email='benniehan98@gmail.com',
      url='https://github.com/bennieHan/PyNeval',
      packages=['pyneval', 'pyneval.cli', 'pyneval.io', 'pyneval.metric',
                'pyneval.metric.utils', 'pyneval.metric.utils.klib', 'pyneval.model',
                'pyneval.tools', 'pyneval.tools.optimize', 'pyneval.errors'],
      py_modules=['pyneval', 'pyneval.cli', 'pyneval.io', 'pyneval.metric',
                  'pyneval.metric.utils', 'pyneval.metric.utils.klib', 'pyneval.model',
                  'pyneval.tools', 'pyneval.tools.optimize', 'pyneval.errors'],
      install_requires=[
            'anytree>=2.7.2',
            'kdtree>=0.16',
            'numpy>=1.0',
            'rtree>=0.8',
            'jsonschema>=3.2.0',
            'pandas>=1.3.0'
      ],
      entry_points={
          'console_scripts': [
              'pyneval=pyneval.cli.pyneval:run'
          ]
      }
)

