from pyneval.metric.utils.config_utils import EPS

class KM:
    def __init__(self, maxn, nx, ny, G):
        self.maxn = 330
        self.ny = ny
        self.nx = nx
        self.G = G

        self.KM_INF = 0x3f3f3f3f
        self.match = [-1]*maxn
        self.slack = [0]*maxn
        self.visx = [False]*maxn
        self.visy = [False]*maxn
        self.lx = [0]*maxn
        self.ly = [0]*maxn
        self.fa = [0]*(maxn*2)

    def find_path(self, x):
        self.visx[x] = True
        for y in range(self.ny):
            if self.visy[y]:
                continue
            tmp_delta = self.lx[x] + self.ly[y] - self.G[x][y]
            if tmp_delta < EPS:
                self.visy[y] = True
                if self.match[y] == -1 or self.find_path(self.match[y]):
                    self.match[y] = x
                    return True
            elif self.slack[y] > tmp_delta:
                self.slack[y] = tmp_delta
        return False

    def km(self):
        for x in range(self.nx):
            for j in range(self.ny):
                self.slack[j] = self.KM_INF
            while True:
                self.visx = [False] * self.maxn
                self.visy = [False] * self.maxn
                if self.find_path(x):
                    break
                delta = self.KM_INF
                for j in range(self.ny):
                    if not self.visy[j] and delta > self.slack[j]:
                        delta = self.slack[j]
                for i in range(self.nx):
                    if self.visx[x]:
                        self.lx[i] -= delta
                for j in range(self.ny):
                    if self.visy[j]:
                        self.ly[j] += delta
                    else:
                        self.slack[j] -= delta

    def solve(self):
        self.match = [-1]*self.maxn
        self.ly = [0]*self.maxn

        for i in range(self.nx):
            self.lx[i] = -self.KM_INF
            for j in range(self.ny):
                if self.lx[i] < self.G[i][j]:
                    self.lx[i] = self.G[i][j]
        self.km()

    def get_max_dis(self):
        ans = 0
        for i in range(0, self.ny):
            if self.match[i] != -1 and self.G[self.match[i]][i] != -self.KM_INF/2:
                ans += self.G[self.match[i]][i]
        return ans


if __name__ == "__main__":
    pass
