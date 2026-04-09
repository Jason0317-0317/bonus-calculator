import streamlit as st

# ========================
# 🧮 計算函式
# ========================
def calculate_bonus(deal_counts, extra_classes, loyalty_counts, upgrade_counts, monthly_deals):
    total = 0

    # 1. 體驗成交 (按筆數累計)
    total += deal_counts.get("當天", 0) * 80
    total += deal_counts.get("1-2天", 0) * 60
    total += deal_counts.get("3-7天", 0) * 50

    # 2. 補位獎金
    total += extra_classes * 30

    # 3. 回流獎勵 (改為按「達標人數/筆數」累計)
    # 邏輯：只要該購買方案達標，每筆都給獎
    total += loyalty_counts.get("10堂", 0) * 100
    total += loyalty_counts.get("20堂", 0) * 200
    total += loyalty_counts.get("30堂", 0) * 300
    total += loyalty_counts.get("40堂", 0) * 500

    # 4. 結構升級獎 (按次數累計)
    upgrade_prices = {
        "1對2變1對3": 100,
        "團課變期班": 150,
        "包班成立": 300
    }
    for name, count in upgrade_counts.items():
        total += upgrade_prices.get(name, 0) * count

    # 5. 月轉換獎 (維持全月達成門檻)
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

# --- 第二區：補位與回流 ---
st.header("📊 2. 基礎與回流")
classes = st.number_input("補位次數", min_value=0, step=1)

st.subheader("💎 回流達標人數")
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
    result = calculate_bonus(deal_dict, classes, loyalty_dict, upgrades, monthly)
    
    st.balloons() 
    st.success(f"計算完成！")
    
    with st.container():
        st.markdown(f"### 💵 本月總獎金預估： **{result}** 元")
        
        # 顯示更詳細的加總資訊
        total_deals = sum(deal_dict.values())
        total_loyalty = sum(loyalty_dict.values())
        st.info(f"明細：成交 {total_deals} 筆 / 回流 {total_loyalty} 人 / 升級 {sum(upgrades.values())} 次")
