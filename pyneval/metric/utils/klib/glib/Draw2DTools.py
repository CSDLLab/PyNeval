# @Author: guanwanxian
# @Date:   1970-01-01T08:00:00+08:00
# @Email:  guanwanxian@zju.edu.cn
# @Last modified by:   guanwanxian
# @Last modified time: 2017-02-25T20:57:35+08:00

"""Draw2DTools, providing functions to generate 2d images
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as lines
import matplotlib.transforms as mtransforms
import matplotlib.text as mtext

from Utils import joinPath
from PlotTools import createNewAxes
from ImageUtils import ImgType, OpType
import Draw2DTools as draw2d

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

def generateLines2(img_type):

    lines_array = []
    x0 = int(1 * np.cos(np.pi * 0/180))
    y0 = int(1 * np.sin(np.pi * 0/180))

    x1 = int(5 * np.cos(np.pi * 180/180))
    y1 = int(5 * np.sin(np.pi * 180/180))
    lines_array.append(MyLine([x0, x1], [y0, y1], lw=5, c='k'))

    x1 = int(5 * np.cos(np.pi * 270/180))
    y1 = int(5 * np.sin(np.pi * 270/180))
    lines_array.append(MyLine([x0, x1], [y0, y1], lw=5, c='k'))

    x1 = int(5 * np.cos(np.pi * 45/180))
    y1 = int(5 * np.sin(np.pi * 45/180))
    lines_array.append(MyLine([x0, x1], [y0, y1], lw=5, c='k'))

    return lines_array

def generateLines3(img_type):
    if img_type==ImgType.NonBranch:
        neighbor_number = np.random.randint(1,3)  # 1~2

    else:
        neighbor_number = np.random.randint(3,5) # 3~4
    margin = int(360/neighbor_number)
    print('margin: ', margin)

    lines_array = []
    center_r = np.random.randint(0, 4) # 1~5
    center_angle = np.random.randint(0, 360)
    x0 = int(center_r * np.cos(np.pi * center_angle/180))
    y0 = int(center_r * np.sin(np.pi * center_angle/180))

    for i in range(neighbor_number):
        neighbor_r = np.random.randint(6, 11) # 6~10
        neighbor_angle = np.random.randint(0, margin) + i*margin
        x1 = int(neighbor_r * np.cos(np.pi * neighbor_angle/180))
        y1 = int(neighbor_r * np.sin(np.pi * neighbor_angle/180))

        print(x0, y0, x1, y1, neighbor_angle)
        lines_array.append(MyLine([x0, x1], [y0, y1], lw=5, c='k'))

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

def getVertexSequence(pa,pb, line_width_range):
    ''' Separate va-vb to more segments, and returen the points list as well as line_widths list
    '''
    segs = np.random.randint(20,30)

    pts = [pa]
    for i in range(1,segs):
        pc = tuple([pa[j]+(pb[j]-pa[j])*i*1.0/segs for j in range(2)])
        pts.append(pc)
    pts.append(pb)

    line_widths = []

    line_segs = [([pts[idx][0], pts[idx+1][0]],[pts[idx][1], pts[idx+1][1]]) for idx in range(segs)]
    line_widths = np.linspace(line_width_range[0], line_width_range[1], segs)
#     print(line_segs)
#     print('line width: ',line_widths)
    return line_segs, line_widths

def drawGradLines(ax, line_segs, line_widths):
    for l,w in zip(line_segs, line_widths):
        ax.add_line(MyLine(l[0], l[1], lw=w, c='k'))

def sliceRange(s, t, n):
    arr, step = np.linspace(s, t, n, endpoint=False, retstep=True)
    arr = [(x+step/3, x+step*2/3) for x in arr]
    return arr

def rotMatrix2d(theta):
    c, s = np.cos(theta/180*np.pi), np.sin(theta/180*np.pi)
    M = np.matrix([[c, -s, 0],[s, c, 0],[0, 0, 1]]) # '{} {}; {} {};'.format(c, -s, s, c)
    return M

def transMatrix2d(tx, ty):
    M = np.matrix([[1,0,tx],[0,1,ty],[0,0,1]])
    return M

def transMatrix2dCompose(theta, tx, ty):
    m_r = rotMatrix2d(theta)
    m_t = transMatrix2d(tx, ty)
    return np.matmul(m_t, m_r)

def appendMatrix2d(m, m_add):
    return np.matmul(m, m_add)

def cosAngle(x):
    return np.cos(x/180*np.pi)

def sinAngle(x):
    return np.sin(x/180*np.pi)

def getRandomThetaAndRadiu(theta_range, r_range):
    return np.random.uniform(theta_range[0],theta_range[1]), np.random.randint(r_range[0], r_range[1])

def grow2(m0, ps, theta, r, ax, line_width_range):
    """grow2, 在局部坐标系第一象限绘制
    """
    x = r*cosAngle(theta)
    y = r*sinAngle(theta)

    p = np.array([[x],[y],[1]])
    p_t = np.matmul(m0, p)
    p_t = tuple(np.asarray(p_t).flatten())
#     print(x, y, '\n', p_s,'\n', p_t)
    # ax.add_line(MyLine([ps[0], p_t[0]], [ps[1], p_t[1]], lw=5, c='k'))
    line_segs, line_widths = getVertexSequence(ps, p_t, line_width_range)
    drawGradLines(ax, line_segs, line_widths)

    m1 = transMatrix2dCompose(theta, x, y)
    m0_new = appendMatrix2d(m0, m1)
    return m0_new, p_t

def expand(revert_matrix, start_point, ax, depth, img_type, max_width):
    if depth>0:
        if img_type==ImgType.Branch:
            branch_numbers = np.random.randint(2,4)
            angle_slices = sliceRange(-90, 90, branch_numbers)
            for angle in angle_slices:
                angle_s = angle[0]
                angle_width = angle[1]-angle[0]

                revert_matrix_local = appendMatrix2d(revert_matrix, rotMatrix2d(angle_s))
                theta_range = (0, angle_width)
                radiu_range = (3*depth+1, 3*depth+9)
                local_max_width = max_width
                local_min_width = max_width-np.random.randint(1, 11)
                line_width_range = (local_max_width, local_min_width)
                # line_width_range = (5*depth+15, np.random.randint(5*depth+10, 5*depth+16))
                theta,radiu = getRandomThetaAndRadiu(theta_range, radiu_range)
                revert_matrix_new, start_point_new = grow2(revert_matrix_local,
                                                           start_point,
                                                           theta,
                                                           radiu,
                                                           ax,
                                                           line_width_range)
                expand(revert_matrix_new, start_point_new, ax, depth-1, img_type, local_min_width)

        else: # NonBranch
            angle_s = -40
            angle_width = 80

            revert_matrix_local = appendMatrix2d(revert_matrix, rotMatrix2d(angle_s))
            theta_range = (0, angle_width)
            radiu_range = (8, 14)
            line_width_range = (max_width, np.random.randint(max_width-5,max_width+1))
            theta,radiu = getRandomThetaAndRadiu(theta_range, radiu_range)
            revert_matrix_new, start_point_new = grow2(revert_matrix_local,
                                                       start_point,
                                                       theta,
                                                       radiu,
                                                       ax,
                                                       line_width_range)

def initCanvas():
    fig, ax = createNewAxes(1, 1)

    fig.set_size_inches(10, 10)
    ax.set_xlim(-10,10)
    ax.set_ylim(-10,10)

    return fig,ax



def drawWithGrowing(ax, img_type, dest_path, img_name):
    ax.cla()

    if img_type==ImgType.Branch:
        start_point = (-10, -10, 1)
        revert_matrix = draw2d.transMatrix2d(-10,-10)

        max_width = np.random.randint(30, 131)
        min_width = max_width - np.random.randint(1, 11)
        line_width_range = (max_width, min_width)
        radiu_range = (10,14)
        theta_range = (30,60)
        theta,radiu = draw2d.getRandomThetaAndRadiu(theta_range, radiu_range)
        revert_matrix, start_point = draw2d.grow2(revert_matrix, start_point, theta, radiu, ax, line_width_range)

        expand_depth = 1 + (np.random.uniform()>0.8);
        draw2d.expand(revert_matrix, start_point, ax, expand_depth, img_type, min_width)
    else:
        start_point = (-10, -10, 1)
        revert_matrix = draw2d.transMatrix2d(-10,-10)

        max_width = np.random.randint(100, 131)
        min_width = np.random.randint(max_width-5,max_width+1)
        line_width_range = (max_width, min_width)
        radiu_range = (13,17)
        theta_range = (30,60)
        theta,radiu = draw2d.getRandomThetaAndRadiu(theta_range, radiu_range)
        revert_matrix, start_point = draw2d.grow2(revert_matrix, start_point, theta, radiu, ax, line_width_range)

        draw2d.expand(revert_matrix, start_point, ax, 1, img_type, min_width)

    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(joinPath(dest_path, img_name), pad_inches=0, frameon=False, dpi=4)
    # plt.savefig(joinPath(dest_path, img_name), bbox_inches='tight', pad_inches=0, frameon=False)
