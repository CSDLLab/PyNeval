
import os
from functools import reduce
from collections import  deque
import numpy as np
import scipy as sp
from numpy import linalg as LA
from scipy.spatial import distance_matrix

from Transformations import rotation_matrix, superimposition_matrix
from SWCExtractor import Vertex
from Obj3D import Point3D, Sphere, Cone, calculateBound, calScaleRatio
from Utils import  Timer
import Draw3DTools
import ImageUtils

def getRandChildNumber():
    ''' Random generate children number of a tree node
        Input:
            None
        Output:
            (int) : Children number
    '''
    return np.random.choice([1,2,3,4], p=[0.5, 0.35, 0.1, 0.05])

def getChildRadius(depth, max_depth):
    if depth==0: # root
        return np.random.choice([3,4,5], p=[0.25,0.5,0.25])
    else:
        return np.random.choice([1,2,3,4,5], p=[0.05, 0.2, 0.35, 0.35, 0.05])

def getChildLength(depth, max_depth):
    ''' 子节点距离父节点的长度
    '''
    return 25 + (max_depth-depth) + np.random.randint(0,11)

def getNodeFromMark(mark, pos, MIN_DISTANCE, MAX_DISTANCE, mark_shape, use_parent=False, parent_pos=None):

    # Calculate general search range
    x,y,z = pos
    bbox = [x-MAX_DISTANCE, y-MAX_DISTANCE, z-MAX_DISTANCE, x+MAX_DISTANCE+1, y+MAX_DISTANCE+1, z+MAX_DISTANCE+1] # xmin,ymin,zmin,xmax,ymax,zmax
    for i in range(3):
        j = i+3
        if (bbox[i]<0):
            bbox[i] = 0
        if (bbox[j]>mark_shape[i]):
            bbox[j] = mark_shape[i]
    (xmin,ymin,zmin,xmax,ymax,zmax) = tuple(bbox)

    (x_idxs,y_idxs,z_idxs)=np.where(mark[xmin:xmax,ymin:ymax,zmin:zmax]==0)

    if not use_parent:
        if len(x_idxs) > 0:
            xs = np.asarray(xmin+x_idxs).reshape((len(x_idxs),1))
            ys = np.asarray(ymin+y_idxs).reshape((len(y_idxs),1))
            zs = np.asarray(zmin+z_idxs).reshape((len(z_idxs),1))
            points=np.hstack((xs,ys,zs))

            # 计算所有点到中心点的距离
            center_point = np.array([pos]) # 1*3
            dis_mat = distance_matrix(points, center_point) # M*1

            # 判断距离是否小于半径
            res_idxs = np.where(np.logical_and(MIN_DISTANCE<dis_mat, dis_mat<MAX_DISTANCE))[0]

            if len(res_idxs)>0:
                child_choose = np.random.choice(res_idxs)
                child_pos = (xmin+x_idxs[child_choose], ymin+y_idxs[child_choose], zmin+z_idxs[child_choose])
                return child_pos
            else:
                return None
        else:
            return None
    else:
        if len(x_idxs) > 0:
            xs = np.asarray(xmin+x_idxs-x).reshape((len(x_idxs),1))
            ys = np.asarray(ymin+y_idxs-y).reshape((len(y_idxs),1))
            zs = np.asarray(zmin+z_idxs-z).reshape((len(z_idxs),1))
            points=np.hstack((xs,ys,zs)) # M*3
            parent_vec = np.array([[parent_pos[0]-pos[0]],
                                   [parent_pos[1]-pos[1]],
                                   [parent_pos[2]-pos[2]]]) # 3*1

            # 计算所有点到中心点的距离
            dis_mat = LA.norm(points, axis=1) # M*1
            dis_mat = dis_mat.reshape((dis_mat.shape[0],1))

            # 计算与parent_vec的夹角，保证是向外生长的
            angle_mat = np.matmul(points, parent_vec) # M*1

            # 判断距离是否小于半径
            res_idxs = np.where(np.logical_and(angle_mat<0, dis_mat<MAX_DISTANCE))[0]

            if len(res_idxs)>0:
                child_choose = np.random.choice(res_idxs)
                child_pos = (xmin+x_idxs[child_choose], ymin+y_idxs[child_choose], zmin+z_idxs[child_choose])
                return child_pos
            else:
                return None
        else:
            return None

def setMarkWithSphere(mark, sphere, mark_shape, value, use_bbox=False):
    bbox = list(sphere.calBBox()) # xmin,ymin,zmin,xmax,ymax,zmax
    for i in range(3):
        j = i+3
        if (bbox[i]<0):
            bbox[i] = 0
        if (bbox[j]>mark_shape[i]):
            bbox[j] = mark_shape[i]
    (xmin,ymin,zmin,xmax,ymax,zmax) = tuple(bbox)
    (x_idxs,y_idxs,z_idxs)=np.where(mark[xmin:xmax,ymin:ymax,zmin:zmax]==0)
    # points=img_idxs[:3, xmin+x_idxs, ymin+y_idxs, zmin+z_idxs] # 3*M
    # points=points.T # M*3
    if not use_bbox:
        xs = np.asarray(xmin+x_idxs).reshape((len(x_idxs),1))
        ys = np.asarray(ymin+y_idxs).reshape((len(y_idxs),1))
        zs = np.asarray(zmin+z_idxs).reshape((len(z_idxs),1))
        points=np.hstack((xs,ys,zs))

        sphere_c_mat = np.array([sphere.center_point.toList()]) # 1*3
        # 计算所有点到所有球心的距离
        dis_mat = distance_matrix(points,sphere_c_mat) # M*1

        # 判断距离是否小于半径
        res_idxs = np.where(dis_mat<=sphere.radius)[0]
        mark[xmin+x_idxs[res_idxs], ymin+y_idxs[res_idxs], zmin+z_idxs[res_idxs]] = value
    else:
        mark[xmin+x_idxs, ymin+y_idxs, zmin+z_idxs] = value

def setMarkWithCone(mark, cone, mark_shape, value, use_bbox=False):
    bbox = list(cone.calBBox()) # xmin,ymin,zmin,xmax,ymax,zmax
    for i in range(3):
        j = i+3
        if (bbox[i]<0):
            bbox[i] = 0
        if (bbox[j]>mark_shape[i]):
            bbox[j] = mark_shape[i]
    (xmin,ymin,zmin,xmax,ymax,zmax) = tuple(bbox)

    (x_idxs,y_idxs,z_idxs)=np.where(mark[xmin:xmax,ymin:ymax,zmin:zmax]==0)
    if not use_bbox:
        xs = np.asarray(xmin+x_idxs).reshape((len(x_idxs),1))
        ys = np.asarray(ymin+y_idxs).reshape((len(y_idxs),1))
        zs = np.asarray(zmin+z_idxs).reshape((len(z_idxs),1))
        ns = np.ones((len(z_idxs),1))
        points=np.hstack((xs,ys,zs,ns))

        # 每个圆锥的还原矩阵
        r_min=cone.up_radius
        r_max=cone.bottom_radius
        height=cone.height
        cone_revert_mat = cone.revertMat().T # 4*4

        # 每个椎体还原后坐标
        revert_coor_mat = np.matmul(points, cone_revert_mat) # M*4
        revert_radius_list = LA.norm(revert_coor_mat[:,:2], axis=1) # M

        # Local Indexs
        M = points.shape[0]
        l_idx = np.arange(M) # M (1-dim)
        l_mark = np.ones((M,), dtype=bool)

        # 过滤高度在外部的点
        res_idxs = np.logical_or(revert_coor_mat[l_idx[l_mark],2]<0, revert_coor_mat[l_idx[l_mark],2]>height)
        l_mark[l_idx[l_mark][res_idxs]]=False

        # 过滤半径在外部的点
        res_idxs = revert_radius_list[l_idx[l_mark]]>r_max
        l_mark[l_idx[l_mark][res_idxs]]=False

        # 过滤半径在内部的点
        res_idxs = revert_radius_list[l_idx[l_mark]]<=r_min
        mark[xmin+x_idxs[l_idx[l_mark][res_idxs]], ymin+y_idxs[l_idx[l_mark][res_idxs]], zmin+z_idxs[l_idx[l_mark][res_idxs]]] = value
        l_mark[l_idx[l_mark][res_idxs]]=False

        # 计算剩余
        if r_max>r_min:
            res_idxs = ((r_max-revert_radius_list[l_idx[l_mark]])*height/(r_max-r_min)) >= revert_coor_mat[l_idx[l_mark],2]
            mark[xmin+x_idxs[l_idx[l_mark][res_idxs]], ymin+y_idxs[l_idx[l_mark][res_idxs]], zmin+z_idxs[l_idx[l_mark][res_idxs]]] = value
            l_mark[l_idx[l_mark][res_idxs]]=False
    else:
        mark[xmin+x_idxs, ymin+y_idxs, zmin+z_idxs] = value

def simulate3DTree():
    MAX_TREE_DEPTH = 4
    MAX_RADIUS = 6
    SAFE_DISTANCE = MAX_RADIUS + 2

    MAX_DISTANCE = 16

    mark_shape = (251,251,251)

    # Init space
    mark = np.zeros(mark_shape, dtype=np.uint8)
    mark_shape = mark.shape
    node_count = 0

    # Create root node
    root_r = getChildRadius(0,MAX_TREE_DEPTH)
    root_pos = (125,125,125)
    node_count += 1
    root_node = Vertex(node_count,0,root_pos[0],root_pos[1],root_pos[2],root_r,-1)
    setMarkWithSphere(mark, Sphere(Point3D(*root_node.pos), root_node.r), mark_shape, 255)
    # setMarkWithSphere(mark, Sphere(Point3D(*root_node.pos), root_node.r + SAFE_DISTANCE), mark_shape, 1)

    # Creante dequeue and list to contain result
    dq = deque([(root_node, 0)]) # 第二项表示node节点的depth
    nodes = {}
    graph = {}

    while len(dq):
        root_node = dq[0][0]
        root_depth = dq[0][1]
        dq.popleft()

        # Add to nodes and graph
        v1 = root_node.idx
        v2 = root_node.p_idx
        if root_node.idx not in nodes:
            nodes[root_node.idx] = root_node
        if v1>0 and v2>0:
            if not v1 in graph:
                graph[v1] = set([v2])
            else:
                graph[v1].add(v2)

            if not v2 in graph:
                graph[v2] = set([v1])
            else:
                graph[v2].add(v1)

        if root_depth<MAX_TREE_DEPTH:
            # Get children number
            if root_node.idx==1: # 根节点与其他节点单独处理
                child_num = 4
                mask = np.array([[1,1,1],
                                 [-1,1,1],
                                 [1,1,-1],
                                 [-1,1,-1]])
                for i in range(4):
                    # 获取分支半径和长度
                    child_r = getChildRadius(root_depth+1,MAX_TREE_DEPTH)
                    child_length = getChildLength(root_depth+1,MAX_TREE_DEPTH)

                    #theta_z = np.random.uniform(30,60)
                    theta_y = 45
                    #A = rotation_matrix(theta_z/180*np.math.pi, [0,0,1])
                    B = rotation_matrix(-theta_y/180*np.math.pi, [0,1,0])
                    # rot_mat = np.matmul(A,B)
                    p0 = np.array([[child_length],[0],[0],[1]])
                    p1 = np.matmul(B, p0)
                    child_pos = (int(p1[0]*mask[i][0]+root_node.pos[0]), \
                                 int(p1[1]*mask[i][1]+root_node.pos[1]), \
                                 int(p1[2]*mask[i][2]+root_node.pos[2]))
                    if ImageUtils.bboxCheck3D(child_pos[0], child_pos[1], child_pos[2], child_r, mark_shape):
                        node_count += 1
                        #print('parent', root_node.idx, 'id', node_count, 'pos', child_pos, 'depth', root_depth+1)
                        child_node = Vertex(node_count, 0, child_pos[0], child_pos[1], child_pos[2], child_r, root_node.idx)
                        # 绘制
                        setMarkWithSphere(mark, Sphere(Point3D(*child_node.pos), child_node.r), mark_shape, 255)
                        setMarkWithCone(mark, Cone(Point3D(*root_node.pos), root_node.r, \
                                                   Point3D(*child_node.pos), child_node.r), mark_shape, 255)

                        # Add to dequeue
                        dq.append((child_node, root_depth+1))
            else:

                child_num = getRandChildNumber()
                child_angles_range = Draw3DTools.sliceRange(0, 360, child_num)

                for i in range(child_num):

                    # 获取分支半径和长度
                    child_r = getChildRadius(root_depth+1,MAX_TREE_DEPTH)
                    child_length = getChildLength(root_depth+1,MAX_TREE_DEPTH)

                    # 获取生长角度
                    if child_num==1:
                        theta_z = np.random.uniform(0,360)
                        theta_y = np.random.uniform(60,90)
                    else:
                        theta_z = np.random.uniform(child_angles_range[i][0],child_angles_range[i][1])
                        theta_y = np.random.uniform(30,70)

                    A = rotation_matrix(theta_z/180*np.math.pi, [0,0,1])
                    B = rotation_matrix(-theta_y/180*np.math.pi, [0,1,0])
                    rot_mat = np.matmul(A,B)
                    p0 = np.array([[child_length],[0],[0],[1]])
                    p1 = np.matmul(rot_mat, p0)

                    grand_node = nodes[root_node.p_idx] # root节点的父节点
                    p_a = Point3D(0,0,0)
                    p_c = Point3D(root_node.pos[0]-grand_node.pos[0], \
                                  root_node.pos[1]-grand_node.pos[1], \
                                  root_node.pos[2]-grand_node.pos[2])
                    p_b = p_a.medianWithPoint(p_c)
                    v1=np.array([[p_a.x, p_b.x, p_c.x],
                                 [p_a.y, p_b.y, p_c.y],
                                 [p_a.z, p_b.z, p_c.z],
                                 [   1,    1,    1]])
                    Dis=p_a.distanceWithPoint(p_c)
                    v0=np.array([[0,     0,   0],
                                 [0,     0,   0],
                                 [-Dis, -Dis/2, 0],
                                 [1,     1,  1]])
                    rev_mat = superimposition_matrix(v0,v1)
                    p2 = np.matmul(rev_mat, p1)
                    child_pos = (int(p2[0]+grand_node.pos[0]), int(p2[1]+grand_node.pos[1]), int(p2[2]+grand_node.pos[2]))
                    if ImageUtils.bboxCheck3D(child_pos[0], child_pos[1], child_pos[2], child_r, mark_shape):
                        node_count += 1
                        #print('parent', root_node.idx, 'id', node_count, 'pos', child_pos, 'depth', root_depth+1)
                        child_node = Vertex(node_count, 0, child_pos[0], child_pos[1], child_pos[2], child_r, root_node.idx)
                        # 绘制
                        setMarkWithSphere(mark, Sphere(Point3D(*child_node.pos), child_node.r), mark_shape, 255)
                        setMarkWithCone(mark, Cone(Point3D(*root_node.pos), root_node.r, \
                                                   Point3D(*child_node.pos), child_node.r), mark_shape, 255)

                        # Add to dequeue
                        dq.append((child_node, root_depth+1))

    mark = np.where(mark==255, 255, 0).astype(np.uint8)
    mark = np.swapaxes(mark, 0, 2)
    return mark, nodes, graph
