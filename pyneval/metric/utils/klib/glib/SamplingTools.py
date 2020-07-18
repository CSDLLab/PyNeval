from PIL import Image
from PIL import ImageDraw
import numpy as np
import matplotlib.pyplot as plt
from Utils import joinPath, saveData, setDir
from PlotTools import plotMyFigureOnAxes

def extractSelectedRegion(selected_data):
    img_array = selected_data['image_array']
    W_R = int(selected_data['W_R'])
    H_R = int(selected_data['H_R'])
    # import pdb
    # pdb.set_trace()
    return np.array([img_array[x[1]-H_R:x[1]+H_R, x[0]-W_R:x[0]+W_R] for x in selected_data['selection']['regions']])

def redrawFromSelectedData(ax, selected_data, circle_R=3):
    redraw(ax, Image.fromarray(selected_data['image_array']),
                               selected_data['selection'],
                               selected_data['W_R'],
                               selected_data['H_R'],
                               circle_R)


def redraw(ax, img, selection, W_R, H_R, circle_R):
    """Redraw image presented in numpy format(img) on Matplotlib Axes(ax)
       :ax : Matplotlib axes, where to draw image
       :img : Pillow Image Object
       :selection: {'regions':[], 'count':int}, regions contain the regions to draw
       :W_R : int, half of window width
       :H_R : int, half of window height
    """
    ax.cla()
    img_rgb = img.convert(mode='RGB')
    draw = ImageDraw.Draw(img_rgb)

    for idx, lb in enumerate(selection['regions']):
        if lb[2]==0: # branch
            # The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate
            draw.rectangle([lb[0]-W_R, lb[1]-H_R, lb[0]+W_R, lb[1]+H_R]
                            ,outline="red")

            draw.ellipse([lb[0]-circle_R, lb[1]-circle_R, lb[0]+circle_R, lb[1]+circle_R]
                         , fill="red", outline=None) # "red"
            draw.text((lb[0]-W_R,lb[1]-H_R), '{0}'.format(idx), fill='yellow')
        else: # nonbranch
            draw.rectangle([lb[0]-W_R, lb[1]-H_R, lb[0]+W_R, lb[1]+H_R]
                                ,outline="green")
            draw.ellipse([lb[0]-circle_R, lb[1]-circle_R, lb[0]+circle_R, lb[1]+circle_R]
                         , fill="green", outline=None) # "green"
            draw.text((lb[0]-W_R,lb[1]-H_R), '{0}'.format(idx), fill='yellow')

    del draw

    plotMyFigureOnAxes(ax, np.asarray(img_rgb))
    # im = ax.imshow()
    # fig = ax.figure
    # fig.subplots_adjust(right=0.8)
    # cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    # fig.colorbar(im, cax=cbar_ax)

def checkBoxInside(img_size, x, y, box_w, box_h):
    '''checkBoxInside: Check whether mouse selected region inside
    Args:
        img_size (tuple(int,int)): image size (width, height).
        x (int): x position of box.
        y (int): y position of box.
        box_w (int): width of box.
        box_h (int): height of box.

    Returns:
        bool: Whether box is inside this image.
    '''
    left = x-box_w
    right = x+box_w
    up = y-box_h
    down = y+box_h
    return left>=0 and right<=img_size[0] and up>=0 and down<=img_size[1]


def mouseSample(dst_pckl_path, src_dir, img_name, W_R, H_R, circle_R):
    """mouseSample, use mouse to select [2*W_R, 2*H_R] windows in images
       :dst_pckl_path : string, destination path to store extracted variables
       :src_dir : string, source dir of image
       :img_name : string, image name
       :W_R : int, half window width
       :H_R : int , half window height
       :circle_R : int, radiu of circle drawn on image
    """
    setDir(dst_pckl_path)
    img_path = joinPath(src_dir, img_name)

    img = Image.open(img_path)
    print('Image size: {}'.format(img.size))
    img_size = img.size
    img_array = np.asarray(img)

    selection = {'regions':[], 'count':0}

    # fig_a and fig_b are created differently for each different image
    # and it's okay they are load simultaneously
    fig_a = plt.figure()
    fig_a.clf()
    fig_a_ax = fig_a.add_subplot(111)
    plotMyFigureOnAxes(fig_a_ax, img_array)
    # fig_a_ax.imshow(img_array, cmap='Greys_r')

    fig_b = plt.figure()
    fig_b.clf()
    fig_b_ax = fig_b.add_subplot(111)

    cids = []

    def onclick(event, selection, W_R, H_R, circle_R):
        center_x = int(event.xdata)
        center_y = int(event.ydata)
        fig_b_ax.cla()
        if checkBoxInside(img_size, center_x, center_y, W_R, H_R):
            window = img_array[center_y-H_R:center_y+H_R, center_x-W_R:center_x+W_R]
            window_img = Image.fromarray(window)
            window_arr = np.asarray(window_img)
            plotMyFigureOnAxes(fig_b_ax, window_arr)
            # fig_b_ax.imshow(window_arr,cmap='Greys_r')

            fig_b_ax.text(0,0.4,'img{0}, ({1},{2})'.format(selection['count'], center_x, center_y), color='r')
            selection['count'] += 1
            selection['regions'].append((center_x, center_y, 0))

            redraw(fig_a_ax, img, selection, W_R, H_R, circle_R)
        else:
            fig_b_ax.text(0,0.4,'The box is outside of image', color='r')

    def on_key(event, ax, cids):
        if event.key=='ctrl+alt+n':
            for cid in cids:
                ax.figure.canvas.mpl_disconnect(cid)

            # Save data into a pickl file
            selected_data = {}
            selected_data['selection'] = selection
            selected_data['image_array'] = img_array
            selected_data['img_name'] = img_name
            selected_data['W_R'] = W_R
            selected_data['H_R'] = H_R

            save_pickl_file_name = '_'.join(img_name.split('.')[:-1]).replace('/', '_')
            save_pickl_file_name += '.pckl'

            print('saved pickl file name: {}'.format(save_pickl_file_name))
            saveData([selected_data], joinPath(dst_pckl_path, save_pickl_file_name))

            # Notify
            fig_a_ax.text(0,0.4,'Finishe mouse selection', color='r')

    # Register event handler
    cids.append(fig_a_ax.figure.canvas.mpl_connect('button_press_event', lambda event: onclick(event, selection, W_R, H_R, circle_R)))
    cids.append(fig_a_ax.figure.canvas.mpl_connect('key_press_event', lambda event: on_key(event, fig_a_ax, cids)))
