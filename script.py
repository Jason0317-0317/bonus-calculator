import streamlit as st

# 計算函式（保留你的邏輯）
def calculate_bonus(days_to_deal, extra_classes, loyalty_sessions, upgrade_counts, monthly_deals):
    total = 0

    # 1. 體驗成交
    if days_to_deal == 0:
        total += 80
    elif days_to_deal <= 2:
        total += 60
    elif days_to_deal <= 7:
        total += 50

    # 2. 補位獎金
    total += extra_classes * 30

    # 3. 回流購物金
    if loyalty_sessions >= 40:
        total += 500
    elif loyalty_sessions >= 30:
        total += 300
    elif loyalty_sessions >= 20:
        total += 200
    elif loyalty_sessions >= 10:
        total += 100

    # 4. 結構升級獎
    upgrade_prices = {
        "1對2變1對3": 100,
        "團課變期班": 150,
        "包班成立": 300
    }

    for name, count in upgrade_counts.items():
        total += upgrade_prices.get(name, 0) * count

    # 5. 月轉換獎
    if monthly_deals >= 50:
        total += 5000
    elif monthly_deals > 30:
        total += 2000

    return total


# ========================
# 🎯 Streamlit UI
# ========================

st.title("💰 業務獎金計算系統")

st.header("📊 請輸入資料")

days = st.number_input("成交天數 (當天=0)", min_value=0, step=1)
classes = st.number_input("補位次數", min_value=0, step=1)
loyalty = st.number_input("購買堂數", min_value=0, step=1)

st.subheader("📈 結構升級獎")
u1 = st.number_input("1對2變1對3 次數", min_value=0, step=1)
u2 = st.number_input("團課變期班 次數", min_value=0, step=1)
u3 = st.number_input("包班成立 次數", min_value=0, step=1)

monthly = st.number_input("本月轉換筆數", min_value=0, step=1)

# 包成 dict
upgrades = {
    "1對2變1對3": u1,
    "團課變期班": u2,
    "包班成立": u3
}

# 按鈕
if st.button("🔥 計算獎金"):
    result = calculate_bonus(days, classes, loyalty, upgrades, monthly)

    st.success("計算完成！")

    st.write(f"📌 升級統計：{u1} / {u2} / {u3}")
    st.write(f"📌 本月轉換：{monthly}")

    st.markdown(f"## 💵 總獎金：{result} 元")
