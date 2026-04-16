import streamlit as st
import pandas as pd
import io
from openpyxl.styles import Font, Alignment, PatternFill
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

    # 5. 品牌知名度提升獎金與備註
    base_val = 5 if is_full_time else 2
    b_note = ""
    if brand_count == 0:
        b_total = -200
        b_note = "推廣人數為 0"
    elif brand_count < base_val:
        b_total = -100
        b_note = f"未達基本門檻 ({base_val}位)"
    elif brand_count == base_val:
        b_total = 0
        b_note = "符合基本門檻"
    else:
        extra_units = (brand_count - base_val) // 5
        b_total = extra_units * 200
        b_note = f"加發 {extra_units} 組獎金"

    # 6. 月轉換高手筆數累計
    total_deals = (sum(deal_counts.values()) + sum(upgrade_counts.values()) + 
                   sum(loyalty_counts.values()) + extra_classes)
    monthly_bonus = 5000 if total_deals >= 50 else (2000 if total_deals >= 30 else 0)
    
    final_total = d_total + c_total + l_total + u_total + monthly_bonus + b_total
    return final_total, total_deals, monthly_bonus, l_total, d_total, u_total, b_total, b_note

# ========================
# 產生橫向格式化 Excel 的函式
# ========================
def generate_side_by_side_excel(total_v, result, deal_dict, classes, loyalty_dict, upgrades, d_bonus, l_bonus, u_bonus, m_bonus, b_bonus, b_note, emp_type, b_count):
    # 左側資料：統計與總結
    stats_data = {
        "統計類別": ["總結", "總結", "統計", "統計", "統計", "統計", "統計"],
        "項目名稱": ["總轉換筆數", "預計總獎金", "體驗成交", "補開課程", "回流人數", "結構升級", "品牌推廣人數"],
        "數值": [total_v, result, sum(deal_dict.values()), classes, sum(loyalty_dict.values()), sum(upgrades.values()), b_count]
    }
    
    # 右側資料：明細與備註
    details_data = {
        "明細項目": ["員工身份", "體驗成交獎金", "補位獎金", "回流獎金", "結構升級獎金", "品牌知名度獎金", "月高手獎勵", "獎金說明備註"],
        "金額/內容": [emp_type, d_bonus, classes * 30, l_bonus, u_bonus, b_bonus, m_bonus, b_note]
    }
    
    df_stats = pd.DataFrame(stats_data)
    df_details = pd.DataFrame(details_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # 寫入左側表格 (從 A1 開始)
        df_stats.to_excel(writer, index=False, sheet_name='獎金結算', startcol=0)
        # 寫入右側表格 (從 E1 開始，中間空一欄)
        df_details.to_excel(writer, index=False, sheet_name='獎金結算', startcol=4)
        
        workbook = writer.book
        worksheet = writer.sheets['獎金結算']
        
        # 樣式定義
        header_fill = PatternFill(start_color="44546A", end_color="44546A", fill_type="solid") # 深藍色調
        header_font = Font(color="FFFFFF", bold=True)
        center_align = Alignment(horizontal="center", vertical="center")
        red_font = Font(color="FF0000", bold=True)

        # 格式化所有標題列 (第一列的 A,B,C 欄位 與 E,F 欄位)
        for col_idx in [1, 2, 3, 5, 6]:
            cell = worksheet.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align

        # 調整欄寬與內容置中
        all_cols = [1, 2, 3, 4, 5, 6] # A,B,C (左) D (空) E,F (右)
        for col_idx in all_cols:
            worksheet.column_dimensions[get_column_letter(col_idx)].width = 18
            for row in range(1, worksheet.max_row + 1):
                cell = worksheet.cell(row=row, column=col_idx)
                cell.alignment = center_align
                # 負數標紅 (檢查 C 欄與 F 欄的數值)
                if col_idx in [3, 6]:
                    if isinstance(cell.value, (int, float)) and cell.value < 0:
                        cell.font = red_font

    return output.getvalue()

# ========================
# Streamlit UI
# ========================
st.set_page_config(page_title="業務獎金計算系統 v4", layout="wide") # 使用寬版介面
st.title("💰 業務獎金結算與導出系統")

# 初始化 Session State
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = None

# UI 佈局
main_col1, main_col2 = st.columns([1, 1])

with main_col1:
    st.header("1. 體驗與推廣")
    d_c1, d_c2, d_c3 = st.columns(3)
    with d_c1: d0 = st.number_input("當天成交", min_value=0, step=1)
    with d_c2: d12 = st.number_input("48小時", min_value=0, step=1)
    with d_c3: d37 = st.number_input("7天內", min_value=0, step=1)
    
    st.divider()
    emp_type = st.radio("員工身份", ["正職人員", "兼職人員"], horizontal=True)
    brand_count = st.number_input("知名度推廣人數 (位)", min_value=0, step=1)

with main_col2:
    st.header("2. 課程與升級")
    classes = st.number_input("補開課次數", min_value=0, step=1)
    
    st.subheader("回流購課 (人)")
    la, lb, lc, ld = st.columns(4)
    with la: l10 = st.number_input("10堂", min_value=0, step=1)
    with lb: l20 = st.number_input("20堂", min_value=0, step=1)
    with lc: l30 = st.number_input("30堂", min_value=0, step=1)
    with ld: l40 = st.number_input("40堂", min_value=0, step=1)
    
    st.subheader("結構升級 (次)")
    u_c1, u_c2, u_c3 = st.columns(3)
    with u_c1: u1 = st.number_input("1對2變3", min_value=0, step=1)
    with u_c2: u2 = st.number_input("團變期", min_value=0, step=1)
    with u_c3: u3 = st.number_input("包班", min_value=0, step=1)

# 計算邏輯
if st.button("開始計算並生成報表", type="primary", use_container_width=True):
    deal_dict = {"當天": d0, "48小時": d12, "7天內": d37}
    loyalty_dict = {"10堂": l10, "20堂": l20, "30堂": l30, "40堂": l40}
    upgrades = {"1對2變1對3": u1, "團課變期班": u2, "包班成立": u3}
    
    (result, total_v, m_bonus, l_bonus, d_bonus, u_bonus, b_bonus, b_note) = calculate_bonus(
        deal_dict, classes, loyalty_dict, upgrades, (emp_type == "正職人員"), brand_count
    )
    
    st.session_state.excel_data = generate_side_by_side_excel(
        total_v, result, deal_dict, classes, loyalty_dict, 
        upgrades, d_bonus, l_bonus, u_bonus, m_bonus, b_bonus, b_note, emp_type, brand_count
    )
    st.balloons()
    st.success(f"計算完畢！本月總獎金預計為：NT$ {result}")

# 下載區塊
if st.session_state.excel_data:
    st.divider()
    st.download_button(
        label="📥 下載對齊美化版 Excel 報表",
        data=st.session_state.excel_data,
        file_name=f"業務獎金結算_{emp_type}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
