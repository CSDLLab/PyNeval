# @Author: guanwanxian
# @Date:   1970-01-01T08:00:00+08:00
# @Email:  guanwanxian@zju.edu.cn
# @Last modified by:   guanwanxian
# @Last modified time: 2017-02-25T21:13:32+08:00

import numpy as np

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
