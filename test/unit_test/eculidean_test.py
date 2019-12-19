import unittest
import random
import math
from pymets.model.euclidean_point import EuclideanPoint,Line

def rand(k):
    return random.uniform(0, k)
class TestPointMethods(unittest.TestCase):

    def test_point_to_line(self):
        p = EuclideanPoint([1,2,3])
        l = Line(coords=[[2,3,4],[5,6,7]])
        print(p.distance(l))

    def test_foot_point1(self):
        for i in range(5000):
            p = EuclideanPoint([1,2,3])
            l = Line(coords=[[2,3,4],[5,6,7]])
            p.get_foot_point(l)

    def test_foot_point2(self):
        for i in range(5000):
            p = EuclideanPoint([1,2,3])
            l = Line(coords=[[2,3,4],[5,6,7]])
            p.get_foot_point_fast(l)

    def test_foot_point_right(self):
        for i in range(5000):
            p = EuclideanPoint([rand(10),rand(10),rand(10)])
            line = Line(coords=[[rand(10),rand(10),rand(10)],[rand(10),rand(10),rand(10)]])
            ans1 = p.get_foot_point_fast(line)
            ans2 = p.get_foot_point(line)
            for i in range(0,3):
                self.assertTrue(math.fabs(ans1._pos[i] - ans2._pos[i]) < 0.0000001)



if __name__ == "__main__":
    unittest.main()
