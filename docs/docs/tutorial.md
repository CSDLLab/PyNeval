## Tutorials

### Quick start

The command line of pyneval is:

    pyneval [-h] [--gold GOLD_PATH] [--test [TEST_PATH1, TEST_PATH2, ...]] 
            [--metric METRIC] [--output OUTPUT_PATH] [--detail DETAIL_PATH] 
            [--config CONFIG_PATH] [--debug DEBUG]

A pair of sample data from BigNeuron are provided, you can use [neuTube](https://www.neutracing.com/) to preview and edit them:

[gold swc data](./swc/gold.swc)

[test_swc_data](./swc/test.swc)

The meaning of each parameter can be found here:

|meaning|cmd|brief_cmd|required|default|range|
| --- | --- | --- | --- | --- | --- |
| path of a gold standard swc file | --gold | -G | T | - |  |
| path of one or several test swc files or folders | --test | -T | T | - |  |
| file different metrics | --metric | -M | T | - | ssd, length, diadem, cn |
| output path of metric score in json | --output | -O | F | no output |  |
| output path of detail metric result in swc | --detail | -D | F | no output | |
| path of config file in json format | --config | -C | F | default config | details in [here]() |

An example of output of Pyneval is(ssd metric is selected as example):
    
    There are 1 test image(s)
    ---------------Result---------------
    avg_score       = 2.27268943225517
    recall          = 1.0
    precision       = 0.9
    ----------------End-----------------

If detail and output path is given, you can find output files in the corresponding folder. 

### Description of metrics and detail of configs
####  SSD metric
|parameter|type|description|
|---|:---:|---|
|threshold_mode|int|mode(1 or 2):<br />1 means static threshold, final threshold equal to ssd_threshold.<br />2 means dynamic threshold, final threshold equal to ssd_threshold * src_node.radius|
|ssd_threshold|float| For each node in gold standard tree, ssd find its closest node in test tree. If the distance of these two nodes is less than ssd_threshold, this node is successfully reconstructed and it will contribute to recall or precision, otherwise the distance will be contribute to ssd score. |
|up_sample_threshold|float|up sample rate of gold standard and test test tree. Smaller sample rate threshold means higher sample rate, denser upsampled tree. 
|scale|tuple(1*3)| scaling of gold and test tree in x,y,z coordinates. 
|debug|boolean|show debug information or not|

Example:

    {
        "threshold_mode": 1,
        "ssd_threshold": 2,
        "up_sample_threshold": 2,
        "scale": [1, 1, 1],
        "debug": False
    }
#### Length metric
|parameter|type|description|
|---|:---:|---|
|radius_mode|int|mode(1 or 2):<br />1 means static threshold, final threshold equal to rad_threshold.<br />2 means dynamic threshold, final threshold equal to rad_threshold * src_node.radius|
|radius_threshold|float|This threshold measures the distance between nodes on gold standard tree and the closest edge on test tree. 
|length_threshold|float|This threshold measures the difference between edges on gold standard tree and their corresponding trace on test tree.  
|scale|tuple(1*3)|scaling of gold and test tree in x,y,z coordinates. |
|debug|boolean|show debug information or not|

Example:
    
    {
        "radius_mode": 1,
        "radius_threshold": 2,
        "length_threshold": 2,
        "scale": [1, 1, 1],
        "debug": False
    }

#### Critical node metric
|parameter|type|description|
|---|:---:|---|
|threshold_distance|float| If the distance of two nodes on two trees is less than this threshold, they are probably matched. 
|scale|tuple(1*3)| scaling of gold and test tree in x,y,z coordinates.|
|true_positive_type|int| Identify the type of true positive nodes in swc. (This and following two parameters may affect the color of nodes in visualization program) | 
|false_negative_type|int| Identify the type of false negative nodes in swc. |
|false_positive_type|int| Identify the type of false positive nodes in swc. |

Example:
    
    {
        "radius_mode": 1,
        "radius_threshold": 2,
        "length_threshold": 2,
        "scale": [1, 1, 1],
        "debug": False
    }

#### DIADEM metric
|parameter|type|description|
|---|:---:|---|
|weight_mode|int|Choose different map between degree and weight.<br/>(a). WEIGHT_DEGREE = 1<br/>weight is the degree of node <br/>(b). WEIGHT_SQRT_DEGREE = 2<br/>weight is the sqrt of degree <br/>(c). WEIGHT_DEGREE_HARMONIC_MEAN = 3<br/>weight is the harmonic mean of degree of left and right son. <br/>(d). WEIGHT_PATH_LENGTH = 4<br/>weight is the length of path from node to its root<br/>|
|remove_spur|boolean| remove spur or not |
|count_excess_nodes|boolean| count excess nodes in test tree or not | 
|list_miss_nodes|boolean| list missed nodes(reconstruct failed nodes) or not|
|list_distant_matches|boolean| distant match means the parent of a branch is not a matched node, but ancestor is. If this branch is matched, they are distant matched| 
|list_continuations_nodes|boolean| Continuation refer to nodes with only one one. List this kind of nodes or not. |
|find_proper_root|boolean| find a pair of matched node as roots of two trees or not |
|scale|tuple(1*3)|scaling of gold and test tree in x,y,z coordinates.|
|xy_threshold|float| node distance threshold in xy surface.|
|z_threshold|float| node distance threshold in z axis. |
|default_xy_path_error_threshold|float| path length difference threshold in xy surface. 
|default_z_path_error_threshold|float| path length difference threshold in z axis. |
|debug|boolean| show debug information or not |

Example:

    {
        "weight_mode": 1,
        "remove_spur": False,
        "count_excess_nodes": True,
        "align_tree_by_root": False,
        "list_miss": True,
        "list_distant_matches": True,
        "list_continuations": True,
        "find_proper_root": True,
        "scale": [1, 1, 1],
        "xy_threshold": 1.2,
        "z_threshold": 0.0,
        "default_xy_path_error_threshold": 0.05,
        "default_z_path_error_threshold": 0.05,
        "local_path_error_threshold": 0.4,
        "debug": False
    }