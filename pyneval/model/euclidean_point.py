import numpy as np
import math
from pyneval.metric.utils.config_utils import EPS

class EuclideanPoint(object):
    '''
    geometry node without volume
    for point-line calculate
    '''
    def __init__(self,
                 center=[0, 0, 0]):
        if not isinstance(center, list):
            raise Exception("[Error: ]not a list")
        self._pos = center

    def get_x(self):
        return self._pos[0]

    def get_y(self):
        return self._pos[1]

    def get_z(self):
        return self._pos[2]

    def set_x(self, x):
        self._pos[0] = x

    def set_y(self, y):
        self._pos[1] = y

    def set_z(self, z):
        self._pos[2] = z

    def to_str(self):
        print("{} {} {}".format(self._pos[0], self._pos[1], self._pos[2]))

    def add_coord(self, point_a):
        '''
        :param point_a: another EuclideanPoint
        :return: True if success
        '''
        if not isinstance(point_a, EuclideanPoint):
            return False

        self._pos[0] += point_a.get_x()
        self._pos[1] += point_a.get_y()
        self._pos[2] += point_a.get_z()

        return True

    def get_foot_point(self, line):
        p = self._pos
        a = line.coords[0]
        b = line.coords[1]
        a_p = [a[0]-p[0], a[1]-p[1], a[2]-p[2]]
        b_a = [b[0]-a[0], b[1]-a[1], b[2]-a[2]]

        k_up = -(a_p[0]*b_a[0]+a_p[1]*b_a[1]+a_p[2]*b_a[2])
        k_down = b_a[0]**2+b_a[1]**2+b_a[2]**2
        if k_down < EPS:
            raise Exception("[Error: ] Line {} {} is just a point".format(a, b))
        k = k_up/k_down
        foot = [k*b_a[0]+a[0], k*b_a[1]+a[1], k*b_a[2]+a[2]]
        return EuclideanPoint(foot)

    def get_closest_point(self, line):
        foot = self.get_foot_point(line)
        if foot.on_line(line):
            return foot
        else:
            dis1 = self.distance(EuclideanPoint(center=line.coords[0]))
            dis2 = self.distance(EuclideanPoint(center=line.coords[1]))
            if dis1 <dis2:
                return EuclideanPoint(center=line.coords[0])
            else:
                return EuclideanPoint(center=line.coords[1])

    def on_line(self, line):
        p = self._pos
        a = line.coords[0]
        b = line.coords[1]

        if min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and \
                min(a[1], b[1]) <= p[1] <= max(a[1], b[1]) and \
                min(a[2], b[2]) <= p[2] <= max(a[2], b[2]):
            return True
        return False

    def distance_to_point(self, point):
        if isinstance(point, list) and len(point) == 3:
            point = EuclideanPoint(point)
        if not isinstance(point, EuclideanPoint):
            raise Exception("[Error:  ] expect point. got {}".format(point))

        sub = [self._pos[0] - point._pos[0],
               self._pos[1] - point._pos[1],
               self._pos[2] - point._pos[2]]
        return math.sqrt(sub[0]*sub[0] + sub[1]*sub[1] + sub[2]*sub[2])

    def distance_to_point_2d(self, point):
        if isinstance(point, list) and len(point) == 3:
            point = EuclideanPoint(point)
        if not isinstance(point, EuclideanPoint):
            raise Exception("[Error:  ] expect point. got {}".format(point))

        sub = [self._pos[0] - point._pos[0],
               self._pos[1] - point._pos[1],
               self._pos[2] - point._pos[2]]
        return math.sqrt(sub[0]*sub[0] + sub[1]*sub[1])

    def distance_to_line(self, line):
        foot = self.get_foot_point(line)
        return self.distance_to_point(foot)

    def distance_to_segment(self, line):
        foot = self.get_foot_point(line)
        # foot = EuclideanPoint([0, 0, 0])
        if foot.on_line(line):
            return self.distance_to_point(foot)
        else:
            dis1 = self.distance_to_point(line.coords[0])
            dis2 = self.distance_to_point(line.coords[1])
            return min(dis1, dis2)

    def distance(self, obj):
        if isinstance(obj, EuclideanPoint):
            return self.distance_to_point(obj)
        elif isinstance(obj, Line):
            if obj.is_segment:
                return self.distance_to_segment(obj)
            else:
                return self.distance_to_line(obj)
        else:
            raise Exception("[Error: ] unexpected object type {}".format(type(obj)))


class Line:
    '''
    consist of two EuclideanPoint
    coords[0] and coords[1]
    '''
    def __init__(self,
                 coords=None,
                 e_node_1=None,
                 e_node_2=None,
                 is_segment=True):
        if coords is not None:
            self.coords = coords
        else:
            self.coords = [[],[]]
            self.coords[0] = e_node_1._pos
            self.coords[1] = e_node_2._pos
        self.is_segment = is_segment

    def to_str(self):
        print("[{} {} {}, {} {} {}]".format(
            self.coords[0].get_x(), self.coords[0].get_y(), self.coords[0].get_z(),
            self.coords[1].get_x(), self.coords[1].get_y(), self.coords[1].get_z()))

    def get_points(self):
        point_a = EuclideanPoint(self.coords[0])
        point_b = EuclideanPoint(self.coords[1])
        return point_a, point_b

    def distance(self, obj):
        if isinstance(obj, EuclideanPoint):
            return obj.distance(self)
        else:
            raise Exception("[Error: ] unexpected object type" + type(obj))


if __name__ == "__main__":
    pass
