## Automatical parameters optimization
As we have developed five different metrics, the reconstruction result could be evaluated quantitatively. So we write a script to search for the best parameters automatically. 
Simulated Annealing is used to find the global optimal result, and the loss value in each iteration is calculated by averaging the precision and recall of ssd metric. 

### 1. Locate the optimization script, data and neutu
![image](https://user-images.githubusercontent.com/32678771/119219334-a150c880-bb17-11eb-8622-9a91873abe10.png)
#### 1.1 Tools and configs of tools: 
##### NEUTU_PATH: 
The reconstruction process relies on neutu(https://github.com/janelia-flyem/NeuTu), the path executable neutu program need to be list. 
In the example, neutu has been added to enviroment variable so only a "neutu" is enough. 
##### METRIC_CONFIG_PATH:
Metric methods such as SSD requires configs in json format too. In most case default configs are enough. 
##### LOG_PATH
The process of tracing in Neutu produce quite a lot of log data prevent us from getting the log about optimization. So we redirect these log to files in this path. 
#### 1.2 Input
The input of contains three parts known as：
##### ORIGIN_PATH：
origin neuron image in TIFF format
##### GOLD_PATH：
gold standard reconstruction result in SWC format
##### CONFIG_PATH：
path of initial parameters of reconstruction

You can create a folder named by FILE_ID in ($Pyneval)/data/optimization/ and name the ORIGIN tiff with FILE_ID_test.tif, name the GOLD swc with  FILE_ID_gold.swc, 
and leave initial parameters of reconstruction with default value. Of course you can ignore FILE_ID and change these PATH as you like. Only make sure you can understand the meaning of these path. 

#### 1.3 OUTPUT
This script provides two output：
##### optimal parameters
the optimal parameters among all the iterations are save in the following path
in ($PyNeval)/config/fake_reconstruction_configs/best_x_{FILE_ID}.json

##### optimal reconstruction result
The optimal reconstruction will be saved in:
TEST_PATH/FILE_ID.swc

### 2. run the script
Once you have confirmed all the path above, run:
```python optimize.py```
in ($Pyneval)/pyneval/tools/optimize/ and waiting for results
![image](https://user-images.githubusercontent.com/32678771/119220480-5a65d180-bb1d-11eb-8b06-733146095c3e.png)

### 3. Adjusting parameters of SA
![image](https://user-images.githubusercontent.com/32678771/119220534-95680500-bb1d-11eb-9e82-7907e3f8291b.png)
All the configs in SA can be adjust in the main function
##### T_max: initial temperature
##### T_min: minimum temperature, script stops if temperature is lower then T_min
##### q:descending rate of T
##### L: number of random loops under each iteration
##### max_stay_counter: script stop if no new optimal value is found after max_stay_counter times of temperature descension.
##### upper, lower: resize the step of random movement in each iteration
