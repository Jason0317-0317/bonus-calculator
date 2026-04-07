def calculate_bonus(days_to_deal, extra_classes, loyalty_sessions, upgrade_type, monthly_deals):
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

    # 4. 結構升級獎
    upgrade_map = {"1對2變1對3": 100, "團課變期班": 150, "包班成立": 300}
    total += upgrade_map.get(upgrade_type, 0)

    # 5. 月轉換獎高手
    if monthly_deals >= 50:
        total += 5000
    elif monthly_deals > 30:
        total += 2000

    return total


# --- 互動輸入部分 ---
print("=== 業務獎金計算系統 ===")

try:
    # 使用 int() 確保輸入的是數字
    days = int(input("請輸入成交天數 (當天成交請打 0): "))
    classes = int(input("請輸入補位次數: "))
    loyalty = int(input("請輸入購買堂數: "))

    print("\n[升級類型選項: 1對2變1對3, 團課變期班, 包班成立, 無]")
    upgrade = input("請輸入升級類型: ")

    monthly = int(input("請輸入本月總轉換筆數: "))

    # 呼叫函式計算
    result = calculate_bonus(days, classes, loyalty, upgrade, monthly)

    print("\n" + "=" * 20)
    print(f"計算完成！本月預計總獎金為: {result} 元")
    print("=" * 20)

except ValueError:
    print("\n[錯誤] 請在數字欄位輸入整數數字，不要輸入文字喔！")