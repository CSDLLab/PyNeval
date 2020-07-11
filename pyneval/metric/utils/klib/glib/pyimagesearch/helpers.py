# @Author: guanwanxian
# @Date:   1970-01-01T08:00:00+08:00
# @Email:  guanwanxian@zju.edu.cn
# @Last modified by:   guanwanxian
# @Last modified time: 2016-12-27T20:24:14+08:00



# import the necessary packages
# import imutils

def pyramid(image, scale=1.5, minSize=(30, 30)):
	original_proportion = 1

	# yield the original image
	yield (original_proportion, image)

	# keep looping over the pyramid
	while True:
		# compute the new dimensions of the image and resize it
		w = int(image.shape[1] / scale)
		image = imutils.resize(image, width=w)
		original_proportion = original_proportion * scale
		# if the resized image does not meet the supplied minimum
		# size, then stop constructing the pyramid
		if image.shape[0] < minSize[1] or image.shape[1] < minSize[0]:
			break

		# yield the next image in the pyramid
		yield (original_proportion, image)

def sliding_window(image, stepSize, windowSize):
	# slide a window across the image
	for y in xrange(0, image.shape[0], stepSize):
		for x in xrange(0, image.shape[1], stepSize):
			# yield the current window
			yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])

def sliding_window_2d(image, step_size_h, step_size_w, windowSize):
	# slide a window across the image
	for y in range(0, image.shape[0], step_size_h):
		for x in range(0, image.shape[1], step_size_w):
			# yield the current window
			yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])


def slidingWindow3D(image, step_size, window_size):
	''' slide a window across the image
		Input:
			image (3d numpy array): z,y,x order.
			step_size (int).
			window_size (int).
		Output:
			(3d numpy array).
	'''
	for y in range(0, image.shape[1], step_size):
		for x in range(0, image.shape[2], step_size):
			for z in range(0, image.shape[0], step_size):
				img = image[z:z+window_size, y:y+window_size, x:x+window_size]
				if img.shape[0]==window_size and img.shape[1]==window_size and img.shape[2]==window_size:
					yield (z,y,x,img)
