import streamlit as st

# 設定網頁標題與圖示
st.set_page_config(page_title="業務獎金計算系統", page_icon="💰")

def calculate_bonus(days_to_deal, extra_classes, loyalty_sessions, upgrade_type, monthly_deals):
    total = 0
    # 1. 體驗成交
    if days_to_deal == 0: total += 80
    elif days_to_deal <= 2: total += 60
    elif days_to_deal <= 7: total += 50
    # 2. 補位獎金
    total += extra_classes * 30
    # 3. 加發回流購物金
    if loyalty_sessions >= 40: total += 500
    elif loyalty_sessions >= 30: total += 300
    elif loyalty_sessions >= 20: total += 200
    elif loyalty_sessions >= 10: total += 100
    # 4. 結構升級獎
    upgrade_map = {"無": 0, "1對2變1對3": 100, "團課變期班": 150, "包班成立": 300}
    total += upgrade_map.get(upgrade_type, 0)
    # 5. 月轉換獎高手
    if monthly_deals >= 50: total += 5000
    elif monthly_deals > 30: total += 2000
    return total

# 網頁介面開發
st.title("💰 業務獎金自動計算")
st.markdown("請輸入各項指標，系統將自動計算本月預計獎金。")

with st.form("bonus_form"):
    col1, col2 = st.columns(2)
    with col1:
        days = st.number_input("成交天數 (0=當天)", min_value=0, value=0, step=1)
        classes = st.number_input("補位次數", min_value=0, value=0, step=1)
        loyalty = st.number_input("購買堂數 (回流)", min_value=0, value=0, step=1)
    with col2:
        upgrade = st.selectbox("結構升級類型", ["無", "1對2變1對3", "團課變期班", "包班成立"])
        monthly = st.number_input("本月總轉換筆數", min_value=0, value=0, step=1)
    
    submit = st.form_submit_button("立即計算")

if submit:
    result = calculate_bonus(days, classes, loyalty, upgrade, monthly)
    st.balloons() # 增加一點成功特效
    st.success(f"### 本月預計總獎金： TWD {result:,} 元")
