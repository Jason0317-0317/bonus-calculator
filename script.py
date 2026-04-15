import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# ========================
# 計算函式
# ========================
def calculate_bonus(deal_counts, extra_classes, loyalty_counts, upgrade_counts):
    # 1. 體驗成交獎金計算
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

    # 5. 月轉換高手筆數累計
    total_deals = (sum(deal_counts.values()) + 
                   sum(upgrade_counts.values()) + 
                   sum(loyalty_counts.values()) + 
                   extra_classes)
    
    monthly_bonus = 0
    if total_deals >= 50:
        monthly_bonus = 5000
    elif total_deals >= 30:
        monthly_bonus = 2000
    
    final_total = d_total + c_total + l_total + u_total + monthly_bonus

    return final_total, total_deals, monthly_bonus, l_total, d_total, u_total

# ========================
# 寄信函式
# ========================
def send_email(receiver_email, content):
    # 這邊設定您的 Gmail 帳號資訊
    # 注意：需使用 Google 的 "應用程式密碼"
    sender_user = "您的Gmail帳號@gmail.com" 
    sender_password = "您的應用程式密碼" 
    
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = sender_user
    msg['To'] = receiver_email
    msg['Subject'] = Header("業務獎金結算報表", 'utf-8')

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_user, sender_password)
        server.sendmail(sender_user, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"寄送失敗：{e}")
        return False

# ========================
# Streamlit UI
# ========================

st.title("業務獎金計算系統")

# --- 第一區：體驗成交 ---
st.header("1. 體驗成交/筆")
col1, col2, col3 = st.columns(3)
with col1:
    d0 = st.number_input("當天成交(筆)", min_value=0, step=1)
with col2:
    d12 = st.number_input("48小時(筆)", min_value=0, step=1)
with col3:
    d37 = st.number_input("7天內(筆)", min_value=0, step=1)

deal_dict = {"當天": d0, "48小時": d12, "7天內": d37}

# --- 第二區：補位與回流 ---
st.header("2. 補位獎金")
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
u1 = st.number_input("1對2 > 1對3+多 / 次數", min_value=0, step=1)
u2 = st.number_input("團課 > 期班 / 次數", min_value=0, step=1)
u3 = st.number_input("包班成立 / 次數", min_value=0, step=1)

upgrades = {"1對2變1對3": u1, "團課變期班": u2, "包班成立": u3}

# 暫存計算結果供寄信使用
if 'report_text' not in st.session_state:
    st.session_state.report_text = ""

# --- 計算按鈕 ---
st.divider()
if st.button("開始計算總獎金", type="primary"):
    # 執行氣球動畫
    st.balloons()
    
    # 執行計算
    result, total_v, m_bonus, l_bonus, d_bonus, u_bonus = calculate_bonus(deal_dict, classes, loyalty_dict, upgrades)
    
    st.success("計算完成")
    
    # 數據看板
    m1, m2 = st.columns(2)
    m1.metric("總轉換筆數", f"{total_v} 筆")
    m2.metric("本月預計總獎金", f"NT$ {result}")

    # 詳細報表內容 (準備給 Email 使用)
    st.session_state.report_text = f"""
業務獎金結算報表
----------------------
總轉換筆數：{total_v} 筆
本月總獎金：NT$ {result}

項目統計：
- 體驗成交：{sum(deal_dict.values())} 筆
- 補開課程：{classes} 筆
- 回流人數：{sum(loyalty_dict.values())} 人
- 結構升級：{sum(upgrades.values())} 次

獎金明細：
- 體驗成交獎金：{d_bonus} 元
- 補位獎金：{classes * 30} 元
- 加發回流獎金：{l_bonus} 元
- 結構升級獎金：{u_bonus} 元
- 月轉換高手獎勵：{m_bonus} 元
    """

    with st.expander("查看詳細報表", expanded=True):
        st.text(st.session_state.report_text)
        
        if total_v >= 30:
            st.info(f"總筆數 {total_v} 達標。已包含高手獎勵 {m_bonus} 元")
        else:
            st.warning(f"目前總筆數 {total_v}，距離領取 2000 元高手獎金還差 {30 - total_v} 筆")

# --- 寄送郵件區塊 ---
if st.session_state.report_text != "":
    st.divider()
    st.header("寄送電子郵件報表")
    target_email = st.text_input("輸入接收者的 Gmail 信箱")
    
    if st.button("發送郵件"):
        if target_email:
            with st.spinner("正在寄送..."):
                success = send_email(target_email, st.session_state.report_text)
                if success:
                    st.success(f"已成功寄送至 {target_email}")
        else:
            st.error("請輸入完整的 Email 地址")
