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

# --- CORE ENGINEERING FUNCTIONS ---
def calculate_piles(p_load, mx_load, my_load, swl, piles_df):
    # 1. คำนวณค่าเยื้องศูนย์ของกลุ่ม (Global Eccentricity)
    x_bar = piles_df['x_actual'].mean()
    y_bar = piles_df['y_actual'].mean()
    
    # 2. คำนวณ Moment สุทธิ (Applied + P*e)
    # หมายเหตุ: ทิศทางของ Moment ขึ้นอยู่กับจตุภาคพิกัด
    mx_total = mx_load + (p_load * y_bar)
    my_total = my_load + (p_load * x_bar)
    
    # 3. คำนวณระยะจากจุด CG ใหม่ (Local Coordinates)
    piles_df['dx'] = piles_df['x_actual'] - x_bar
    piles_df['dy'] = piles_df['y_actual'] - y_bar
    
    # 4. Pile Group Properties
    sum_x2 = (piles_df['dx']**2).sum()
    sum_y2 = (piles_df['dy']**2).sum()
    n = len(piles_df)
    
    # 5. Individual Pile Reactions (Formula: R = P/n + My*x/Ix + Mx*y/Iy)
    # ระวังการสลับแกน: Mx หมุนรอบแกน X ทำให้เกิดแรงตามระยะ Y
    piles_df['reaction'] = (p_load / n) + (mx_total * piles_df['dy'] / sum_y2) + (my_total * piles_df['dx'] / sum_x2)
    
    # 6. Structural Integrity Checks
    piles_df['deviation_mm'] = np.sqrt((piles_df['x_actual'] - piles_df['x_design'])**2 + 
                                       (piles_df['y_actual'] - piles_df['y_design'])**2) * 1000
    piles_df['pile_moment_tm'] = piles_df['reaction'] * (piles_df['deviation_mm'] / 1000)
    piles_df['status'] = np.where(piles_df['reaction'] > swl, "OVERLOAD", 
                         np.where(piles_df['reaction'] < 0, "UPLIFT", "OK"))
    
    return piles_df, x_bar, y_bar, mx_total, my_total

# --- UI SECTION ---
st.title("🏗️ Pile Eccentricity Analysis Tool (SDM Approach)")
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
    num_piles = st.number_input("จำนวนเสาเข็มในกลุ่ม", min_value=1, max_value=24, value=4)
    
    # Default coordinates for a standard 4-pile group (1.2m spacing)
    default_data = {
        "Pile_ID": [f"P{i+1}" for i in range(num_piles)],
        "x_design": [-0.6, 0.6, -0.6, 0.6][:num_piles] + [0.0]*(max(0, num_piles-4)),
        "y_design": [0.6, 0.6, -0.6, -0.6][:num_piles] + [0.0]*(max(0, num_piles-4)),
        "x_actual": [-0.65, 0.62, -0.58, 0.67][:num_piles] + [0.0]*(max(0, num_piles-4)),
        "y_actual": [0.63, 0.58, -0.65, -0.62][:num_piles] + [0.0]*(max(0, num_piles-4)),
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
    
    # Actual Positions (Color by Reaction)
    fig.add_trace(go.Scatter(x=res_df['x_actual'], y=res_df['y_actual'], mode='markers+text',
                             text=res_df['Pile_ID'], textposition="top center",
                             marker=dict(size=res_df['reaction']*0.8, 
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
