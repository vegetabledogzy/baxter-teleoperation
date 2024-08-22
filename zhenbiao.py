import cv2
import numpy as np
import glob

# 设置棋盘格的内角点数 (nx, ny)
chessboard_size = (7, 7)
# 设置每个方块的实际大小 (以米为单位，例如0.02表示方块边长为2厘米)
square_size = 23.1

# 准备棋盘格角点的世界坐标
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size


# 用于保存所有图像的角点和对应的世界坐标
objpoints = []  # 世界坐标系中的三维点
imgpoints = []  # 图像平面的二维点

# 读取标定图像
images = glob.glob('H:/deep/envs/torchpy/calibration_images/*.jpg')  # 替换为你的标定图像路径

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 查找棋盘格角点
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
    
    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)
        
        # 绘制角点并显示
        img = cv2.drawChessboardCorners(img, chessboard_size, corners, ret)
        cv2.imshow('Chessboard corners', img)
        cv2.waitKey(1000)

cv2.destroyAllWindows()

# 标定相机
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# 打印结果
print("Camera matrix:\n", camera_matrix)
print("Distortion coefficients:\n", dist_coeffs)

# 选择一张图像进行畸变校正
img = cv2.imread(images[6])
h, w = img.shape[:2]
new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))

# 畸变校正
dst = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_camera_matrix)

# 裁剪图像
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv2.imwrite('calibrated_image.jpg', dst)

cv2.imshow('Calibrated image', dst)
cv2.waitKey(100000)
cv2.destroyAllWindows()
