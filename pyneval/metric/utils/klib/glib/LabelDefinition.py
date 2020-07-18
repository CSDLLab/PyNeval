"""Example Google style docstrings.

This module define the labels for each class images.

"""

label_d_class = {
    0:'branch',
    1:'nonbranch'
}

class_d_label = {
    'branch':0,
    'nonbranch':1
}

class_d_name = {
    'branch':2,
    'nonbranch':1
}

class_names = list(class_d_label.keys())

label_class_names = class_names.copy()
label_class_names.append('none')
LabelPatchSizeRestrict = (32,32)
PlotLabelDir = '/home/guanwanxian/LearnPython/NeuTube/TrainModel/Extra/PlotLabel32by32'
MouseSampleDir = '/home/guanwanxian/LearnPython/NeuTube/TrainModel/Extra/MouseSample32by32'
MouseLabelDir = '/home/guanwanxian/LearnPython/NeuTube/TrainModel/Extra/MouseLabel32by32'
