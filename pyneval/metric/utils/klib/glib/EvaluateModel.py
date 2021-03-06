# @Author: guanwanxian
# @Date:   2017-02-17T14:54:30+08:00
# @Email:  guanwanxian@zju.edu.cn
# @Last modified by:   guanwanxian
# @Last modified time: 2017-02-17T16:53:49+08:00
import os
import collections
from PIL import Image
from PIL import ImageDraw
import numpy as np
import tifffile

from pyimagesearch.helpers import sliding_window_2d
from PlotTools import plotMyFigure
from Utils import joinPath
from LabelDefinition import label_d_class

def PredictImageWithSlidingWindow(image_path, window_width, window_height,  session, op, images_placeholder):
    '''PredictImageWithSlidingWindow: Predict Image Patchs With Sliding Window
    Args:
        image_path (string): Path to the image.

    Returns:
        bool: The return value.
    '''
    # Open image
    img = Image.open(image_path)
    print('Image Size: ', img.size)

    # Convert to numpy and plot
    img_arr = np.asarray(img)
    plotMyFigure(img_arr)

    W_R = int(window_width/2)
    H_R = int(window_height/2)
    step_size_w = W_R
    step_size_h = H_R
    circle_R = 3

    imgtest = Image.fromarray(img_arr)
    patchs = []
    patch_labels = []
    patch_softmaxs = []

    for (x, y, window) in sliding_window_2d(img_arr, step_size_h=step_size_h, step_size_w=step_size_w, windowSize=(window_width, window_height)):
        if window.shape[0]!=window_height or window.shape[1]!=window_width:
            continue

        test_img = Image.fromarray(window)
        # test_img = test_img.resize((32,32))
        img_input = np.asarray(test_img)
        img_input = np.reshape(img_input, (32,32,1))
        img_feed = {images_placeholder: [img_input] }

        window_label = session.run(op, feed_dict=img_feed)
        patch_softmaxs.append(window_label[0])
        patch_labels.append((x, y, window_label[0]))

    imgtest = imgtest.convert(mode='RGB')
    draw = ImageDraw.Draw(imgtest)

    for lb in patch_labels:
        if lb[2]==0: # branch
            # The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate
            draw.rectangle([lb[0], lb[1], lb[0]+window_width, lb[1]+window_height]
                            ,outline="red")

            draw.ellipse([lb[0]+W_R-circle_R, lb[1]+H_R-circle_R, lb[0]+W_R+circle_R, lb[1]+H_R+circle_R]
                         , fill="red", outline=None) # "red"
        else: # nonbranch
            draw.rectangle([lb[0], lb[1], lb[0]+window_width, lb[1]+window_height],outline="green")
            draw.ellipse([lb[0]+W_R-circle_R, lb[1]+H_R-circle_R, lb[0]+W_R+circle_R, lb[1]+H_R+circle_R], fill="green", outline=None) # "green"

    plotMyFigure(np.asarray(imgtest))
    del draw


def predImgsInDir(in_dir,
                  model,
                  sc,
                  crop=False,
                  save_out=False,
                  out_dir=None,
                  only_error=True):
    img_names = os.listdir(in_dir)
    img_names = sorted(img_names)
    if save_out:
        resetDir(out_dir)

    true_cnt = 0
    err_imgs = []

    for i in range(len(img_names)):
        img_path = joinPath(in_dir, img_names[i])
        im = tifffile.imread(img_path)
        if crop:
            im = im[4:36,4:36,4:36]

        ## Predict
        X_test = [[im.mean()]]
        if sc:
            X_test = sc.transform(X_test)
        y_test = model.predict(X_test)
        pred_class = label_d_class[y_test[0]]
        ground_truth = label_d_class[int(img_names[i].split('#')[0])]

        if  pred_class== ground_truth:
            true_cnt += 1
            if save_out and not only_error:
                img_save_name = img_names[i]
                copy2(img_path, joinPath(out_dir, img_save_name))
        else:
            img_save_name = 'Actual-%s#'%(pred_class) + '#' + img_names[i]
            err_imgs.append(img_save_name)
            if save_out:
                copy2(img_path, joinPath(out_dir, img_save_name))

    return true_cnt, len(img_names), err_imgs
                                                                                 
def evalModel(img_dirs,
              model,
              sc,
              crop=False,
              save_out=False,
              out_dir=None,
              only_error=True):
    '''Evaluate imgs under each folder of img_dirs, with 'modele'.
    Args:
        img_dirs (string list): folders.
        sc (Scikit-Learn Data Converter).
        model (Any Model implement predict function).
        crop (Bool): whether crop the input image.
        save_out (Bool): Whether save predict result.
        out_dir (String): Dir to save output.
        only_error (Bool): Whether only save wrong predicted images.

    Returns:
        ticks (list of string): name of every dir.
        acc_rates (list of double): accurate of dataset under each different folder.
    '''

    ticks = []
    acc_rates = []

    for img_dir in img_dirs:
        tick = img_dir.strip('/').split('/')[-1]
        true_cnt, all_cnt, err_imgs = predImgsInDir(img_dir,
                                                    model,
                                                    sc,
                                                    crop,
                                                    save_out,
                                                    out_dir,
                                                    only_error)
        acc_rate = true_cnt/all_cnt

        # Add to result
        ticks.append(tick)
        acc_rates.append(acc_rate)

    return ticks, acc_rates
