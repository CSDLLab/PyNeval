# pymets
# This is a project still under construstion

## 1. introduction
pymets is a metric tool to judge the reconstruction of neural cells. In other word, judge the difference between the ground truth data (gold) build by human and the test data(test) build by computer.  
## 2. metric method
### 2.1 length metric
It compares two 3D trees base on 3D geometry structure. <br>
LM simple calculates the ratio between the length of gold tree and test tree. <br>
LM overlap calculates the ratio between the length of the overlap part of gold and test trees, and the total length of the gold tree.<br>
LM FP-pernalize lists the wrong matched edge in the test trees. In other words, it shows the edges appear in the test tree but not in the gold tree. FP means false positive.
### 2.2 diadem metirc
It is a metric introduced by Gillette, T. A., Brown. We merge it into our tool as a important part. Detail of this metric can been seen in:<br>
http://diademchallenge.org/metric.html
## 3. How to use
1. clone this project into your computer<br>
`git clone https://github.com/bennieHan/PyMets.git`
2. make sure your enviroment met "requirement"<br>

3. move into the root of this project, it's the place where pymets.py exist.<br>

4. prepare the json config file, the explanation and sample json of different metrics are in `/doc/config`<br>

5. run command line:
  ```
  python ./pymets.py
  --test D:\gitProject\mine\PyMets\test\data_example\test\34_18_10_test.swc
  --gold D:\gitProject\mine\PyMets\test\data_example\gold\30_18_10_gold.swc
  --metric length_metric
  --config D:\gitProject\mine\PyMets\test\length_metric.json
  ```
  the explanation also can been seen in the `doc`<br> 
