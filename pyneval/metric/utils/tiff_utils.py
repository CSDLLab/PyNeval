

def front_expend_step(tiff_file, threshold=1):
    str = (
        (0, 0, 1),
        (0, 0, -1),
        (0, 1, 0),
        (0, -1, 0),
        (1, 0, 0),
        (-1, 0, 0),
    )
    for i in range(tiff_file.shape[0]):
        for j in range(tiff_file.shape[1]):
            for k in range(tiff_file.shape[2]):
                print(i*512**2 + j*512 + k)
                if tiff_file[i][j][k] < threshold:
                    continue
                for d in range(6):
                    dx, dy, dz = i + str[d][0], j + str[d][1], k + str[d][2]
                    if 0<=dx<tiff_file.shape[0] and \
                        0<=dy<tiff_file.shape[1] and \
                        0<=dz<tiff_file.shape[2]:
                        tiff_file[dx][dy][dz] = max(tiff_file[i][j][k], threshold)


