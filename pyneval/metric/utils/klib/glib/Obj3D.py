# @Author: guanwanxian
# @Date:   1970-01-01T08:00:00+08:00
# @Email:  guanwanxian@zju.edu.cn
# @Last modified by:   guanwanxian
# @Last modified time: 2017-03-26T19:39:24+08:00

from .Transformations import superimposition_matrix
import numpy as np

class Point3D():
    """ 3D Object Class
    """
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return 'Point3D: position {}'.format((self.x, self.y, self.z))

    def toList(self):
        return [self.x, self.y, self.z]

    def medianWithPoint(self, p):
        '''medianWithPoint: Calculate median with other Point3D
        Args:
            p (Point3D): The other point.

        Returns:
            (Point3D): The median point.
        '''
        x_m = self.x + (p.x-self.x)/2;
        y_m = self.y + (p.y-self.y)/2;
        z_m = self.z + (p.z-self.z)/2;

        return Point3D(x_m, y_m, z_m)

    def distanceWithPoint(self, p):
        '''distanceWithPoint: Calculate distance with Point3D
        Args:
            p (Point3D): The other point.

        Returns:
            (float): The distance between two points.
        '''

        return np.sqrt((p.x-self.x)**2 + (p.y-self.y)**2 + (p.z-self.z)**2)

    def scale(self, lower_bound=(0,0,0), scale_ratio=1, base=0):
        '''scale: Scale the sphere with respect to lower_bound with scale_ratio.
        Args:
            lower_bound ((float, float, float)): The lower_bound.
            scale_ratio (float): The scale ratio.
            base (float): New base
            ----------------------------------------
            new_x = (x-lower_bound[0])*scale_ratio + base
            new_y = (y-lower_bound[1])*scale_ratio + base
            new_z = (z-lower_bound[2])*scale_ratio + base
        '''
        self.x = (self.x-lower_bound[0])*scale_ratio + base
        self.y = (self.y-lower_bound[1])*scale_ratio + base
        self.z = (self.z-lower_bound[2])*scale_ratio + base

class Obj3D():
    """ Base 3D Object Class
    """
    def __init__(self, p):
        '''Initialization function.
        Args:
            p (Point3D): Center of object.
        '''
        self.center =  p

    def __str__(self):
        return 'Obj3D: position {}'.format(self.center)

    def scale(self, lower_bound=(0,0,0), scale_ratio=1, base=0):
        '''scale: Scale the sphere with respect to lower_bound with scale_ratio.
        Args:
            lower_bound ((float, float, float)): The lower_bound.
            scale_ratio (float): The scale ratio.
            base (float): New base
        '''
        self.center.scale(lower_bound, scale_ratio, base)

class Sphere(Obj3D):
    """ Sphere inherit from Obj3D
    """
    def __init__(self, center_point, radius):
        '''__init__:
        Args:
            center_point (Obj3D): Center point.
            radius (float): Radius of sphere.
        '''
        self.center_point = center_point
        self.radius = radius
        super().__init__(center_point)

    def __str__(self):
        return 'Sphere:\n' \
               +'\tcenter_point: '+self.center_point.__str__()+'\n' \
               +'\tradius:{}'.format(self.radius)

    def calBBox(self):
            min_mat = np.array(self.center_point.toList()) # 1*3
            max_mat = min_mat.copy()
            r_mat = np.array([self.radius]) # 1*1
            r_mat = np.tile(r_mat, (1,3))

            min_mat = min_mat-r_mat
            max_mat = max_mat+r_mat+1

            min_bound = np.floor(np.min(min_mat, 0)).astype(np.int)
            max_bound = np.ceil(np.max(max_mat, 0)).astype(np.int)
            return tuple(np.hstack((min_bound, max_bound)))

    def scale(self, lower_bound=(0,0,0), scale_ratio=1, base=0):
        '''scale: Scale the sphere with respect to lower_bound with scale_ratio.
        Args:
            lower_bound ((float, float, float)): The lower_bound.
            scale_ratio (float): The scale ratio.
            base (float): New base
            ----------------------------------------
        '''
        self.center_point.scale(lower_bound, scale_ratio, base)
        self.radius = self.radius*scale_ratio


class Cone(Obj3D):
    """ Cone inherit from Obj3D
    """
    def __init__(self, bottom_point, bottom_radius, up_point, up_radius):
        '''__init__:
        Args:
            bottom_point (Obj3D): Bottom point.
            bottom_radius (float): Bottom radius.
            up_point (Obj3D): Up point.
            up_radius (float): Up radius.
        '''
        if bottom_radius<up_radius:
            self.bottom_point =  up_point
            self.bottom_radius = up_radius
            self.up_point = bottom_point
            self.up_radius = bottom_radius
        else:
            self.bottom_point = bottom_point
            self.bottom_radius = bottom_radius
            self.up_point = up_point
            self.up_radius = up_radius

        self.height=bottom_point.distanceWithPoint(up_point)
        super().__init__(bottom_point.medianWithPoint(up_point))

    def __str__(self):
            return 'Cone:\n' \
                   +'\tbottom_point: '+self.bottom_point.__str__()+'\n' \
                   +'\tbottom_radius: {}'.format(self.bottom_radius)+'\n' \
                   +'\tup_point: '+self.up_point.__str__()+'\n' \
                   +'\tup_radius: {}'.format(self.up_radius)+'\n' \
                   +'\theight: {}'.format(self.height)

    def calBBox(self):
            min_mat = np.array([self.up_point.toList(), self.bottom_point.toList()])
            max_mat = min_mat.copy()
            r_mat = np.array([[self.up_radius], [self.bottom_radius]])
            r_mat = np.tile(r_mat, (1,3))

            min_mat = min_mat-r_mat
            max_mat = max_mat+r_mat+1

            min_bound = np.floor(np.min(min_mat, 0)).astype(np.int)
            max_bound = np.ceil(np.max(max_mat, 0)).astype(np.int)
            return tuple(np.hstack((min_bound, max_bound)))

    def revertMat(self):
        '''revertMat: Calculate revert matrix.
        Returns:
            bool: The return value.
        '''
        p1 = self.bottom_point
        p2 = self.up_point
        p3=p1.medianWithPoint(p2)
        v0=np.array([[p1.x, p2.x, p3.x],
                     [p1.y, p2.y, p3.y],
                     [p1.z, p2.z, p3.z],
                     [   1,    1,    1]])
        Dis=p1.distanceWithPoint(p2)
        v1=np.array([[0,     0,   0],
                     [0,     0,   0],
                     [0, Dis, Dis/2],
                     [1,     1,  1]])
        rev_mat = superimposition_matrix(v0,v1)
        return rev_mat

    def scale(self, lower_bound=(0,0,0), scale_ratio=1, base=0):
        '''scale: Scale the sphere with respect to lower_bound with scale_ratio.
        Args:
            lower_bound ((float, float, float)): The lower_bound.
            scale_ratio (float): The scale ratio.
            base (float): New base
            ----------------------------------------
        '''
        self.bottom_point.scale(lower_bound, scale_ratio, base)
        self.bottom_radius = self.bottom_radius*scale_ratio
        self.up_point.scale(lower_bound, scale_ratio, base)
        self.up_radius = self.up_radius*scale_ratio
        self.height = self.bottom_point.distanceWithPoint(self.up_point)

def calculateBound(sphere_list):
    '''calculateBound: Calculate the bound of spheres.
    Args:
        sphere_list (list of Sphere).
    Returns:
        min_bound ([float, float, float]): minimum of x,y,z.
        max_bound ([float, float, float]): maximum of x,y,z.
    '''
    min_mat = np.array([p.center_point.toList() for p in sphere_list])
    max_mat = min_mat.copy()
    r_mat = np.array([p.radius for p in sphere_list])
    r_mat = np.transpose(np.tile(r_mat, (3,1)))

    min_mat = min_mat-r_mat
    max_mat = max_mat+r_mat

    min_bound = np.min(min_mat, 0)
    max_bound = np.max(max_mat, 0)

    return min_bound, max_bound

def calScaleRatio(min_bound, max_bound, img_lengths):
    '''calScaleRatio: Calculate the scale ratio with respect to length.
    Args:
        min_bound ([float, float, float]): minimum of x,y,z.
        max_bound ([float, float, float]): maximum of x,y,z.
        img_lengths ((float, float, float)): The desired length.
    Returns:
        (float): The calculated ratio.
    '''
    spans = max_bound-min_bound
    scale_ratios = np.array(img_lengths)/np.array(spans)
    return np.min(scale_ratios)
