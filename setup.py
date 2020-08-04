from setuptools import setup

setup(name='pyneval',
      version='1.0',
      description='pyneval first edition',
      author='ZhangHan',
      author_email='benniehan98@gmail.com',
      url='https://github.com/bennieHan/PyNeval.git',
      packages=['pyneval', 'cli', 'test', 'test.test_model',
                'test.test_model.diadem_metric', 'test.test_model.length_metric',
                'pyneval.io', 'pyneval.metric', 'pyneval.metric.utils', 'pyneval.metric.utils.klib', 'pyneval.model', 'pyneval.tools'],
      py_modules=['pyneval', 'cli', 'test', 'test.test_model',
                'test.test_model.diadem_metric', 'test.test_model.length_metric',
                'pyneval.io', 'pyneval.metric', 'pyneval.metric.utils', 'pyneval.metric.utils.klib', 'pyneval.model', 'pyneval.tools'],
      install_requires=[
            'anytree>=2.7.2',
            'numpy>=1.17.3',
            'rtree>=0.8'
      ]
)

