"""
Pile Eccentricity Analysis Tool — SDM Approach
แก้ไขจุดบกพร่อง + UI ใหม่ สำหรับวิศวกรโยธา
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pile Eccentricity Pro",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');

/* ── Variables ── */
:root {
    --bg:        #0a0e17;
    --bg-card:   #111827;
    --bg-card2:  #1a2235;
    --bg-input:  #151d2e;
    --accent:    #00d4ff;
    --accent2:   #0077ff;
    --gold:      #f5a623;
    --success:   #00e676;
    --danger:    #ff3d57;
    --warn:      #ffab00;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --border:    #1e293b;
    --glow:      0 0 20px rgba(0,212,255,0.15);
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Sarabun', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0e17 0%, #0d1520 100%) !important;
    border-right: 1px solid rgba(0,212,255,0.12) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }

/* ── Number inputs ── */
[data-testid="stNumberInput"] input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.9rem !important;
}
[data-testid="stNumberInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,212,255,0.18) !important;
}

/* ── Select box ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* ── Data editor ── */
[data-testid="stDataFrame"], .stDataFrame {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid rgba(0,212,255,0.12) !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Sarabun', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    border: none !important;
    transition: all 0.25s !important;
    letter-spacing: 0.05em !important;
}
.calc-btn > button {
    background: linear-gradient(135deg, #00d4ff 0%, #0077ff 100%) !important;
    color: #000 !important;
    padding: 0.6rem 2rem !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 20px rgba(0,212,255,0.35) !important;
}
.calc-btn > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0,212,255,0.50) !important;
}
.clear-btn > button {
    background: rgba(255,61,87,0.15) !important;
    color: #ff3d57 !important;
    border: 1px solid rgba(255,61,87,0.3) !important;
    padding: 0.6rem 1.5rem !important;
}
.clear-btn > button:hover {
    background: rgba(255,61,87,0.25) !important;
    transform: translateY(-1px) !important;
}

/* ── Custom cards ── */
.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    position: relative;
    overflow: hidden;
    margin-bottom: 0;
}
.stat-card::after {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.stat-card.gold::after  { background: linear-gradient(90deg, #f5a623, #ff6b35); }
.stat-card.green::after { background: linear-gradient(90deg, #00e676, #00b248); }
.stat-card.red::after   { background: linear-gradient(90deg, #ff3d57, #c62828); }

.stat-label { font-size: 0.68rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.3rem; }
.stat-value { font-size: 1.5rem; font-family: 'Share Tech Mono', monospace; font-weight: 600; line-height: 1.2; }
.stat-unit  { font-size: 0.72rem; color: var(--muted); margin-top: 0.15rem; }
.stat-badge { display:inline-block; font-size:0.65rem; font-weight:700;
              padding:2px 9px; border-radius:20px; margin-top:6px;
              letter-spacing:0.06em; text-transform:uppercase; }
.badge-ok   { background:rgba(0,230,118,0.12); color:#00e676; border:1px solid rgba(0,230,118,0.25); }
.badge-ng   { background:rgba(255,61,87,0.12);  color:#ff3d57;  border:1px solid rgba(255,61,87,0.25); }
.badge-warn { background:rgba(255,171,0,0.12);  color:#ffab00;  border:1px solid rgba(255,171,0,0.25); }

/* ── Section headers ── */
.sec-head {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.6rem 0; border-bottom: 1px solid var(--border);
    margin: 1.4rem 0 1rem;
}
.sec-head span { font-size: 1rem; }
.sec-head h3 {
    margin: 0; font-size: 0.85rem; font-weight: 700;
    color: var(--accent); letter-spacing: 0.1em; text-transform: uppercase;
}

/* ── Hero banner ── */
.hero-wrap {
    background: linear-gradient(135deg, #111827 0%, #1a2235 60%, #0d1520 100%);
    border: 1px solid rgba(0,212,255,0.15);
    border-top: 3px solid var(--accent);
    border-radius: 14px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-wrap::before {
    content: '⬡';
    position: absolute; right: 2rem; top: 50%;
    transform: translateY(-50%);
    font-size: 6rem; color: rgba(0,212,255,0.04);
    pointer-events: none;
}
.hero-wrap h1 { margin: 0 0 0.25rem; font-size: 1.5rem; font-weight: 700; color: var(--text); }
.hero-wrap p  { margin: 0; font-size: 0.82rem; color: var(--muted); }
.hero-badge {
    display: inline-block; font-size: 0.7rem; font-weight: 700;
    padding: 3px 12px; border-radius: 20px; margin-right: 0.5rem;
    background: rgba(0,212,255,0.1); color: var(--accent);
    border: 1px solid rgba(0,212,255,0.25); letter-spacing: 0.06em;
}

/* ── Table ── */
.pile-table { width:100%; border-collapse:collapse; font-size:0.8rem; }
.pile-table th {
    background: var(--bg-card2); color: var(--accent);
    padding: 0.55rem 0.9rem; border: 1px solid var(--border);
    font-size:0.7rem; text-transform:uppercase; letter-spacing:0.08em;
    font-weight:700; text-align:center;
}
.pile-table td {
    padding: 0.45rem 0.9rem; border: 1px solid var(--border);
    text-align:center; font-family:'Share Tech Mono',monospace;
}
.pile-table tr:nth-child(even) td { background: rgba(255,255,255,0.015); }
.pile-table td.ok   { color: var(--success); font-weight:700; }
.pile-table td.ng   { color: var(--danger);  font-weight:700; }
.pile-table td.warn { color: var(--warn);    font-weight:700; }

/* ── Alert boxes ── */
.alert { border-radius:10px; padding:0.8rem 1.1rem; margin:0.4rem 0; font-size:0.83rem; }
.alert-ok   { background:rgba(0,230,118,0.07); border:1px solid rgba(0,230,118,0.3); color:var(--success); }
.alert-ng   { background:rgba(255,61,87,0.07);  border:1px solid rgba(255,61,87,0.3); color:var(--danger); }
.alert-warn { background:rgba(255,171,0,0.07);  border:1px solid rgba(255,171,0,0.3); color:var(--warn); }
.alert-info { background:rgba(0,212,255,0.07);  border:1px solid rgba(0,212,255,0.3); color:var(--accent); }

/* ── Sidebar label ── */
[data-testid="stSidebar"] label { color: var(--muted) !important; font-size:0.78rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  BUG-FIX NOTES (สรุปจุดบกพร่องที่แก้ไข)
#
#  BUG 1: calculate_piles() แก้ไข DataFrame in-place โดยไม่ .copy()
#          → ทำให้เกิด SettingWithCopyWarning และผลลัพธ์อาจผิดพลาด
#          FIX: ใช้ df.copy() ก่อนเสมอ
#
#  BUG 2: sum_x2 หรือ sum_y2 อาจเป็น 0 (เสาเข็มทั้งหมดอยู่แนวเดียวกัน)
#          → ทำให้เกิด ZeroDivisionError
#          FIX: ตรวจสอบและ guard division ด้วย max(val, 1e-12)
#
#  BUG 3: marker size = reaction * 0.8 ทำให้ size ติดลบถ้ามีแรงดึง (Uplift)
#          → Plotly crash หรือ marker ไม่แสดง
#          FIX: marker size = abs(reaction) * scale, clamp ≥ 5
#
#  BUG 4: applymap() deprecated ตั้งแต่ pandas 2.1+ (ควรใช้ map())
#          FIX: ใช้ .map() แทน .applymap()
#
#  BUG 5: num_piles เป็น float จาก number_input → range() crash
#          FIX: int(num_piles) ทุกที่ที่ใช้
#
#  BUG 6: Default lists สำหรับ x_design, y_design ฯลฯ ไม่ scale
#          ตาม num_piles > 4 → IndexError / list ขนาดผิด
#          FIX: สร้าง default ด้วย logic ที่ scale ได้ถูกต้อง
#
#  BUG 7: Calculation ทำงานก่อน with col_viz: block เสร็จ
#          → visualization block อ่าน res_df ก่อนคำนวณ (โชคดีว่า
#          Python อ่าน sequential แต่ logic ยากติดตาม)
#          FIX: จัดลำดับ flow ให้ชัดเจน ใช้ session_state
# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
#  ENGINEERING ENGINE (BUG-FIXED)
# ─────────────────────────────────────────────────────────────
def calculate_piles(p_load: float, mx_load: float, my_load: float,
                    swl: float, piles_df: pd.DataFrame):
    """
    คำนวณแรงปฏิกิริยาในเสาเข็มกรณีเยื้องศูนย์ (SDM)

    สูตร: R_i = P/n + Mx_total·dy_i/Σdy² + My_total·dx_i/Σdx²
    """
    # ── BUG FIX 1: ทำงานกับ copy เสมอ ──
    df = piles_df.copy()

    # ── 1. จุดศูนย์กลางกลุ่มเสาเข็มจริง (CG of actual piles) ──
    x_bar = df['x_actual'].mean()
    y_bar = df['y_actual'].mean()

    # ── 2. Moment สุทธิรอบ CG ──
    mx_total = mx_load + (p_load * y_bar)
    my_total = my_load + (p_load * x_bar)

    # ── 3. พิกัด local จาก CG ──
    df['dx'] = df['x_actual'] - x_bar
    df['dy'] = df['y_actual'] - y_bar

    # ── 4. Second moment of pile group ──
    sum_dx2 = (df['dx'] ** 2).sum()
    sum_dy2 = (df['dy'] ** 2).sum()
    n = len(df)

    # ── BUG FIX 2: Guard ZeroDivisionError เมื่อเสาเข็มอยู่แนวเดียวกัน ──
    safe_sum_dx2 = sum_dx2 if sum_dx2 > 1e-12 else 1e-12
    safe_sum_dy2 = sum_dy2 if sum_dy2 > 1e-12 else 1e-12

    # ── 5. แรงในเสาเข็มแต่ละต้น ──
    df['reaction'] = (
        (p_load / n)
        + (mx_total * df['dy'] / safe_sum_dy2)
        + (my_total * df['dx'] / safe_sum_dx2)
    )

    # ── 6. ระยะเยื้องศูนย์ (deviation) ──
    df['deviation_mm'] = (
        np.sqrt(
            (df['x_actual'] - df['x_design']) ** 2
            + (df['y_actual'] - df['y_design']) ** 2
        ) * 1000
    )

    # ── 7. Pile moment จากการเยื้องศูนย์ ──
    df['pile_moment_tm'] = df['reaction'] * (df['deviation_mm'] / 1000)

    # ── 8. Status ──
    df['status'] = np.where(
        df['reaction'] > swl, "OVERLOAD",
        np.where(df['reaction'] < -0.001, "UPLIFT", "OK")
    )

    return df, x_bar, y_bar, mx_total, my_total, sum_dx2, sum_dy2


def make_default_coords(n: int):
    """สร้างพิกัดดีฟอลต์ตามจำนวนเสาเข็มที่ระบุ (grid layout)"""
    if n == 1:
        design_x, design_y = [0.0], [0.0]
    elif n == 2:
        design_x = [-0.75, 0.75];     design_y = [0.0,  0.0]
    elif n == 3:
        design_x = [-0.75, 0.75, 0.0]; design_y = [-0.45, -0.45, 0.65]
    elif n == 4:
        design_x = [-0.75, 0.75, -0.75,  0.75]
        design_y = [ 0.75,  0.75, -0.75, -0.75]
    else:
        # Grid: จัดแถวอัตโนมัติ
        cols = int(np.ceil(np.sqrt(n)))
        sp   = 1.5
        design_x, design_y = [], []
        for i in range(n):
            r, c = divmod(i, cols)
            design_x.append((c - (cols - 1) / 2) * sp)
            design_y.append((r - (int(np.ceil(n / cols)) - 1) / 2) * sp)

    # เพิ่ม noise เล็กน้อยเพื่อจำลองตำแหน่งตอกจริง
    rng = np.random.default_rng(42)
    actual_x = [x + rng.uniform(-0.05, 0.05) for x in design_x]
    actual_y = [y + rng.uniform(-0.05, 0.05) for y in design_y]

    return design_x, design_y, actual_x, actual_y


# ─────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────
def reset_state():
    keys = ['calculated', 'result_df', 'summary']
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]

if 'num_piles' not in st.session_state:
    st.session_state.num_piles = 4

# ─────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem;">
        <div style="font-size:2.5rem;">🏗️</div>
        <div style="font-size:1rem;font-weight:700;color:#00d4ff;letter-spacing:0.1em;">PILE ECCENTRICITY</div>
        <div style="font-size:0.7rem;color:#64748b;letter-spacing:0.06em;">SDM ANALYSIS TOOL</div>
    </div>
    <hr style="border-color:#1e293b;margin:0.5rem 0;">
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.72rem;color:#00d4ff;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:0.8rem 0 0.3rem;">⚡ แรงที่กระทำ</div>', unsafe_allow_html=True)
    p_input  = st.number_input("Axial Load P (tons)", min_value=0.0, value=120.0, step=5.0, format="%.1f")
    mx_input = st.number_input("Moment Mx (ton-m)", value=5.0, step=0.5, format="%.2f",
                                help="โมเมนต์รอบแกน X (ก่อให้เกิดแรงในแนว Y)")
    my_input = st.number_input("Moment My (ton-m)", value=2.0, step=0.5, format="%.2f",
                                help="โมเมนต์รอบแกน Y (ก่อให้เกิดแรงในแนว X)")

    st.markdown('<div style="font-size:0.72rem;color:#00d4ff;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:0.8rem 0 0.3rem;">🛡️ กำลังรับแรงเสาเข็ม</div>', unsafe_allow_html=True)
    swl_input  = st.number_input("SWL — กำลังรับแรงกด (tons)", min_value=1.0, value=40.0, step=1.0, format="%.1f")
    tolerance  = st.number_input("Tolerance ระยะเยื้องศูนย์ (mm)", min_value=0.0, value=75.0, step=5.0)

    st.markdown('<div style="font-size:0.72rem;color:#00d4ff;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:0.8rem 0 0.3rem;">📐 กลุ่มเสาเข็ม</div>', unsafe_allow_html=True)
    # ── BUG FIX 5: บังคับ int ──
    num_piles = int(st.number_input("จำนวนเสาเข็ม", min_value=2, max_value=24, value=4, step=1))

    st.markdown("")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown('<div class="calc-btn">', unsafe_allow_html=True)
        calc_btn = st.button("▶ คำนวณ", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b2:
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        clear_btn = st.button("↺ ล้างค่า", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if clear_btn:
        reset_state()
        st.rerun()

    st.markdown("""
    <div style="margin-top:2rem;padding:0.8rem;background:rgba(0,212,255,0.05);
                border-radius:8px;border:1px solid rgba(0,212,255,0.1);">
        <div style="font-size:0.68rem;color:#64748b;line-height:1.7;">
            <strong style="color:#00d4ff;">สูตรคำนวณ (SDM)</strong><br>
            R_i = P/n ± Mx·dy_i/Σdy² ± My·dx_i/Σdx²<br>
            <br>
            <strong style="color:#64748b;">อ้างอิง:</strong> ACI 318, AISC, วสท.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  MAIN LAYOUT
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <h1>🏗️ Pile Eccentricity Analysis — SDM Approach</h1>
    <p>วิเคราะห์แรงปฏิกิริยาเสาเข็มกรณีเยื้องศูนย์ สำหรับวิศวกรโครงสร้าง</p>
    <div style="margin-top:0.7rem;">
        <span class="hero-badge">SDM</span>
        <span class="hero-badge">ACI 318</span>
        <span class="hero-badge">วสท.</span>
        <span class="hero-badge">Plotly Interactive</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  INPUT TABLE
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="sec-head"><span>📍</span><h3>พิกัดเสาเข็ม — ตำแหน่งออกแบบ vs ตอกจริง</h3></div>', unsafe_allow_html=True)

# ── BUG FIX 6: Default data generator ที่ scale ถูกต้อง ──
dx, dy, ax, ay = make_default_coords(num_piles)

default_data = {
    "Pile_ID":  [f"P{i+1}" for i in range(num_piles)],
    "x_design": [round(v, 3) for v in dx],
    "y_design": [round(v, 3) for v in dy],
    "x_actual": [round(v, 3) for v in ax],
    "y_actual": [round(v, 3) for v in ay],
}
df_input = pd.DataFrame(default_data)

col_tbl, col_hint = st.columns([3, 1])
with col_tbl:
    edited_df = st.data_editor(
        df_input,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "Pile_ID":  st.column_config.TextColumn("Pile ID",    width="small"),
            "x_design": st.column_config.NumberColumn("X Design (m)", format="%.3f"),
            "y_design": st.column_config.NumberColumn("Y Design (m)", format="%.3f"),
            "x_actual": st.column_config.NumberColumn("X Actual (m)", format="%.3f"),
            "y_actual": st.column_config.NumberColumn("Y Actual (m)", format="%.3f"),
        },
    )
with col_hint:
    st.markdown("""
    <div style="background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.15);
                border-radius:10px;padding:1rem;font-size:0.76rem;color:#94a3b8;
                line-height:1.8;margin-top:0.2rem;">
        <strong style="color:#00d4ff;">📌 คำแนะนำ</strong><br>
        • จุดอ้างอิง (0,0) = แกนกลางเสา<br>
        • X → ทิศ East (+) / West (−)<br>
        • Y → ทิศ North (+) / South (−)<br>
        • ป้อนพิกัด <em>ตอกจริง</em> จากใบรายงานหน้างาน<br>
        • หน่วย: เมตร (m)
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  CALCULATION
# ─────────────────────────────────────────────────────────────
if calc_btn or st.session_state.get('calculated'):
    try:
        res_df, ex, ey, mxt, myt, sdx2, sdy2 = calculate_piles(
            p_input, mx_input, my_input, swl_input, edited_df
        )
        st.session_state['calculated'] = True

        # ── SUMMARY METRICS ──
        st.markdown('<div class="sec-head"><span>📊</span><h3>สรุปผลการวิเคราะห์</h3></div>', unsafe_allow_html=True)

        r_max    = res_df['reaction'].max()
        r_min    = res_df['reaction'].min()
        n_over   = (res_df['status'] == 'OVERLOAD').sum()
        n_uplift = (res_df['status'] == 'UPLIFT').sum()
        n_ok     = (res_df['status'] == 'OK').sum()
        util_max = r_max / swl_input * 100

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        cards = [
            (c1, "Global Eccen. X", f"{ex*1000:.1f}", "mm", "cyan", ""),
            (c2, "Global Eccen. Y", f"{ey*1000:.1f}", "mm", "cyan", ""),
            (c3, "R_max (กดสูงสุด)", f"{r_max:.2f}", "tons",
             "green" if r_max <= swl_input else "red",
             "ok" if r_max <= swl_input else "ng"),
            (c4, "R_min (กดน้อยสุด)", f"{r_min:.2f}", "tons",
             "green" if r_min >= 0 else "red",
             "ok" if r_min >= 0 else "warn"),
            (c5, "Utilization สูงสุด", f"{util_max:.1f}", "%",
             "green" if util_max <= 100 else "red",
             "ok" if util_max <= 100 else "ng"),
            (c6, "สถานะ OVERLOAD", str(n_over), "ต้น",
             "green" if n_over == 0 else "red",
             "ok" if n_over == 0 else "ng"),
        ]
        for col, label, val, unit, theme, badge_cls in cards:
            badge_html = ""
            if badge_cls == "ok":
                badge_html = '<span class="stat-badge badge-ok">✓ ปลอดภัย</span>'
            elif badge_cls == "ng":
                badge_html = '<span class="stat-badge badge-ng">✗ เกินกำลัง</span>'
            elif badge_cls == "warn":
                badge_html = '<span class="stat-badge badge-warn">⚠ ตรวจสอบ</span>'
            top_color = {"cyan": "#00d4ff", "green": "#00e676", "red": "#ff3d57"}.get(theme, "#00d4ff")
            with col:
                st.markdown(f"""
                <div class="stat-card" style="border-top-color:{top_color};">
                    <div class="stat-label">{label}</div>
                    <div class="stat-value" style="color:{top_color};">{val}</div>
                    <div class="stat-unit">{unit}</div>
                    {badge_html}
                </div>
                """, unsafe_allow_html=True)

        # ── VISUALIZATION ──
        st.markdown('<div class="sec-head"><span>🗺️</span><h3>แผนผังกลุ่มเสาเข็ม & กราฟแรง</h3></div>', unsafe_allow_html=True)

        col_v1, col_v2 = st.columns([1.3, 1])

        with col_v1:
            # ── Plan view (Plotly) ──
            # BUG FIX 3: marker size ต้องบวกเสมอ
            def safe_size(reactions, scale=2.5, base=12):
                return [max(abs(r) * scale + base, 6) for r in reactions]

            status_colors = {
                "OK":       "#00e676",
                "OVERLOAD": "#ff3d57",
                "UPLIFT":   "#ffab00",
            }
            marker_colors = [status_colors.get(s, "#aaa") for s in res_df['status']]

            fig_plan = go.Figure()

            # Design positions
            fig_plan.add_trace(go.Scatter(
                x=res_df['x_design'], y=res_df['y_design'],
                mode='markers',
                marker=dict(size=14, color='rgba(255,255,255,0.12)',
                            symbol='square', line=dict(color='#334155', width=1.5)),
                name='ตำแหน่งออกแบบ',
                hovertemplate="Design: (%{x:.3f}, %{y:.3f})<extra></extra>"
            ))

            # Lines connecting design → actual
            for _, row in res_df.iterrows():
                fig_plan.add_shape(type='line',
                    x0=row['x_design'], y0=row['y_design'],
                    x1=row['x_actual'], y1=row['y_actual'],
                    line=dict(color='rgba(255,171,0,0.4)', width=1, dash='dot'))

            # Actual positions
            fig_plan.add_trace(go.Scatter(
                x=res_df['x_actual'], y=res_df['y_actual'],
                mode='markers+text',
                text=res_df['Pile_ID'],
                textposition="top center",
                textfont=dict(size=10, color='white', family='Share Tech Mono'),
                marker=dict(
                    size=safe_size(res_df['reaction']),
                    color=res_df['reaction'],
                    colorscale=[[0, '#00e676'], [0.5, '#ffab00'], [1, '#ff3d57']],
                    showscale=True,
                    colorbar=dict(
                        title=dict(text="Reaction<br>(tons)", font=dict(color='#64748b', size=10)),
                        tickfont=dict(color='#64748b', size=9),
                        len=0.7, thickness=12,
                        bgcolor='rgba(0,0,0,0)',
                        bordercolor='#1e293b',
                    ),
                    line=dict(color='white', width=1.5),
                    cmin=0, cmax=swl_input,
                ),
                customdata=np.stack([res_df['reaction'], res_df['deviation_mm'], res_df['status']], axis=-1),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Actual: (%{x:.3f}, %{y:.3f})<br>"
                    "Reaction: <b>%{customdata[0]:.2f} t</b><br>"
                    "Deviation: %{customdata[1]:.1f} mm<br>"
                    "Status: <b>%{customdata[2]}</b>"
                    "<extra></extra>"
                ),
                name='ตำแหน่งตอกจริง',
            ))

            # Column center
            fig_plan.add_trace(go.Scatter(
                x=[0], y=[0], mode='markers',
                marker=dict(size=18, color='#00d4ff', symbol='cross',
                            line=dict(color='white', width=1.5)),
                name='ศูนย์กลางเสา',
                hovertemplate="Column Center (0,0)<extra></extra>"
            ))

            # CG actual
            fig_plan.add_trace(go.Scatter(
                x=[ex], y=[ey], mode='markers',
                marker=dict(size=12, color='#f5a623', symbol='diamond',
                            line=dict(color='white', width=1.5)),
                name=f'CG จริง ({ex*1000:.1f},{ey*1000:.1f} mm)',
                hovertemplate=f"CG Actual<br>({ex:.4f}, {ey:.4f}) m<extra></extra>"
            ))

            # Tolerance circles (dashed)
            theta = np.linspace(0, 2 * np.pi, 80)
            tol_m = tolerance / 1000
            for _, row in res_df.iterrows():
                fig_plan.add_trace(go.Scatter(
                    x=row['x_design'] + tol_m * np.cos(theta),
                    y=row['y_design'] + tol_m * np.sin(theta),
                    mode='lines',
                    line=dict(color='rgba(255,171,0,0.2)', width=0.8, dash='dot'),
                    showlegend=False, hoverinfo='skip'
                ))

            fig_plan.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(10,14,23,0)',
                plot_bgcolor='rgba(17,24,39,0.8)',
                height=440,
                margin=dict(l=10, r=10, t=30, b=30),
                xaxis=dict(title="X (m)", gridcolor='#1e293b', zerolinecolor='#334155',
                           tickfont=dict(color='#64748b', size=9)),
                yaxis=dict(title="Y (m)", gridcolor='#1e293b', zerolinecolor='#334155',
                           scaleanchor="x", scaleratio=1,
                           tickfont=dict(color='#64748b', size=9)),
                legend=dict(bgcolor='rgba(17,24,39,0.9)', bordercolor='#1e293b',
                            font=dict(color='#94a3b8', size=9), x=0.01, y=0.99),
                title=dict(text="Plan View — Pile Group", font=dict(color='#00d4ff', size=11), x=0.5),
            )
            st.plotly_chart(fig_plan, use_container_width=True)

        with col_v2:
            # ── Bar chart reaction per pile ──
            bar_colors = [status_colors.get(s, "#aaa") for s in res_df['status']]
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=res_df['Pile_ID'],
                y=res_df['reaction'],
                marker=dict(color=bar_colors,
                            line=dict(color='rgba(255,255,255,0.1)', width=0.5)),
                text=[f"{r:.1f}" for r in res_df['reaction']],
                textposition='outside',
                textfont=dict(color='white', size=9, family='Share Tech Mono'),
                customdata=res_df[['status', 'deviation_mm']].values,
                hovertemplate="<b>%{x}</b><br>Reaction: %{y:.2f} t<br>Status: %{customdata[0]}<extra></extra>",
                name='Reaction',
            ))
            fig_bar.add_hline(y=swl_input, line=dict(color='#ff3d57', width=1.5, dash='dash'),
                              annotation_text=f"SWL={swl_input}t",
                              annotation_font=dict(color='#ff3d57', size=9))
            fig_bar.add_hline(y=0, line=dict(color='#334155', width=0.8))

            fig_bar.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(17,24,39,0.8)',
                height=200,
                margin=dict(l=10, r=10, t=30, b=20),
                xaxis=dict(tickfont=dict(color='#94a3b8', size=9), gridcolor='#1e293b'),
                yaxis=dict(title="Reaction (t)", tickfont=dict(color='#64748b', size=8), gridcolor='#1e293b'),
                showlegend=False,
                title=dict(text="แรงปฏิกิริยาแต่ละต้น", font=dict(color='#00d4ff', size=11), x=0.5),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            # ── Deviation chart ──
            dev_colors = ['#ff3d57' if d > tolerance else '#00e676' for d in res_df['deviation_mm']]
            fig_dev = go.Figure()
            fig_dev.add_trace(go.Bar(
                x=res_df['Pile_ID'],
                y=res_df['deviation_mm'],
                marker=dict(color=dev_colors, line=dict(color='rgba(255,255,255,0.1)', width=0.5)),
                text=[f"{d:.1f}" for d in res_df['deviation_mm']],
                textposition='outside',
                textfont=dict(color='white', size=9, family='Share Tech Mono'),
                name='Deviation',
            ))
            fig_dev.add_hline(y=tolerance, line=dict(color='#ffab00', width=1.5, dash='dash'),
                              annotation_text=f"Tol={tolerance:.0f}mm",
                              annotation_font=dict(color='#ffab00', size=9))
            fig_dev.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(17,24,39,0.8)',
                height=200,
                margin=dict(l=10, r=10, t=30, b=20),
                xaxis=dict(tickfont=dict(color='#94a3b8', size=9), gridcolor='#1e293b'),
                yaxis=dict(title="Deviation (mm)", tickfont=dict(color='#64748b', size=8), gridcolor='#1e293b'),
                showlegend=False,
                title=dict(text="ระยะเยื้องศูนย์แต่ละต้น", font=dict(color='#00d4ff', size=11), x=0.5),
            )
            st.plotly_chart(fig_dev, use_container_width=True)

        # ── DETAILED TABLE ──
        st.markdown('<div class="sec-head"><span>📋</span><h3>ตารางผลการวิเคราะห์รายต้น</h3></div>', unsafe_allow_html=True)

        tbl_df = res_df[['Pile_ID', 'x_actual', 'y_actual',
                          'deviation_mm', 'reaction', 'pile_moment_tm', 'status']].copy()

        rows_html = ""
        for _, row in tbl_df.iterrows():
            s = row['status']
            s_cls = "ok" if s == "OK" else ("ng" if s == "OVERLOAD" else "warn")
            s_icon = "✓" if s == "OK" else ("✗" if s == "OVERLOAD" else "⚠")
            dev_cls = "ng" if row['deviation_mm'] > tolerance else "ok"
            react_cls = "ng" if row['reaction'] > swl_input or row['reaction'] < 0 else "ok"
            rows_html += f"""
            <tr>
              <td><strong>{row['Pile_ID']}</strong></td>
              <td>{row['x_actual']:.3f}</td>
              <td>{row['y_actual']:.3f}</td>
              <td class="{dev_cls}">{row['deviation_mm']:.1f}</td>
              <td class="{react_cls}">{row['reaction']:.2f}</td>
              <td>{row['pile_moment_tm']:.3f}</td>
              <td class="{s_cls}">{s_icon} {s}</td>
            </tr>"""

        st.markdown(f"""
        <table class="pile-table">
          <thead>
            <tr>
              <th>Pile ID</th><th>X จริง (m)</th><th>Y จริง (m)</th>
              <th>Deviation (mm)</th><th>Reaction (t)</th>
              <th>Pile Moment (t·m)</th><th>สถานะ</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)

        # ── WARNINGS & ENGINEERING NOTES ──
        st.markdown('<div class="sec-head"><span>⚠️</span><h3>การแจ้งเตือนและข้อสังเกต</h3></div>', unsafe_allow_html=True)

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            over_tol = res_df[res_df['deviation_mm'] > tolerance]
            if not over_tol.empty:
                ids = ', '.join(over_tol['Pile_ID'].tolist())
                st.markdown(f'<div class="alert alert-ng">❌ <strong>เยื้องศูนย์เกินมาตรฐาน ({tolerance:.0f} mm):</strong><br>{ids}<br><small>→ ต้องทำ Pile Head Modification หรือยื่น Engineering Justification</small></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert alert-ok">✅ <strong>ระยะเยื้องศูนย์ทุกต้นอยู่ในเกณฑ์มาตรฐาน</strong></div>', unsafe_allow_html=True)

            if n_over > 0:
                st.markdown(f'<div class="alert alert-ng">❌ <strong>OVERLOAD {n_over} ต้น:</strong> แรงกดเกิน SWL<br><small>→ พิจารณาขยาย Pile Cap หรือเพิ่มเสาเข็มแซม</small></div>', unsafe_allow_html=True)
            if n_uplift > 0:
                st.markdown(f'<div class="alert alert-warn">⚠️ <strong>UPLIFT {n_uplift} ต้น:</strong> ตรวจพบแรงดึง<br><small>→ ตรวจสอบรอยต่อหัวเข็มและ Tension capacity</small></div>', unsafe_allow_html=True)
            if n_over == 0 and n_uplift == 0:
                st.markdown('<div class="alert alert-ok">✅ <strong>ไม่พบเสาเข็มรับแรงเกินกำลัง</strong> — ทุกต้นอยู่ในเกณฑ์ปลอดภัย</div>', unsafe_allow_html=True)

        with col_w2:
            st.markdown(f"""
            <div class="alert alert-info">
            <strong>📐 ผลการวิเคราะห์เชิงสรุป</strong><br><br>
            • จำนวนเสาเข็ม: <strong>{len(res_df)} ต้น</strong><br>
            • CG เยื้อง: X = {ex*1000:.1f} mm, Y = {ey*1000:.1f} mm<br>
            • Mx สุทธิ: {mxt:.3f} t·m &nbsp;|&nbsp; My สุทธิ: {myt:.3f} t·m<br>
            • Σdx² = {sdx2:.4f} m² &nbsp;|&nbsp; Σdy² = {sdy2:.4f} m²<br>
            • Utilization สูงสุด: <strong>{util_max:.1f}%</strong><br>
            • OK: {n_ok} ต้น | OVERLOAD: {n_over} ต้น | UPLIFT: {n_uplift} ต้น
            </div>
            """, unsafe_allow_html=True)

        # ── EXPORT ──
        st.markdown("<br>", unsafe_allow_html=True)
        export_df = res_df[['Pile_ID', 'x_design', 'y_design',
                             'x_actual', 'y_actual', 'deviation_mm',
                             'reaction', 'pile_moment_tm', 'status']].copy()
        export_df.columns = ['Pile_ID', 'X_Design(m)', 'Y_Design(m)',
                              'X_Actual(m)', 'Y_Actual(m)', 'Deviation(mm)',
                              'Reaction(t)', 'PileMoment(t-m)', 'Status']
        csv_bytes = export_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            "⬇️  Export ผลการวิเคราะห์ (CSV)",
            data=csv_bytes,
            file_name="pile_eccentricity_result.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.markdown(f'<div class="alert alert-ng">❌ <strong>เกิดข้อผิดพลาด:</strong> {e}</div>', unsafe_allow_html=True)

else:
    # ── Welcome screen ──
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                height:50vh;gap:1rem;text-align:center;color:#64748b;">
        <div style="font-size:4rem;filter:drop-shadow(0 0 20px rgba(0,212,255,0.3));">⚙️</div>
        <div style="font-size:1.1rem;color:#e2e8f0;font-weight:600;">พร้อมวิเคราะห์</div>
        <div style="font-size:0.83rem;max-width:400px;line-height:1.8;">
            ตั้งค่าพารามิเตอร์ในแถบซ้าย กรอกพิกัดเสาเข็มในตารางด้านบน<br>
            แล้วกดปุ่ม <strong style="color:#00d4ff;">▶ คำนวณ</strong>
        </div>
        <div style="display:flex;gap:1.5rem;margin-top:0.5rem;font-size:0.73rem;color:#334155;">
            <span>SDM Analysis</span><span>•</span>
            <span>Interactive Plot</span><span>•</span>
            <span>Export CSV</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:#1e293b;margin:2rem 0 0.5rem;">
<div style="text-align:center;font-size:0.68rem;color:#334155;padding-bottom:0.5rem;">
    Pile Eccentricity Analysis Tool · SDM Approach · ACI 318 / วสท. ·
    สำหรับการประมาณการเบื้องต้น — กรุณาตรวจสอบโดยวิศวกรที่มีใบอนุญาต
</div>
""", unsafe_allow_html=True)
