import cv2
from openni import openni2
import numpy as np

# 初始化OpenNI
openni2.initialize()
dev = openni2.Device.open_any()

# 创建颜色流
color_stream = dev.create_color_stream()
color_stream.start()

# 创建一个目录用于保存图像
import os
output_dir = 'calibration_images'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 捕获图像
try:
    for i in range(16):  # 捕捉10张图片
        # 从流中读取图像
        frame = color_stream.read_frame()
        frame_data = frame.get_buffer_as_triplet()
        img = np.frombuffer(frame_data, dtype=np.uint8).reshape((480, 640, 3))  # 假设分辨率为640x480
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # 显示图像
        cv2.imshow('RGB Image', img)
        
        # 保存图像
        img_filename = os.path.join(output_dir, f'calibration_{i}.jpg')
        cv2.imwrite(img_filename, img)
        print(f'Saved {img_filename}')
        
        # 等待按键或等待一段时间
        key = cv2.waitKey(5000)
        if key == ord('q'):
            break

finally:
    # 释放资源
    color_stream.stop()
    openni2.unload()
    cv2.destroyAllWindows()
