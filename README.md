# PyNeval

[User Documentation](https://csdllab.github.io/PyNeval_doc/)

## Introduction
PyNeval is a Python package for evaluating the qualities of neuron reconstructions in the [SWC format](http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html). It outputs quality scores of one or more test models by comparing them to a gold standard model. The scores also depend on which metric is specified because PyNeval supports several metric options.

Here is the simplest command line interface to run PyNeval:
```
pyneval --test <test_swc_path> --gold <gold_swc_path> --metric <metric>
```
`test_swc_path` is the file path to a test model, which is often produced by an automatic reconstruction method, and `gold_swc_path` is the file path to the gold standard model, which is typically created by manual editing. `metric` is the name of a quality metric, which can be

* <em>length</em>: Length metric for measuring the overlapping ratio between two models by matching line segments.
* <em>ssd</em>: SSD metric for measuring the overlapping ratio between two models by matching resampled nodes.
* <em>diadem</em>: [DIADEM](http://diademchallenge.org/metric.html) metric for measuring the amount of paths that contribute to topological similarity between two models.
* <em>cn</em>: Critical node metric for measuring the topological similarity between two models by matching topologically critical nodes.

## Installation
### pip
```
pip install pyneval
```

### conda
```
conda install pyneval -c csdllab -c conda-forge
```

### source code

```
git clone https://github.com/bennieHan/pyNeval.git
cd PyNeval
python setup.py install
```

## Example
Once PyNeval is installed successfully, you can test it with the [demo data](https://github.com/CSDLLab/PyNeval/tree/master/data/demo) included in the source code.
```
pyneval --gold data/example/gold.swc --test data/example/test.swc --metric ssd
```