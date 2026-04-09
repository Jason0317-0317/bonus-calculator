import streamlit as st

# ========================
# 🧮 計算函式
# ========================
def calculate_bonus(deal_counts, extra_classes, loyalty_counts, upgrade_counts):
    total = 0

    # 1. 體驗成交 (按筆數累計)
    d_total = (deal_counts.get("當天", 0) * 80 + 
               deal_counts.get("1-2天", 0) * 60 + 
               deal_counts.get("3-7天", 0) * 50)
    total += d_total

    # 2. 補位獎金
    total += extra_classes * 30

    # 3. 回流獎勵 (按人數筆數累計)
    l_total = (loyalty_counts.get("10堂", 0) * 100 + 
               loyalty_counts.get("20堂", 0) * 200 + 
               loyalty_counts.get("30堂", 0) * 300 + 
               loyalty_counts.get("40堂", 0) * 500)
    total += l_total

    # 4. 結構升級獎 (按次數累計)
    upgrade_prices = {"1對2變1對3": 100, "團課變期班": 150, "包班成立": 300}
    u_total = 0
    for name, count in upgrade_counts.items():
        u_total += upgrade_prices.get(name, 0) * count
    total += u_total

    # 5. 月轉換獎高手 (自動加總筆數)
    # 總轉換筆數 = 體驗成交總筆數 + 結構升級總次數
    total_deals = sum(deal_counts.values()) + sum(upgrade_counts.values())
    
    monthly_bonus = 0
    if total_deals >= 50:
        monthly_bonus = 5000
    elif total_deals > 30:
        monthly_bonus = 2000
    
    total += monthly_bonus

    return total, total_deals, monthly_bonus


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

# --- 計算按鈕 ---
st.divider()
if st.button("🔥 開始計算總獎金"):
    # 呼叫函式，回傳總分、總筆數、以及月轉換獎金額
    result, total_deals, m_bonus = calculate_bonus(deal_dict, classes, loyalty_dict, upgrades)
    
    st.balloons()
    
    # 顯示結果
    st.success("計算完成！")
    
    # 使用 Dashboard 風格顯示
    m1, m2, m3 = st.columns(3)
    m1.metric("總成交/轉換筆數", f"{total_deals} 筆")
    m2.metric("月轉換高手獎金", f"${m_bonus}")
    m3.metric("本月預計總獎金", f"${result}", delta_color="normal")

    with st.expander("詳情明細"):
        st.write(f"📌 體驗成交：{sum(deal_dict.values())} 筆")
        st.write(f"📌 回流人數：{sum(loyalty_dict.values())} 人")
        st.write(f"📌 升級次數：{sum(upgrades.values())} 次")
        if total_deals > 30:
            st.write(f"✅ 已達成月轉換高手門檻！額外獎金：{m_bonus} 元")
        else:
            st.write(f"❌ 未達月高手門檻 (還差 {31 - total_deals} 筆)")
