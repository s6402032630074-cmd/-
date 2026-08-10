import re
import pdfplumber
import pandas as pd


def extract_pdf_data(pdf_path):
    extracted_rows = []

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)

        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""

            # กำหนดค่าเริ่มต้นเป็น "-" ทุกฟิลด์ตามเงื่อนไข
            row_data = {
                "NO.": "-",
                "Concrete Code": "-",
                "Location": "-",
                "วันที่ Casted on": "-",
                "วันที่ Tested on": "-",
                "อายุทดสอบ (Age - วัน)": "-",
                "กำลังอัดออกแบบ (Design Strength - ksc)": "-",
                "กำลังอัดที่ได้ Average": "-",
            }

            if text:
                # ตัวอย่างการสกัดข้อมูลด้วย Regular Expression (ปรับ Pattern ตามข้อความจริงในไฟล์ PDF)
                no_match = re.search(r"(?:NO\.|No\.|เลขที่)\s*[:.]?\s*([^\n]+)", text)
                code_match = re.search(
                    r"(?:Concrete Code|Code)\s*[:.]?\s*([^\n]+)", text
                )
                location_match = re.search(
                    r"(?:Location|สถานที่)\s*[:.]?\s*([^\n]+)", text
                )
                casted_match = re.search(
                    r"(?:Casted on|วันที่เท)\s*[:.]?\s*([\d\/\.\-]+)", text
                )
                tested_match = re.search(
                    r"(?:Tested on|วันที่ทดสอบ)\s*[:.]?\s*([\d\/\.\-]+)", text
                )
                age_match = re.search(r"(?:Age|อายุ)\s*[:.]?\s*(\d+)", text)
                design_match = re.search(
                    r"(?:Design Strength|กำลังอัดออกแบบ)\s*[:.]?\s*(\d+)", text
                )
                avg_match = re.search(
                    r"(?:Average|กำลังอัดเฉลี่ย)\s*[:.]?\s*([\d\.]+)", text
                )

                if no_match:
                    row_data["NO."] = no_match.group(1).strip()
                if code_match:
                    row_data["Concrete Code"] = code_match.group(1).strip()
                if location_match:
                    row_data["Location"] = location_match.group(1).strip()
                if casted_match:
                    row_data["วันที่ Casted on"] = casted_match.group(1).strip()
                if tested_match:
                    row_data["วันที่ Tested on"] = tested_match.group(1).strip()
                if age_match:
                    row_data["อายุทดสอบ (Age - วัน)"] = age_match.group(
                        1
                    ).strip()
                if design_match:
                    row_data[
                        "กำลังอัดออกแบบ (Design Strength - ksc)"
                    ] = design_match.group(1).strip()
                if avg_match:
                    row_data["กำลังอัดที่ได้ Average"] = avg_match.group(
                        1
                    ).strip()

            extracted_rows.append(row_data)

    # แปลงข้อมูลเป็น DataFrame
    df = pd.DataFrame(extracted_rows)

    # แสดงผลในรูปแบบ Markdown Table
    markdown_table = df.to_markdown(index=False)

    print(markdown_table)
    print("\n---")
    print(f"**สรุปผลการประมวลผล:**")
    print(f"- จำนวนหน้าทั้งหมดในไฟล์ PDF: {total_pages} หน้า")
    print(f"- จำนวนบรรทัดข้อมูลที่สกัดได้ในตาราง: {len(df)} บรรทัด")

    if total_pages == len(df):
        print(
            " STATUS: ยืนยันข้อมูลถูกต้อง (จำนวนบรรทัดในตารางตรงกับจำนวนหน้า PDF)"
        )
    else:
        print(" WARNING: จำนวนบรรทัดไม่ตรงกับจำนวนหน้า PDF")


# ใช้งานโปรแกรมโดยใส่ Path ของไฟล์ PDF
# extract_pdf_data("path_to_your_file.pdf")
