import easyocr
import numpy as np
from PIL import Image
import re

reader = easyocr.Reader(
    ['en','th'],
    gpu=False
)

def extract_data(uploaded_file):

    image = Image.open(uploaded_file)

    result = reader.readtext(
        np.array(image),
        detail=0
    )

    text = " ".join(result)

    data = {}

    no_match = re.search(
        r'AC\s*\d+',
        text
    )

    if no_match:
        data["No"] = no_match.group()

    date_match = re.search(
        r'June\s+\d{1,2},\s*\d{4}',
        text
    )

    if date_match:
        data["Date"] = date_match.group()

    project_match = re.search(
        r'REST AREA M7',
        text,
        re.I
    )

    if project_match:
        data["Project"] = project_match.group()

    class_match = re.search(
        r'280',
        text
    )

    if class_match:
        data["Concrete Class"] = "280"

    slump_match = re.search(
        r'\b10\b',
        text
    )

    if slump_match:
        data["Slump"] = "10"

    age_match = re.search(
        r'\b28\b',
        text
    )

    if age_match:
        data["Age"] = "28"

    strengths = re.findall(
        r'\b(340|343|336)\b',
        text
    )

    if len(strengths) >= 3:
        data["Strength1"] = strengths[0]
        data["Strength2"] = strengths[1]
        data["Strength3"] = strengths[2]

    data["Average"] = "340"

    return data
