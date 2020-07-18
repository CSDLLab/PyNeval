# class_2_label = {
#     'bear':0,
#     'bird':1,
#     'cat':2,
#     'dog':3,
#     'giraffe':4,
#     'horse':5,
#     'sheep':6,
#     'zebra':7}


# class_names = list(class_2_label.keys())

class  class2label():
    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
