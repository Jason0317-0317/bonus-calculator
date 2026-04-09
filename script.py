import streamlit as st

# ========================
# 🧮 計算函式
# ========================
def calculate_bonus(deal_counts, extra_classes, loyalty_counts, upgrade_counts):
    total = 0

    # 1. 體驗成交獎金
    d_total = (deal_counts.get("當天", 0) * 80 + 
               deal_counts.get("1-2天", 0) * 60 + 
               deal_counts.get("3-7天", 0) * 50)
    total += d_total

    # 2. 補位獎金
    total += extra_classes * 30

    # 3. 回流獎勵獎金 (STP-T)
    l_total = (loyalty_counts.get("10堂", 0) * 100 + 
               loyalty_counts.get("20堂", 0) * 200 + 
               loyalty_counts.get("30堂", 0) * 300 + 
               loyalty_counts.get("40堂", 0) * 500)
    total += l_total

    # 4. 結構升級獎金
    upgrade_prices = {"1對2變1對3": 100, "團課變期班": 150, "包班成立": 300}
    u_total = sum(upgrade_prices.get(name, 0) * count for name, count in upgrade_counts.items())
    total += u_total

    # 5. 月轉換獎高手 (修正邏輯：體驗 + 升級 + 回流 + 補位 = 總轉換筆數)
    # 將 extra_classes (補位次數) 也加入加總
    total_deals = (sum(deal_counts.values()) + 
                   sum(upgrade_counts.values()) + 
                   sum(loyalty_counts.values()) + 
                   extra_classes)
    
    monthly_bonus = 0
    if total_deals >= 50:
        monthly_bonus = 5000
    elif total_deals > 30:
        monthly_bonus = 2000
    
    total += monthly_bonus

    return total, total_deals, monthly_bonus, l_total


# ========================
# 🎯 Streamlit UI
# ========================

st.title("💰 業務獎金計算系統")

# --- 第一區：體驗成交 ---
st.header("✨ 1. 體驗成交/筆")
col1, col2, col3 = st.columns(3)
with col1:
    d0 = st.number_input("當天成交(筆)", min_value=0, step=1)
with col2:
    d12 = st.number_input("48小時(筆)", min_value=0, step=1)
with col3:
    d37 = st.number_input("7天內(筆)", min_value=0, step=1)

deal_dict = {"當天": d0, "1-2天": d12, "3-7天": d37}

# --- 第二區：補位與回流 ---
st.header("📊 2. 補位獎金 & 回流")
# 補位獎金現在也會影響總轉換筆數
classes = st.number_input("補開課次數 (計入總轉換)", min_value=0, step=1)

st.subheader("💎 加發回流購課獎金(STP-T)")
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
st.header("📈 3. 結構升級獎/當月轉換")
u1 = st.number_input("1對2變1>>>3+多 次數", min_value=0, step=1)
u2 = st.number_input("團課>>>期班 次數", min_value=0, step=1)
u3 = st.number_input("包班成立 次數", min_value=0, step=1)

upgrades = {"1對2變1對3": u1, "團課變期班": u2, "包班成立": u3}

# --- 計算按鈕 ---
st.divider()
if st.button("🔥 開始計算總獎金"):
    # 執行計算
    result, total_deals, m_bonus, l_subtotal = calculate_bonus(deal_dict, classes, loyalty_dict, upgrades)
    
    st.balloons()
    st.success("計算完成！")
    
    # 數據看板
    m1, m2, m3 = st.columns(3)
    m1.metric("總轉換筆數 (含補位)", f"{total_deals} 筆")
    m2.metric("回流獎金小計", f"${l_subtotal}")
    m3.metric("本月預計總獎金", f"${result}")

    with st.expander("📝 查看詳細拆解"):
        st.write(f"• **體驗成交**：{sum(deal_dict.values())} 筆")
        st.write(f"• **補開課程**：{classes} 筆 (已計入總轉換)")
        st.write(f"• **回流人數**：{sum(loyalty_dict.values())} 筆 (已計入總轉換)")
        st.write(f"• **結構升級**：{sum(upgrades.values())} 筆 (已計入總轉換)")
        st.write("---")
        st.write(f"• **回流獎金小計**：{l_subtotal} 元")
        st.write(f"• **補位獎金小計**：{classes * 30} 元")
        
        if total_deals > 30:
            st.info(f"✅ 總筆數 {total_deals} 達標！額外獲得高手獎金：{m_bonus} 元")
        else:
            st.warning(f"💡 目前總筆數 {total_deals}，還差 {31 - total_deals} 筆即可領取 $2,000 獎金！")
