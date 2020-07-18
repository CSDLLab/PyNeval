"""Draw2DTools, providing functions to generate 2d images
"""
from functools import reduce
import numpy as np
from scipy.ndimage import filters as ndfilter
import matplotlib.pyplot as plt
import matplotlib.lines as lines
from mpl_toolkits.mplot3d.art3d import Line3D
import matplotlib.transforms as mtransforms
import matplotlib.text as mtext

from .Utils import joinPath
from .PlotTools import createNewSubplot
from .ImageUtils import ImgType, OpType

def randIntList(lower, upper, length):
    random_list = []
    for i in range(length):
        random_list.append(np.random.randint(lower, upper))
    return random_list



def gaussFilter3DVolume(im,sz,sx,sy):
    # s0 = np.random.uniform(1.0,2.0)
    # s1 = np.random.uniform(0.5,1.0)
    # s2 = np.random.uniform(0.5,1.0)

    im = ndfilter.gaussian_filter(im, [sz,sx,sy])
    return im

class MyLine(lines.Line2D):
    def __init__(self, *args, **kwargs):
        # we'll update the position when the line data is set
        self.text = mtext.Text(0, 0, '')
        lines.Line2D.__init__(self, *args, **kwargs)

        # we can't access the label attr until *after* the line is
        # inited
        self.text.set_text(self.get_label())

    def set_figure(self, figure):
        self.text.set_figure(figure)
        lines.Line2D.set_figure(self, figure)

    def set_axes(self, axes):
        self.text.set_axes(axes)
        lines.Line2D.set_axes(self, axes)

    def set_transform(self, transform):
        # 2 pixel offset
        texttrans = transform + mtransforms.Affine2D().translate(2, 2)
        self.text.set_transform(texttrans)
        lines.Line2D.set_transform(self, transform)

    def set_data(self, x, y):
        if len(x):
            self.text.set_position((x[-1], y[-1]))

        lines.Line2D.set_data(self, x, y)

    def draw(self, renderer):
        # draw my label at the end of the line with 2 pixel offset
        lines.Line2D.draw(self, renderer)
        self.text.draw(renderer)

def getVertexSequence(pa,pb, line_width_range):
    ''' Separate va-vb to more segments, and returen the points list as well as line_widths list
        Args:
            pa (tuple): start point
            pb (tuple): end point
            line_width_range (tuple): line width range
    '''
    segs = np.random.randint(20,30)

    pts = [pa]
    for i in range(1,segs):
        pc = tuple([pa[j]+(pb[j]-pa[j])*i*1.0/segs for j in range(3)])
        pts.append(pc)
    pts.append(pb)

    line_widths = []

    line_segs = [([pts[idx][0], pts[idx+1][0]],[pts[idx][1], pts[idx+1][1]],[pts[idx][2], pts[idx+1][2]]) for idx in range(segs)]
    line_widths = np.linspace(line_width_range[0], line_width_range[1], segs)
#     print(line_segs)
#     print('line width: ',line_widths)
    return line_segs, line_widths

def drawGradLines(ax, line_segs, line_widths):
    for l,w in zip(line_segs, line_widths):
        ax.add_line(Line3D(l[0], l[1], l[2], lw=w, c='k'))

def sliceRange(s, t, n):
    assert(t>=1)
    if n>1:
        arr, step = np.linspace(s, t, n, endpoint=False, retstep=True)
        arr = [(x+step/3, x+step*2/3) for x in arr]
    else: # n==1
        step = t - s
        arr = [(s+step/3,s+step*2/3)]
    return arr

def rotMatrix3d(theta, axis):
    '''rotMatrix3d: Given axis and theta, calculate rotation matrix in 3d axes.
    Args:
        theta (int): The negative angle along  right-hand screw rule.
        axis (string): The axis which rotate along with.
            'x','y' or 'z'
    Returns:
        M (numpy array): The rotation matrix.
    '''
    assert axis in ['x','y','z']
    c, s = np.cos(theta/180*np.pi), np.sin(theta/180*np.pi)
    if axis=='x':
        M = np.matrix([[1, 0, 0, 0],
                       [0, c, -s,0],
                       [0, s, c, 0],
                       [0, 0, 0, 1]])
    elif axis=='y':
        M = np.matrix([[c, 0, s, 0],
                       [0, 1, 0,  0],
                       [-s,0, c,  0],
                       [0, 0, 0, 1]])
    else: # 'z'
        M = np.matrix([[c, -s, 0, 0],
                       [s, c,  0,0],
                       [0, 0, 1, 0],
                       [0, 0, 0, 1]])
    return M

def transMatrix3d(tx, ty, tz):
    M = np.matrix([[1,0,0,tx],
                   [0,1,0,ty],
                   [0,0,1,tz],
                   [0,0,0,1]])
    return M

def transMatrix3dCompose(theta_z, theta_y, tx, ty, tz):
    m_r_z = rotMatrix3d(theta_z, 'z')
    m_r_y = rotMatrix3d(theta_y, 'y')
    m_t = transMatrix3d(tx, ty, tz)
    return reduce(np.matmul, [m_t, m_r_y, m_r_z])

def appendMatrix3d(m, m_add):
    return np.matmul(m, m_add)

def cosAngle(x):
    return np.cos(x/180*np.pi)

def sinAngle(x):
    return np.sin(x/180*np.pi)

def getRandomTransformParas(theta_z_range,
                            theta_y_range,
                            r_range):
    theta_z = np.random.uniform(theta_z_range[0],theta_z_range[1])
    theta_y = np.random.uniform(theta_y_range[0],theta_y_range[1])
    r = np.random.randint(r_range[0], r_range[1])
    return theta_z, theta_y, r

def grow3(M, ps, theta_z, theta_y, r, ax, line_width_range):
    """ grow3, 在局部坐标系第一象限绘制
    """
    # Calculate local coordination
    p_l = np.array([[r],[0],[0],[1]])
    m_rot_z = rotMatrix3d(theta_z, 'z')
    m_rot_y = rotMatrix3d(-theta_y, 'y')
    m_rot_all = np.matmul(m_rot_y, m_rot_z)
    p_l = np.matmul(m_rot_all, p_l)

    # Transform to global coordination
    p = np.matmul(M, p_l)
    p = tuple(np.asarray(p).flatten())

    # Draw line segments
    line_segs, line_widths = getVertexSequence(ps, p, line_width_range)
    drawGradLines(ax, line_segs, line_widths)

    M_l = transMatrix3dCompose(theta_z, theta_y, p_l[0], p_l[1], p_l[2])
    M = appendMatrix3d(M, M_l)
    return M, p

def expand(revert_matrix, start_point, ax, depth, img_type, max_width):
    if depth>0:
        # Rotate along z clockwise 90
        revert_matrix = appendMatrix3d(revert_matrix, rotMatrix3d(90, 'y'))

        if img_type==ImgType.Branch:
            branch_numbers = np.random.randint(2,4)
            angle_slices = sliceRange(0, 360, branch_numbers)
            for angle in angle_slices:
                angle_s = angle[0]
                angle_width = angle[1]-angle[0]

                revert_matrix_local = appendMatrix3d(revert_matrix, rotMatrix3d(angle_s, 'z'))
                theta_range = (0, angle_width)
                radiu_range = (3*depth+1, 3*depth+9)
                local_max_width = max_width
                local_min_width = max_width-np.random.randint(1, 11)
                line_width_range = (local_max_width, local_min_width)
                # line_width_range = (5*depth+15, np.random.randint(5*depth+10, 5*depth+16))
                theta_z, theta_y, radiu = getRandomTransformParas(theta_range, (75,85), radiu_range)
                revert_matrix_new, start_point_new = grow3(revert_matrix_local,
                                                           start_point,
                                                           theta_z,
                                                           theta_y,
                                                           radiu,
                                                           ax,
                                                           line_width_range)
                expand(revert_matrix_new, start_point_new, ax, depth-1, img_type, local_min_width)

        else: # NonBranch
            angle_s = 0
            angle_width = 360

            revert_matrix_local = appendMatrix3d(revert_matrix, rotMatrix3d(angle_s, 'z'))
            theta_range = (0, angle_width)
            radiu_range = (8, 14)
            line_width_range = (max_width, np.random.randint(max_width-5,max_width+1))
            theta_z, theta_y, radiu = getRandomTransformParas(theta_range, (75, 85), radiu_range)
            revert_matrix_new, start_point_new = grow3(revert_matrix_local,
                                                       start_point,
                                                       theta_z,
                                                       theta_y,
                                                       radiu,
                                                       ax,
                                                       line_width_range)

def initCanvas3D():
    ax = createNewSubplot(111, projection='3d')

    fig = ax.get_figure()
    fig.set_size_inches(10, 10)
    ax.set_xlim(-10,10)
    ax.set_ylim(-10,10)
    ax.set_zlim(-10,10)
    # ax.set_xlim(-10,10)
    # ax.set_ylim(-10,10)

    return fig,ax


def drawWithGrowing(ax, img_type, dest_path, img_name):
    ax.cla()



    if img_type==ImgType.Branch:
        start_point = (-10, -10,-10, 1)
        revert_matrix = transMatrix3d(-10,-10, -10)

        max_width = np.random.randint(30, 51)
        min_width = max_width - np.random.randint(1, 11)
        line_width_range = (max_width, min_width)
        radiu_range = (15,17)
        theta_z_range = (30,60)
        theta_y_range = (30,60)
        theta_z, theta_y,radiu = getRandomTransformParas(theta_z_range, theta_y_range, radiu_range)
        revert_matrix, start_point = grow3(revert_matrix,
                                                  start_point,
                                                  theta_z,
                                                  theta_y,
                                                  radiu,
                                                  ax,
                                                  line_width_range)

        expand_depth = 1 + (np.random.uniform()>0.8);
        expand(revert_matrix, start_point, ax, expand_depth, img_type, min_width)
    else:
        start_point = (-10, -10, -10, 1)
        revert_matrix = transMatrix3d(-10,-10,-10)

        max_width = np.random.randint(30, 51)
        min_width = np.random.randint(max_width-5,max_width+1)
        line_width_range = (max_width, min_width)
        radiu_range = (20,23)
        theta_z_range = (30,60)
        theta_y_range = (30,60)
        theta_z, theta_y,radiu = getRandomTransformParas(theta_z_range, theta_y_range, radiu_range)
        revert_matrix, start_point = grow3(revert_matrix,
                                           start_point,
                                           theta_z,
                                           theta_y,
                                           radiu,
                                           ax,
                                           line_width_range)

        expand(revert_matrix, start_point, ax, 1, img_type, min_width)

    # plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(joinPath(dest_path, img_name), pad_inches=0, frameon=False, dpi=4)
    # plt.savefig(joinPath(dest_path, img_name), bbox_inches='tight', pad_inches=0, frameon=False)

def generateLines(img_type):
    if img_type==ImgType.NonBranch:
        neighbor_number = np.random.randint(1,3)  # 1~2

    else:
        neighbor_number = np.random.randint(3,5) # 3~4

    lines_array = []
    center_r = np.random.randint(0, 4) # 1~5
    center_angle = np.random.randint(0, 360)
    x0 = int(center_r * np.cos(np.pi * center_angle/180))
    y0 = int(center_r * np.sin(np.pi * center_angle/180))

    for i in range(neighbor_number):
        neighbor_r = np.random.randint(6, 11) # 6~10
        neighbor_angle = np.random.randint(0, 360)
        x1 = int(neighbor_r * np.cos(np.pi * neighbor_angle/180))
        y1 = int(neighbor_r * np.sin(np.pi * neighbor_angle/180))

        # print x0, y0, x1, y1, neighbor_angle
        lines_array.append(MyLine([x0, x1], [y0, y1], lw=20, c='k'))

    return lines_array



def drawImage(img_type, dest_path, img_name):
#     fig = plt.figure()
    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(10, 10)
    ax = plt.gca(xlim=[-10,10],ylim=[-10,10]) # Set x and y range

    lines_array = generateLines(img_type)
    for l in lines_array:
        ax.add_line(l)

    # plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(joinPath(dest_path,img_name), bbox_inches='tight', pad_inches=0, frameon=False, dpi=4)
