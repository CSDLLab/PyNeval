from .glib.DrawSimulationSWCModel import simulate3DTreeModel
from .glib.ImageUtils import gaussianNoisyAddGray3D


def simulator(size,max_depth,base_length,base_x,mean,std):
	img,_,_=simulate3DTreeModel(size,max_depth,base_length,base_x)
	return gaussianNoisyAddGray3D(img,mean,std)


if __name__=='__main__':
	img=simulator(200,5,50,1,30,10)
	print(img)