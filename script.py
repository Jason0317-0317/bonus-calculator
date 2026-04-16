import streamlit as st
import pandas as pd
import io
from openpyxl.styles import Font, Alignment, PatternFill, Color
from openpyxl.utils import get_column_letter

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

    # 5. 品牌知名度提升獎金與備註 (新增邏輯)
    base_val = 5 if is_full_time else 2
    b_note = ""
    if brand_count == 0:
        b_total = -200
        b_note = "【扣款】推廣人數為 0"
    elif brand_count < base_val:
        b_total = -100
        b_note = f"【扣款】未達基本門檻 ({base_val}位)"
    elif brand_count == base_val:
        b_total = 0
        b_note = "符合基本門檻"
    else:
        extra_units = (brand_count - base_val) // 5
        b_total = extra_units * 200
        b_note = f"【加給】超過門檻，加發 {extra_units} 組獎金"

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

    return final_total, total_deals, monthly_bonus, l_total, d_total, u_total, b_total, b_note

# ========================
# 產生格式化 Excel 的函式
# ========================
def generate_formatted_excel(total_v, result, deal_dict, classes, loyalty_dict, upgrades, d_bonus, l_bonus, u_bonus, m_bonus, b_bonus, b_note, emp_type, b_count):
    # 建立 DataFrame
    data = {
        "分類": ["總結", "總結", "統計", "統計", "統計", "統計", "統計", "明細", "明細", "明細", "明細", "明細", "明細", "明細", "備註"],
        "報表項目": [
            "總轉換筆數 (筆)", "預計總獎金 (元)",
            "體驗成交 (筆)", "補開課程 (次)", "回流人數 (人)", "結構升級 (次)", "品牌推廣人數 (位)",
            "員工身份", "體驗成交獎金", "補位獎金", "回流獎金", "結構升級獎金", "品牌知名度獎金", "月轉換高手獎勵",
            "獎金變動說明"
        ],
        "數據內容": [
            total_v, result,
            sum(deal_dict.values()), classes, sum(loyalty_dict.values()), sum(upgrades.values()), b_count,
            emp_type, d_bonus, classes * 30, l_bonus, u_bonus, b_bonus, m_bonus,
            b_note
        ]
    }
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    
    # 開始寫入 Excel 並進行格式化
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='獎金結算表')
        workbook = writer.book
        worksheet = writer.sheets['獎金結算表']
        
        # 1. 樣式定義
        header_fill = PatternFill(start_color="333333", end_color="333333", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        center_align = Alignment(horizontal="center", vertical="center")
        red_font = Font(color="FF0000", bold=True) # 扣錢用紅色
        
        # 2. 格式化標題列
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align
            
        # 3. 調整欄寬與內容格式
        for i, col in enumerate(df.columns):
            column_len = df[col].astype(str).str.len().max()
            column_len = max(column_len, len(col)) + 4
            worksheet.column_dimensions[get_column_letter(i+1)].width = column_len
            
            # 將所有內容居中
            for row in range(2, worksheet.max_row + 1):
                worksheet.cell(row=row, column=i+1).alignment = center_align
                
                # 如果是「數據內容」欄位且值小於 0，標註紅色
                if col == "數據內容":
                    val = worksheet.cell(row=row, column=i+1).value
                    if isinstance(val, (int, float)) and val < 0:
                        worksheet.cell(row=row, column=i+1).font = red_font

    return output.getvalue()

# ========================
# Streamlit UI
# ========================
st.set_page_config(page_title="業務獎金計算系統 v3", layout="centered")
st.title("業務獎金計算系統")

# 初始化 Session State
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = None

# --- 第一區：體驗成交與品牌推廣 ---
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

# --- 第二區：補位與回流 ---
st.header("2. 補位與回流獎金")
classes = st.number_input("補開課 / 次數", min_value=0, step=1)
la, lb, lc, ld = st.columns(4)
with la: l10 = st.number_input("10堂", min_value=0, step=1)
with lb: l20 = st.number_input("20堂", min_value=0, step=1)
with lc: l30 = st.number_input("30堂", min_value=0, step=1)
with ld: l40 = st.number_input("40堂", min_value=0, step=1)
loyalty_dict = {"10堂": l10, "20堂": l20, "30堂": l30, "40堂": l40}

# --- 第三區：結構升級 ---
st.header("3. 結構升級獎/當月轉換")
u1 = st.number_input("1對2 變 1對3以上", min_value=0, step=1)
u2 = st.number_input("團課 變 期班", min_value=0, step=1)
u3 = st.number_input("包班成立", min_value=0, step=1)
upgrades = {"1對2變1對3": u1, "團課變期班": u2, "包班成立": u3}

# --- 計算按鈕 ---
st.divider()
if st.button("開始計算總獎金", type="primary"):
    st.balloons()
    
    is_full_time = (emp_type == "正職人員")
    (result, total_v, m_bonus, l_bonus, d_bonus, u_bonus, b_bonus, b_note) = calculate_bonus(
        deal_dict, classes, loyalty_dict, upgrades, is_full_time, brand_count
    )
    
    st.session_state.total_v = total_v
    st.session_state.m_bonus = m_bonus
    
    # 畫面上顯示的報表
    st.session_state.report_text = f"""業務獎金結算報表
----------------------
身份：{emp_type}
總轉換：{total_v} 筆 / 獎金：NT$ {result}
品牌推廣狀況：{b_note} (獎金: {b_bonus} 元)
"""
    # 產生格式化 Excel
    st.session_state.excel_data = generate_formatted_excel(
        total_v, result, deal_dict, classes, loyalty_dict, 
        upgrades, d_bonus, l_bonus, u_bonus, m_bonus, b_bonus, b_note, emp_type, brand_count
    )

# --- 顯示與下載 ---
if st.session_state.excel_data is not None:
    st.success("計算完成")
    st.info(st.session_state.report_text)
    
    st.download_button(
        label="下載 格式化 Excel 結算檔案",
        data=st.session_state.excel_data,
        file_name=f"業務獎金結算_{emp_type}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
