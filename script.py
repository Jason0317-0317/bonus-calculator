import streamlit as st

# ========================
# 🧮 計算函式
# ========================
def calculate_bonus(deal_counts, extra_classes, loyalty_sessions, upgrade_counts, monthly_deals):
    total = 0

    # 1. 體驗成交 (改為筆數累計)
    # deal_counts 格式範例: {"當天": 2, "1-2天": 1, "3-7天": 0}
    total += deal_counts.get("當天", 0) * 80
    total += deal_counts.get("1-2天", 0) * 60
    total += deal_counts.get("3-7天", 0) * 50

    # 2. 補位獎金
    total += extra_classes * 30

    # 3. 回流購物金 (維持階梯式獎勵)
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

# --- 第一區：體驗成交 ---
st.header("✨ 1. 體驗成交筆數")
col1, col2, col3 = st.columns(3)
with col1:
    d0 = st.number_input("當天成交 (筆)", min_value=0, step=1)
with col2:
    d12 = st.number_input("1-2天內 (筆)", min_value=0, step=1)
with col3:
    d37 = st.number_input("3-7天內 (筆)", min_value=0, step=1)

deal_dict = {"當天": d0, "1-2天": d12, "3-7天": d37}

# --- 第二區：基本活動 ---
st.header("📊 2. 基礎與回流")
c1, c2 = st.columns(2)
with c1:
    classes = st.number_input("補位次數", min_value=0, step=1)
with c2:
    loyalty = st.number_input("購買堂數 (回流獎勵用)", min_value=0, step=1)

# --- 第三區：結構升級 ---
st.header("📈 3. 結構升級獎")
u1 = st.number_input("1對2變1對3 次數", min_value=0, step=1)
u2 = st.number_input("團課變期班 次數", min_value=0, step=1)
u3 = st.number_input("包班成立 次數", min_value=0, step=1)

upgrades = {"1對2變1對3": u1, "團課變期班": u2, "包班成立": u3}

# --- 第四區：月總結 ---
st.header("🏆 4. 全月轉換成就")
monthly = st.number_input("本月總轉換筆數", min_value=0, step=1)

# --- 計算按鈕 ---
st.divider()
if st.button("🔥 開始計算總獎金"):
    result = calculate_bonus(deal_dict, classes, loyalty, upgrades, monthly)
    
    st.balloons() # 撒花效果
    st.success(f"計算完成！")
    
    # 使用容器美化顯示
    with st.container():
        st.markdown(f"### 💵 本月總獎金預估： **{result}** 元")
        st.info(f"明細摘要：體驗成交共 {sum(deal_dict.values())} 筆 / 升級共 {sum(upgrades.values())} 次")
