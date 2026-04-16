import streamlit as st
import pandas as pd
import io

# ========================
# 計算函式
# ========================
def calculate_bonus(deal_counts, extra_classes, loyalty_counts, upgrade_counts, is_full_time, brand_count):
    # 1. 體驗成交獎金
    d_total = (deal_counts.get("當天", 0) * 80 + 
               deal_counts.get("48小時", 0) * 60 + 
               deal_counts.get("7天內", 0) * 50)

    # 2. 補位獎金
    c_total = extra_classes * 30

    # 3. 回流獎勵獎金 (STP-T)
    l_total = (loyalty_counts.get("10堂", 0) * 100 + 
               loyalty_counts.get("20堂", 0) * 200 + 
               loyalty_counts.get("30堂", 0) * 300 + 
               loyalty_counts.get("40堂", 0) * 500)

    # 4. 結構升級獎金
    upgrade_prices = {"1對2變1對3": 100, "團課變期班": 150, "包班成立": 300}
    u_total = sum(upgrade_prices.get(name, 0) * count for name, count in upgrade_counts.items())

    # 5. 品牌知名度提升獎金 (新增功能)
    base_val = 5 if is_full_time else 2
    if brand_count == 0:
        b_total = -200
    elif brand_count < base_val:
        b_total = -100
    else:
        # 每增加 5 位加 200
        extra_units = (brand_count - base_val) // 5
        b_total = extra_units * 200

    # 6. 月轉換高手筆數累計
    total_deals = (sum(deal_counts.values()) + 
                   sum(upgrade_counts.values()) + 
                   sum(loyalty_counts.values()) + 
                   extra_classes)
    
    monthly_bonus = 0
    if total_deals >= 50:
        monthly_bonus = 5000
    elif total_deals >= 30:
        monthly_bonus = 2000
    
    final_total = d_total + c_total + l_total + u_total + monthly_bonus + b_total

    return final_total, total_deals, monthly_bonus, l_total, d_total, u_total, b_total

# ========================
# 產生 Excel 檔案的函式
# ========================
def generate_excel(total_v, result, deal_dict, classes, loyalty_dict, upgrades, d_bonus, l_bonus, u_bonus, m_bonus, b_bonus, emp_type, b_count):
    data = {
        "報表項目": [
            "【總結】",
            "總轉換筆數 (筆)", "本月預計總獎金 (元)",
            "【項目統計】",
            "體驗成交 (筆)", "補開課程 (次)", "回流人數 (人)", "結構升級 (次)", "品牌推廣人數 (位)",
            "【獎金明細】",
            "員工身份", "體驗成交獎金 (元)", "補位獎金 (元)", "加發回流獎金 (元)", "結構升級獎金 (元)", "品牌知名度獎金 (元)", "月轉換高手獎勵 (元)"
        ],
        "數據": [
            "", 
            total_v, result,
            "", 
            sum(deal_dict.values()), classes, sum(loyalty_dict.values()), sum(upgrades.values()), b_count,
            "", 
            emp_type, d_bonus, classes * 30, l_bonus, u_bonus, b_bonus, m_bonus
        ]
    }
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='當月獎金結算')
    
    return output.getvalue()

# ========================
# Streamlit UI
# ========================
st.set_page_config(page_title="業務獎金計算系統 v2", layout="centered")
st.title("業務獎金計算系統")

# 初始化 Session State
if 'report_text' not in st.session_state:
    st.session_state.report_text = ""
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = None

# --- 第一區：體驗成交 ---
st.header("1. 體驗成交與品牌推廣")
col1, col2, col3 = st.columns(3)
with col1:
    d0 = st.number_input("當天成交(筆)", min_value=0, step=1)
with col2:
    d12 = st.number_input("48小時(筆)", min_value=0, step=1)
with col3:
    d37 = st.number_input("7天內(筆)", min_value=0, step=1)

deal_dict = {"當天": d0, "48小時": d12, "7天內": d37}

st.subheader("品牌知名度提升")
b_col1, b_col2 = st.columns(2)
with b_col1:
    emp_type = st.selectbox("員工身份", ["正職人員", "兼職人員"])
with b_col2:
    brand_count = st.number_input("知名度推廣人數 (位)", min_value=0, step=1)

is_full_time = (emp_type == "正職人員")

# --- 第二區：補位與回流 ---
st.header("2. 補位與回流獎金")
classes = st.number_input("補開課 / 次數", min_value=0, step=1)

st.subheader("加發回流購課獎金 (STP-T)")
la, lb, lc, ld = st.columns(4)
with la:
    l10 = st.number_input("10堂 (人)", min_value=0, step=1)
with lb:
    l20 = st.number_input("20堂 (人)", min_value=0, step=1)
with lc:
    l30 = st.number_input("30堂 (人)", min_value=0, step=1)
with ld:
    l40 = st.number_input("40堂 (人)", min_value=0, step=1)

loyalty_dict = {"10堂": l10, "20堂": l20, "30堂": l30, "40堂": l40}

# --- 第三區：結構升級 ---
st.header("3. 結構升級獎/當月轉換")
u1 = st.number_input("1對2 變 1對3以上 / 次數", min_value=0, step=1)
u2 = st.number_input("團課 變 期班 / 次數", min_value=0, step=1)
u3 = st.number_input("包班成立 / 次數", min_value=0, step=1)

upgrades = {"1對2變1對3": u1, "團課變期班": u2, "包班成立": u3}

# --- 計算按鈕 ---
st.divider()
if st.button("開始計算總獎金", type="primary"):
    st.balloons()
    
    # 執行計算
    (result, total_v, m_bonus, l_bonus, d_bonus, u_bonus, b_bonus) = calculate_bonus(
        deal_dict, classes, loyalty_dict, upgrades, is_full_time, brand_count
    )
    
    # 儲存狀態
    st.session_state.total_v = total_v
    st.session_state.m_bonus = m_bonus
    
    # 產生文字報表
    st.session_state.report_text = f"""業務獎金結算報表
----------------------
身份：{emp_type}
總轉換筆數：{total_v} 筆
本月總獎金：NT$ {result}

項目統計：
- 體驗成交：{sum(deal_dict.values())} 筆
- 品牌推廣：{brand_count} 位
- 補開課程：{classes} 筆
- 回流人數：{sum(loyalty_dict.values())} 人
- 結構升級：{sum(upgrades.values())} 次

獎金明細：
- 體驗成交獎金：{d_bonus} 元
- 品牌知名度獎金：{b_bonus} 元
- 補位獎金：{classes * 30} 元
- 加發回流獎金：{l_bonus} 元
- 結構升級獎金：{u_bonus} 元
- 月轉換高手獎勵：{m_bonus} 元
"""

    # 產生 Excel
    st.session_state.excel_data = generate_excel(
        total_v, result, deal_dict, classes, loyalty_dict, 
        upgrades, d_bonus, l_bonus, u_bonus, m_bonus, b_bonus, emp_type, brand_count
    )

# --- 顯示與下載 ---
if st.session_state.excel_data is not None:
    st.success("計算完成")
    
    with st.expander("查看詳細報表", expanded=True):
        st.text(st.session_state.report_text)
        
        if st.session_state.total_v >= 30:
            st.info(f"總筆數 {st.session_state.total_v} 已達標。包含高手獎勵 {st.session_state.m_bonus} 元")
        else:
            st.warning(f"目前總筆數 {st.session_state.total_v}。距離高手獎金還差 {30 - st.session_state.total_v} 筆")

    st.download_button(
        label="下載 Excel 結算檔案",
        data=st.session_state.excel_data,
        file_name=f"業務獎金結算_{emp_type}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
