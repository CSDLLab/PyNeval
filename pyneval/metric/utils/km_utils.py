
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
        tmp_delta = 0
        self.visx[x] = True
        for y in range(1, self.ny+1):
            if self.visy[y]:
                continue
            tmp_delta = self.lx[x]+self.ly[y]-self.G[x][y]
            if tmp_delta == 0:
                self.visy[y] = True
                self.fa[y+self.nx] = x
                if self.match[y] == -1:
                    return y+self.nx
                self.fa[self.match[y]] = y+self.nx
                res = self.find_path(self.match[y])
                if res > 0:
                    return res
            elif self.slack[x] > tmp_delta:
                self.slack[x] = tmp_delta
        return -1

    def km(self):
        for x in range(1, self.nx+1):
            for i in range(1, self.nx+1):
                self.slack[i] = self.KM_INF
            for i in range(1, self.nx+self.ny+1):
                self.fa[i] = -1
            self.visx = [False]*self.maxn
            self.visy = [False]*self.maxn

            fir, leaf = 1, -1
            while True:
                if fir == 1:
                    leaf = self.find_path(x)
                    fir = 0
                else:
                    for i in range(1, self.nx+1):
                        if self.slack[i] == 0:
                            self.slack[i] = self.KM_INF
                            leaf = self.find_path(i)
                            if leaf > 0:
                                break
                if leaf > 0:
                    p = leaf
                    while p > 0:
                        self.match[p-self.nx] = self.fa[p]
                        p = self.fa[self.fa[p]]
                    break
                else:
                    delta = self.KM_INF
                    for i in range(1, self.nx+1):
                        if self.visx[i] and delta > self.slack[i]:
                            delta = self.slack[i]
                    for i in range(1, self.nx+1):
                        if self.visx[i]:
                            self.lx[i] -= delta
                            self.slack[i] -= delta
                    for j in range(1, self.ny+1):
                        if self.visy[j]:
                            self.ly[j] += delta

    def solve(self):
        self.match = [-1]*self.maxn
        self.ly = [0]*self.maxn

        for i in range(1, self.nx+1):
            self.lx[i] = -self.KM_INF
            for j in range(1, self.ny+1):
                if self.lx[i] < self.G[i][j]:
                    self.lx[i] = self.G[i][j]
        self.km()

    def get_max_dis(self):
        ans = 0
        for i in range(1, self.ny + 1):
            if self.match[i] != -1 and self.G[self.match[i]][i] != -self.KM_INF:
                ans += self.G[self.match[i]][i]
        return ans


if __name__ == "__main__":
    nx = 2
    ny = 2
    G = [
        [0, 0, 0],
        [0, 1, 100],
        [0, -0x3f3f3f3f, 1],
    ]
    km = KM(maxn=300, nx=nx, ny=ny, G=G)
    km.solve()

    print(km.G)
    for i in range(1, ny+1):
        print("{} {}".format(i, km.match[i]))
    print(km.get_max_dis())

