from setuptools import setup

setup(name='pyneval',
      version='0.0.7',
      description='pyneval first edition',
      author='ZhangHan',
      author_email='benniehan98@gmail.com',
      url='https://github.com/bennieHan/PyNeval',
      packages=['pyneval', 'pyneval.cli', 'test', 'test.test_model',
                'test.test_model.diadem_metric', 'test.test_model.length_metric',
                'pyneval.io', 'pyneval.metric', 'pyneval.metric.utils', 'pyneval.metric.utils.klib', 'pyneval.model',
                'pyneval.tools', 'pyneval.tools.optimize', 'pyneval.errors'],
      py_modules=['pyneval', 'pyneval.cli', 'test', 'test.test_model',
                'test.test_model.diadem_metric', 'test.test_model.length_metric',
                'pyneval.io', 'pyneval.metric', 'pyneval.metric.utils', 'pyneval.metric.utils.klib', 'pyneval.model',
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
              'pyneval=pyneval.cli.pyneval:run',
              'pyneval_tools=pyneval.cli.pyneval_tools:run',
          ]
      }
)

