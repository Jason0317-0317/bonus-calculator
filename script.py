def calculate_bonus(days_to_deal, extra_classes, loyalty_sessions, upgrade_counts, monthly_deals):
    total = 0

    # 1. 體驗成交
    if days_to_deal == 0:
        total += 80
    elif days_to_deal <= 2:
        total += 60
    elif days_to_deal <= 7:
        total += 50

    # 2. 補位獎金 (每開一課 30)
    total += extra_classes * 30

    # 3. 加發回流購物金
    if loyalty_sessions >= 40:
        total += 500
    elif loyalty_sessions >= 30:
        total += 300
    elif loyalty_sessions >= 20:
        total += 200
    elif loyalty_sessions >= 10:
        total += 100

    # 4. 結構升級獎 (優化後：支援複選與多次數)
    upgrade_prices = {"1對2變1對3": 100, "團課變期班": 150, "包班成立": 300}

    # 遍歷所有的升級類型與對應輸入的次數
    for name, count in upgrade_counts.items():
        total += upgrade_prices.get(name, 0) * count

    # 5. 月轉換獎高手
    if monthly_deals >= 50:
        total += 5000
    elif monthly_deals > 30:
        total += 2000

    return total


# --- 互動輸入部分 ---
print("=== 業務獎金計算系統 (進階累計版) ===")

try:
    days = int(input("請輸入成交天數 (當天成交請打 0): "))
    classes = int(input("請輸入補位次數: "))
    loyalty = int(input("請輸入購買堂數: "))

    # 處理複選升級獎
    print("\n--- 結構升級獎 (請輸入次數，若無則填 0) ---")
    u1 = int(input("1對2變1對3 的次數: "))
    u2 = int(input("團課變期班 的次數: "))
    u3 = int(input("包班成立 的次數: "))

    # 將次數包裝成字典傳入
    upgrades = {
        "1對2變1對3": u1,
        "團課變期班": u2,
        "包班成立": u3
    }

    monthly = int(input("\n請輸入本月總轉換筆數: "))

    # 呼叫函式
    result = calculate_bonus(days, classes, loyalty, upgrades, monthly)

    print("\n" + "=" * 30)
    print(f"計算完成！")
    print(f"結構升級部分共達成: {u1}次升級/ {u2}次轉期/ {u3}次包班")
    print(f"本月預計總獎金為: {result} 元")
    print("=" * 30)

except ValueError:
    print("\n[錯誤] 請務必輸入整數數字喔！")
