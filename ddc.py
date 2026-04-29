import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="Pile Eccentricity Pro", layout="wide")

# --- CSS FOR STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- COORDINATE GENERATOR (เพิ่มจากเวอร์ชัน Pro เพื่อไม่ให้พังเวลาเพิ่มจำนวนเข็ม) ---
def make_default_coords(n: int):
    if n == 1:
        return [0.0], [0.0], [0.0], [0.0]
    elif n == 2:
        return [-0.6, 0.6], [0.0, 0.0], [-0.65, 0.62], [0.03, -0.02]
    elif n == 3:
        return [-0.6, 0.6, 0.0], [-0.4, -0.4, 0.6], [-0.62, 0.58, 0.05], [-0.45, -0.38, 0.63]
    elif n == 4:
        return [-0.6, 0.6, -0.6, 0.6], [0.6, 0.6, -0.6, -0.6], [-0.65, 0.62, -0.58, 0.67], [0.63, 0.58, -0.65, -0.62]
    else:
        cols = int(np.ceil(np.sqrt(n)))
        sp = 1.2
        design_x, design_y = [], []
        for i in range(n):
            r, c = divmod(i, cols)
            design_x.append((c - (cols - 1) / 2) * sp)
            design_y.append((r - (int(np.ceil(n / cols)) - 1) / 2) * sp)
        rng = np.random.default_rng(42)
        actual_x = [x + rng.uniform(-0.05, 0.05) for x in design_x]
        actual_y = [y + rng.uniform(-0.05, 0.05) for y in design_y]
        return design_x, design_y, actual_x, actual_y

# --- CORE ENGINEERING FUNCTIONS ---
def calculate_piles(p_load, mx_load, my_load, swl, piles_df):
    df = piles_df.copy() # Fix: ทำงานบน Copy เพื่อป้องกัน Error
    
    # 1. คำนวณค่าเยื้องศูนย์ของกลุ่ม (Global Eccentricity)
    x_bar = df['x_actual'].mean()
    y_bar = df['y_actual'].mean()
    
    # 2. คำนวณ Moment สุทธิ (Applied + P*e)
    mx_total = mx_load + (p_load * y_bar)
    my_total = my_load + (p_load * x_bar)
    
    # 3. คำนวณระยะจากจุด CG ใหม่ (Local Coordinates)
    df['dx'] = df['x_actual'] - x_bar
    df['dy'] = df['y_actual'] - y_bar
    
    # 4. Pile Group Properties
    sum_x2 = (df['dx']**2).sum()
    sum_y2 = (df['dy']**2).sum()
    n = len(df)
    
    # Fix: ป้องกันการหารด้วยศูนย์ (Divide by Zero)
    safe_sum_x2 = sum_x2 if sum_x2 > 1e-12 else 1e-12
    safe_sum_y2 = sum_y2 if sum_y2 > 1e-12 else 1e-12
    
    # 5. Individual Pile Reactions (Formula: R = P/n + My*x/Ix + Mx*y/Iy)
    df['reaction'] = (p_load / n) + (mx_total * df['dy'] / safe_sum_y2) + (my_total * df['dx'] / safe_sum_x2)
    
    # 6. Structural Integrity Checks
    df['deviation_mm'] = np.sqrt((df['x_actual'] - df['x_design'])**2 + 
                                       (df['y_actual'] - df['y_design'])**2) * 1000
    df['pile_moment_tm'] = df['reaction'] * (df['deviation_mm'] / 1000)
    df['status'] = np.where(df['reaction'] > swl, "OVERLOAD", 
                         np.where(df['reaction'] < 0, "UPLIFT", "OK"))
    
    return df, x_bar, y_bar, mx_total, my_total

# --- UI SECTION ---
st.title("🏗️ Pile Eccentricity Analysis Tool")
st.markdown("โปรแกรมตรวจสอบแรงปฏิกิริยาเสาเข็มกรณีเยื้องศูนย์ สำหรับวิศวกรโครงสร้าง")

# Sidebar Inputs
with st.sidebar:
    st.header("1. Input Design Loads")
    p_input = st.number_input("Axial Load (P) [tons]", value=120.0, step=1.0)
    mx_input = st.number_input("Moment Mx [ton-m]", value=5.0, step=0.5)
    my_input = st.number_input("Moment My [ton-m]", value=2.0, step=0.5)
    
    st.divider()
    st.header("2. Pile Capacity & Tolerance")
    swl_input = st.number_input("Safe Working Load (SWL) [tons/pile]", value=40.0)
    tolerance = st.number_input("Tolerance Limit [mm]", value=75.0)

# Main Interaction Area
col_input, col_viz = st.columns([1, 1])

with col_input:
    st.subheader("📍 Pile Coordinates Configuration")
    # Fix: บังคับให้เป็น int
    num_piles = int(st.number_input("จำนวนเสาเข็มในกลุ่ม", min_value=1, max_value=24, value=4))
    
    # ใช้ระบบสร้างพิกัดอัตโนมัติ
    dx, dy, ax, ay = make_default_coords(num_piles)
    default_data = {
        "Pile_ID": [f"P{i+1}" for i in range(num_piles)],
        "x_design": [round(v, 3) for v in dx],
        "y_design": [round(v, 3) for v in dy],
        "x_actual": [round(v, 3) for v in ax],
        "y_actual": [round(v, 3) for v in ay],
    }
    
    df_input = pd.DataFrame(default_data)
    st.markdown("แก้ไขพิกัดตอกจริง (Actual) เทียบกับศูนย์กลางเสา (0,0)")
    edited_df = st.data_editor(df_input, use_container_width=True, num_rows="fixed")

# Calculation Execution
res_df, ex, ey, mxt, myt = calculate_piles(p_input, mx_input, my_input, swl_input, edited_df)

with col_viz:
    st.subheader("📊 Pile Group Visualization")
    
    fig = go.Figure()
    # Design Positions (Gray)
    fig.add_trace(go.Scatter(x=res_df['x_design'], y=res_df['y_design'], mode='markers',
                             marker=dict(size=12, color='lightgray', symbol='x'), name='Design'))
    
    # Fix: ขนาดจุดต้องไม่ติดลบ (ป้องกัน Plotly Error เวลามีแรง Uplift)
    marker_sizes = [max(abs(r) * 0.8, 8) for r in res_df['reaction']]
    
    # Actual Positions (Color by Reaction)
    fig.add_trace(go.Scatter(x=res_df['x_actual'], y=res_df['y_actual'], mode='markers+text',
                             text=res_df['Pile_ID'], textposition="top center",
                             marker=dict(size=marker_sizes, 
                                         color=res_df['reaction'], 
                                         colorscale='Viridis', 
                                         showscale=True,
                                         colorbar=dict(title="Reaction (t)")),
                             name='As-Built'))
    
    # Column Center (0,0)
    fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(size=15, color='red', symbol='cross'), name='Col Center'))
    
    fig.update_layout(template="plotly_white", height=500, xaxis_title="X-Axis (m)", yaxis_title="Y-Axis (m)",
                      yaxis=dict(scaleanchor="x", scaleratio=1))
    st.plotly_chart(fig, use_container_width=True)

# Results Display
st.divider()
st.subheader("✅ Analysis Summary")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Global Eccentricity X", f"{ex*1000:.1f} mm")
c2.metric("Global Eccentricity Y", f"{ey*1000:.1f} mm")
c3.metric("Total Moment Mx", f"{mxt:.2f} t-m")
c4.metric("Total Moment My", f"{myt:.2f} t-m")

# Detailed Table with Highlighting
st.subheader("Detailed Reaction Results")

def color_status(val):
    color = 'red' if val in ['OVERLOAD', 'UPLIFT'] else 'green'
    return f'color: {color}; font-weight: bold'

formatted_df = res_df[['Pile_ID', 'deviation_mm', 'reaction', 'pile_moment_tm', 'status']]
# Fix: เปลี่ยนจาก applymap เป็น map ตาม Pandas เวอร์ชันใหม่
st.dataframe(formatted_df.style.map(color_status, subset=['status']), use_container_width=True)

# Warnings
st.divider()
col_warn1, col_warn2 = st.columns(2)

with col_warn1:
    over_tol = res_df[res_df['deviation_mm'] > tolerance]
    if not over_tol.empty:
        st.error(f"⚠️ ตรวจพบเสาเข็มเยื้องศูนย์เกินมาตรฐาน ({tolerance} mm): {', '.join(over_tol['Pile_ID'].tolist())}")
    else:
        st.success("✅ ระยะเยื้องศูนย์อยู่ในเกณฑ์มาตรฐานทั้งหมด")

with col_warn2:
    if (res_df['status'] == 'OVERLOAD').any():
        st.warning("⚠️ มีเสาเข็มรับน้ำหนักเกินกำลัง (Overload) กรุณาพิจารณาขยายฐานรากหรือเพิ่มเข็มแซม")
    if (res_df['status'] == 'UPLIFT').any():
        st.warning("⚠️ ตรวจพบแรงดึง (Uplift) ในเสาเข็ม กรุณาตรวจสอบรอยต่อหัวเข็ม")
