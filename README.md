# PyNeval
# This is a project still under construstion

## 1. introduction
pyNeval is a metric tool to judge the reconstruction of neural cells. In other word, judge the difference between the ground truth data (gold) build by human and the test data(test) build by computer.  
## 2. metric method
### 2.1 length metric
It compares two 3D trees base on 3D geometry structure. <br>
LM overlap calculates the ratio between the length of the overlap part of gold and test trees, and the total length of the gold tree.<br>
LM FP-pernalize lists the wrong matched edge in the test trees. In other words, it shows the edges appear in the test tree but not in the gold tree. FP means false positive.
### 2.2 diadem metirc
It is a metric introduced by Gillette, T. A., Brown. We merge it into our tool as a important part. Detail of this metric can been seen in:<br>
http://diademchallenge.org/metric.html
### 2.3 volume metric
This metric is designed for the comparison between Tiff file and Swc model. It calculates the ratio between the number of nodes whose center intensity larger than threshold and the number of all nodes. It is considered as Recall of Swc file compare to Tiff file.(Swc is gold standard and Tiff is test). <br>
### 2.4 branch_leaf_metric
This metric firstly select all the branch nodes or leaf nodes in two different swc models, and seperate them into two sets according to which model they belong to. Then we try to find a weight minimum match for these two sets. This metric's output is the mean distance of the edge in the mininum match. The number of mismatched nodes in gold or test model is optional. 
## 3. other functions
### 3.1 self overlap detect
Their are some self overlaps in the swc models. In other word, sometimes a thick fiber is wrongly represented as several thin fibers. It broughts extra work to some users. So we develop this method to show and delete needless edges. 
### 3.2 up_sample/downsample
Sometimes we are unsatified with the sample rate of the swc model. We need to delete or add some nodes between exist nodes to meet our requirement. So we design a program to adjust the sample rate of the tree.
## 4. How to use
1. clone this project into your computer<br>
`git clone https://github.com/bennieHan/pyNeval.git`<br>
2. move into the root of this project, it's the place where pyneval.py exist.<br>

3. make sure your enviroment met "requirement"<br>
3.1 make a virtual enviroment and activate it, for example:<br>
`conda create -n pyneval_env`<br>
`conda activate pyneval_env`<br>
3.2 install libspatialindex<br>
`conda install -c conda-forge libspatialindex=1.9.3`<br>
3.3 install setuptools if your doesn't have it<br>
`conda install setuptools`<br>
3.4 run setup.py<br>
`python setup.py install`<br>
For users in mainland china, I recommand you to install packages in requirement.txt one by one using aliyun source<br>
`pip install rtree -i https://mirrors.aliyun.com/pypi/simple trusted-host =  mirrors.aliyun.com`<br>
`pip install anythree -i https://mirrors.aliyun.com/pypi/simple trusted-host =  mirrors.aliyun.com`<br>
`pip install numpy -i https://mirrors.aliyun.com/pypi/simple trusted-host =  mirrors.aliyun.com`<br>
when you are done, run setup again.<br>
4. prepare the json config file, the explanation and sample json of different metrics are in `/doc/config`. You can ignore it and program will use default config files<br>

5. run command line:<br>
  5.1 for eazy to copy<br>
  ```
  pyneval --test test\data_example\test\ExampleTest.swc --gold test\data_example\gold\ExampleGoldStandard.swc --metric matched_length  
  ```
  &emsp;&emsp;5.2 for better to understand
  ```
  pyneval
  --test test\data_example\test\ExampleTest.swc 
  --gold test\data_example\gold\ExampleGoldStandard.swc 
  --metric matched_length
  ```
  &emsp;&emsp;the explanation also can been seen in the `doc`<br> 
