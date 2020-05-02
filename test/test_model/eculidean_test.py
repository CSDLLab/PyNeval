import unittest
import random
import math
from pyneval.model.euclidean_point import EuclideanPoint,Line


def rand(k):
    return random.uniform(0, k)


class TestPointMethods(unittest.TestCase):

    def test_point_to_line(self):
        p = EuclideanPoint([49.4362, 111.12, 322.687])
        l = Line(coords=[[47.9082, 110.024, 323.994],[56.0636, 112.369, 318.703]])
        l2 = Line(coords=[[49.4362, 111.12, 322.687],[56.0636, 112.369, 318.703]])
        print(p.distance(l))
        print(p.distance(l2))

    def test_foot_point1(self):
        for i in range(5000):
            p = EuclideanPoint([1,2,3])
            l = Line(coords=[[2,3,4],[5,6,7]])
            p.get_foot_point(l)

    def test_foot_point2(self):
        for i in range(5000):
            p = EuclideanPoint([1,2,3])
            l = Line(coords=[[2,3,4],[5,6,7]])
            p.get_foot_point(l)

    def test_foot_point_right(self):
        for i in range(5000):
            p = EuclideanPoint([rand(10),rand(10),rand(10)])
            line = Line(coords=[[rand(10),rand(10),rand(10)],[rand(10),rand(10),rand(10)]])
            ans1 = p.get_foot_point(line)
            ans2 = p.get_foot_point(line)
            for i in range(0,3):
                self.assertTrue(math.fabs(ans1._pos[i] - ans2._pos[i]) < 0.0000001)


if __name__ == "__main__":
    unittest.main()
