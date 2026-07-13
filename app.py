import os
import easyocr
import numpy as np
from PIL import Image
import re

# สร้างโฟลเดอร์ชื่อ 'models' ไว้ในโปรเจคของเราเองเพื่อตัดปัญหาเรื่องสิทธิ์ระบบ
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'models')

# เพิ่มพารามิเตอร์ model_storage_directory เข้าไป
reader = easyocr.Reader(
    ['en', 'th'],
    gpu=False,
    model_storage_directory=model_path
)

# ... โค้ดส่วนดึงข้อมูล extract_data(uploaded_file) ด้านล่างคงเดิมไว้ ...
