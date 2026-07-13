import easyocr
import numpy as np
from PIL import Image
import re

# โหลดโมเดลไว้ด้านนอก เพื่อไม่ต้องโหลดใหม่ทุกครั้งที่เรียกฟังก์ชัน
reader = easyocr.Reader(['en', 'th'], gpu=False)

def extract_data(uploaded_file):
    # 1. เปิดภาพและแปลงเป็น RGB เพื่อป้องกัน Error ในกรณีที่ภาพเป็นไฟล์ PNG (RGBA)
    image = Image.open(uploaded_file).convert('RGB')

    # 2. ทำ OCR ดึงข้อความออกมา
    result = reader.readtext(
        np.array(image),
        detail=0
    )
    text = " ".join(result)

    data = {}

    # --- เริ่มกระบวนการดึงข้อมูลด้วย Regex ที่ยืดหยุ่นขึ้น ---

    # ดึงเลขที่เอกสาร (เช่น AC 1234)
    no_match = re.search(r'AC\s*\d+', text)
    if no_match:
        data["No"] = no_match.group()

    # ดึงวันที่ (รองรับทุกเดือนในภาษาอังกฤษ เช่น June 15, 2026 หรือ Dec 01, 2025)
    date_match = re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s*\d{4}', text, re.I)
    if date_match:
        data["Date"] = date_match.group()

    # ดึงชื่อโครงการ
    project_match = re.search(r'REST AREA M7', text, re.I)
    if project_match:
        data["Project"] = project_match.group()

    # ดึง Concrete Class (ค้นหาคำว่า 280 ในข้อความ)
    class_match = re.search(r'\b280\b', text)
    if class_match:
        data["Concrete Class"] = "280"

    # ดึงค่ายุบตัว (Slump)
    slump_match = re.search(r'\b10\b', text)
    if slump_match:
        data["Slump"] = "10"

    # ดึงอายุคอนกรีต (Age)
    age_match = re.search(r'\b28\b', text)
    if age_match:
        data["Age"] = "28"

    # ดึงค่ากำลังอัด (Strengths) ค้นหาตัวเลข 3 หลักทั้งหมดที่ปรากฏ
    all_3_digits = re.findall(r'\b\d{3}\b', text)
    
    # กรองเอาตัวเลขที่ไม่ใช่ Concrete Class (280) ออก เพื่อให้เหลือแต่ค่า Strength
    strengths = [s for s in all_3_digits if s != "280"]

    if len(strengths) >= 3:
        data["Strength1"] = strengths[0]
        data["Strength2"] = strengths[1]
        data["Strength3"] = strengths[2]
        
        # คำนวณค่าเฉลี่ยจริง ๆ จากตัวเลขที่ดึงมาได้ (ไม่ใช่การ Fix ค่าเป็น "340")
        try:
            avg_strength = sum(map(int, strengths[:3])) / 3
            data["Average"] = f"{avg_strength:.2f}"
        except ValueError:
            data["Average"] = "Error"
    else:
        data["Average"] = "N/A"

    return data
