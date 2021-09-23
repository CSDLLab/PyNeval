

def get_f1score(recall, precision):
    if recall == 0 and precision == 0:
        return 0
    return 2*recall*precision/(recall+precision)
