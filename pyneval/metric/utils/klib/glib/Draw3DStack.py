from functools import reduce
from Obj3D import Point3D, Sphere, Cone, calculateBound, calScaleRatio
import numpy as np
from numpy import linalg as LA
from scipy.spatial import distance_matrix

def getObjList(nodes, graph, node_idx=None):
    if node_idx:
        # 球体索引列表
        sphere_idxs = [node_idx]+list(graph[node_idx])

        sphere_list = [Sphere(Point3D(*nodes[x].pos), nodes[x].r) for x in sphere_idxs]

        # 椎体索引对列表
        cone_idx_pairs  = [(node_idx, x) for x in graph[node_idx]]

        cone_list = [Cone(Point3D(*nodes[p[0]].pos),nodes[p[0]].r,Point3D(*nodes[p[1]].pos),nodes[p[1]].r) for p in cone_idx_pairs]
    else: # Returen all nodes
        sphere_list=[]
        cone_list=[]
        for node_idx in nodes.keys():
            # 加入当前节点对应的球体
            sphere_list.append(Sphere(Point3D(*nodes[node_idx].pos), nodes[node_idx].r))

            # 椎体索引对列表
            cone_idx_pairs  = [(node_idx, x) for x in graph[node_idx] if node_idx<x]
            cone_list_local = [Cone(Point3D(*nodes[p[0]].pos),nodes[p[0]].r,Point3D(*nodes[p[1]].pos),nodes[p[1]].r) \
                               for p in cone_idx_pairs]
            cone_list.extend(cone_list_local)

    return sphere_list, cone_list

def checkSphereV2(mark, sphere, img_shape):
    bbox = list(sphere.calBBox()) # xmin,ymin,zmin,xmax,ymax,zmax
    for i in range(3):
        j = i+3
        if (bbox[i]<0):
            bbox[i] = 0
        if (bbox[j]>img_shape[i]):
            bbox[j] = img_shape[i]
    (xmin,ymin,zmin,xmax,ymax,zmax) = tuple(bbox)
    (x_idxs,y_idxs,z_idxs)=np.where(mark[xmin:xmax,ymin:ymax,zmin:zmax]==0)
    # points=img_idxs[:3, xmin+x_idxs, ymin+y_idxs, zmin+z_idxs] # 3*M
    # points=points.T # M*3
    xs = np.asarray(xmin+x_idxs).reshape((len(x_idxs),1))
    ys = np.asarray(ymin+y_idxs).reshape((len(y_idxs),1))
    zs = np.asarray(zmin+z_idxs).reshape((len(z_idxs),1))
    points=np.hstack((xs,ys,zs))

    sphere_c_mat = np.array([sphere.center_point.toList()]) # 1*3
    # 计算所有点到所有球心的距离
    dis_mat = distance_matrix(points,sphere_c_mat) # M*1

    # 判断距离是否小于半径
    res_idxs = np.where(dis_mat<=sphere.radius)[0]
    mark[xmin+x_idxs[res_idxs], ymin+y_idxs[res_idxs], zmin+z_idxs[res_idxs]] = 255

def checkConeV2(mark, cone, img_shape):
    bbox = list(cone.calBBox()) # xmin,ymin,zmin,xmax,ymax,zmax
    for i in range(3):
        j = i+3
        if (bbox[i]<0):
            bbox[i] = 0
        if (bbox[j]>img_shape[i]):
            bbox[j] = img_shape[i]
    (xmin,ymin,zmin,xmax,ymax,zmax) = tuple(bbox)

    (x_idxs,y_idxs,z_idxs)=np.where(mark[xmin:xmax,ymin:ymax,zmin:zmax]==0)
    # points=img_idxs[:, xmin+x_idxs, ymin+y_idxs, zmin+z_idxs] # 3*M
    # points=points.T # M*3
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
    mark[xmin+x_idxs[l_idx[l_mark][res_idxs]], ymin+y_idxs[l_idx[l_mark][res_idxs]], zmin+z_idxs[l_idx[l_mark][res_idxs]]] = 255
    l_mark[l_idx[l_mark][res_idxs]]=False

    # 计算剩余
    # import pdb
    # pdb.set_trace();
    if r_max>r_min:
        res_idxs = ((r_max-revert_radius_list[l_idx[l_mark]])*height/(r_max-r_min)) >= revert_coor_mat[l_idx[l_mark],2]
        mark[xmin+x_idxs[l_idx[l_mark][res_idxs]], ymin+y_idxs[l_idx[l_mark][res_idxs]], zmin+z_idxs[l_idx[l_mark][res_idxs]]] = 255
        l_mark[l_idx[l_mark][res_idxs]]=False


#@profile
def draw3dStackSparseV2(sphere_list, cone_list, img_shape):
    '''draw3dStack: Draw 3D image stack.
    Args:
        param1 (int): The first parameter.

    Returns:
        bool: The return value.
    '''
    # print('img_shape', img_shape)
    img_total_length = reduce(lambda x,y:x*y, img_shape)

    # 创建原始矩阵
    mark = np.zeros(img_shape, dtype=np.uint8)

    # 对球体进行判断
    for s in sphere_list:
        checkSphereV2(mark, s, img_shape);
    # 对圆台进行判断
    for c in cone_list:
        checkConeV2(mark, c, img_shape);
    ## 绘制
    #mark=np.where(mark==1, 255, 0).astype(np.uint8)
    mark=np.swapaxes(mark,0,2)
    return mark
