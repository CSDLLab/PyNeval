### upsample
#### import
```
from cli.re_sample import up_sample_swc_tree
```
#### useage
```
up_sample_swc_tree(swc_tree, thres_length=1.0)

:param swc_tree: the tree need to add node(dense)
:param thres_length: control how many nodes to add
:return swc_tree. resampled in this function
```
#### example
```
from pyneval.model.swc_node import SwcTree
from pyneval.io.save_swc import swc_save
from cli.re_sample import up_sample_swc_tree

my_swc_tree = SwcTree()
my_swc_tree.load("your_input_path")
upsampled_swc_tree = up_sample_swc_tree(swc_tree=my_swc_tree, thres_length=1.0)
swc_save(upsampled_swc_tree, "your_output_path")
```

### downsample
#### import
```
from cli.re_sample import down_sample_swc_tree
```
#### useage
```
down_sample_swc_tree(swc_tree, rad_mul=1.50, center_dis=None, stage=0):

:param swc_tree: the tree need to delete node
:param rad_mul: defult=1.5
:param center_dis: defult=None
:param stage: 0: for 2 degree node, delete if one side is two close, 1: for 2 degree node, delete if two sides are two close
:return: swc_tree has changed in this function
```
#### example
```
from pyneval.model.swc_node import SwcTree
from pyneval.io.save_swc import swc_save
from cli.re_sample import down_sample_swc_tree

my_swc_tree = SwcTree()
my_swc_tree.load("your_input_path")
downsampled_swc_tree = down_sample_swc_tree(swc_tree)
swc_save(upsampled_swc_tree, "your_output_path")
```

### overlap_clean
#### import
```
from cli.overlap_detect import overlap_clean
```
#### useage
```
def overlap_clean(swc_tree, out_path, file_name, loc_config=None):
:param swc_tree: input swc tree
:param out_path: output fold path
:param file_name: name your file as you want
:param loc_config:  load config/overlap_clean.json
:return: None, results are saved in out_path as file_name
```
#### example
```
from pyneval.model.swc_node import SwcTree
from pyneval.io.save_swc import swc_save
from cli.re_sample import down_sample_swc_tree
from pyneval.io.read_json import read_json

my_swc_tree = SwcTree()
my_swc_tree.load("your_input_path")
config = read_json("config/overlap_clean.json")

overlap_clean(my_swc_tree, "your_fold", "file_name", config)
```
