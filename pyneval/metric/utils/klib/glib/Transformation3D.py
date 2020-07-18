# @Author: guanwanxian
# @Date:   1970-01-01T08:00:00+08:00
# @Email:  guanwanxian@zju.edu.cn
# @Last modified by:   guanwanxian
# @Last modified time: 2017-02-25T21:24:37+08:00

import numpy as np

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
