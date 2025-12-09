# tools/make_financial_dataset.py

import json
from pathlib import Path

problems = [
    {
        "id": "fin_001",
        "problem": (
            "A stock trades at 20 dollars. It increases by 15 percent in one day. "
            "What is the new stock price?"
        ),
        # 20 * 1.15 = 23
        "answer": "23",
    },
    {
        "id": "fin_002",
        "problem": (
            "A stock trades at 50 dollars. It drops by 12 percent after earnings. "
            "What is the new stock price?"
        ),
        # 50 * 0.88 = 44
        "answer": "44",
    },
    {
        "id": "fin_003",
        "problem": (
            "A stock is 100 dollars. In month one it rises 10 percent. "
            "In month two it falls 5 percent. "
            "What is the total percentage return over the two months, "
            "rounded to two decimals?"
        ),
        # 100 * 1.10 * 0.95 = 104.5 -> 4.50%
        "answer": "4.50",
    },
    {
        "id": "fin_004",
        "problem": (
            "An investor deposits 3,000 dollars in a savings account that pays "
            "4 percent simple annual interest. "
            "What is the value of the account after 3 years?"
        ),
        # 3000 * (1 + 0.04 * 3) = 3360
        "answer": "3360",
    },
    {
        "id": "fin_005",
        "problem": (
            "An investor deposits 5,000 dollars into an account that pays "
            "6 percent interest compounded once per year. "
            "What is the account value after 2 years?"
        ),
        # 5000 * 1.06^2 = 5618
        "answer": "5618",
    },
    {
        "id": "fin_006",
        "problem": (
            "A portfolio invests 60 percent in Asset A with an 8 percent return "
            "and 40 percent in Asset B with a 3 percent return. "
            "What is the portfolio's overall return in percent, "
            "rounded to two decimals?"
        ),
        # 0.6*8 + 0.4*3 = 6.00%
        "answer": "6.00",
    },
    {
        "id": "fin_007",
        "problem": (
            "An account starts at 10,000 dollars. It loses 20 percent in the first year "
            "and gains 25 percent in the second year. "
            "What is the total percentage return over the two years, "
            "rounded to two decimals?"
        ),
        # 10000 * 0.8 * 1.25 = 10000 -> 0.00%
        "answer": "0.00",
    },
    {
        "id": "fin_008",
        "problem": (
            "A trader has 50,000 dollars of capital and is willing to risk 2 percent "
            "of the account on a trade. The planned entry price is 40 dollars and the "
            "stop loss is at 36 dollars. "
            "What is the maximum whole number of shares the trader can buy and stay "
            "within the risk limit?"
        ),
        # Risk capital = 1000, per share risk = 4, shares = 250
        "answer": "250",
    },
    {
        "id": "fin_009",
        "problem": (
            "A portfolio suffers a 30 percent loss from its peak value. "
            "What percentage gain, rounded to two decimals, is required on the reduced "
            "capital to recover back to the original peak?"
        ),
        # Required gain = 1/0.70 - 1 ≈ 42.86%
        "answer": "42.86",
    },
    {
        "id": "fin_010",
        "problem": (
            "An investor buys a bond for 980 dollars and receives 1,000 dollars at maturity, "
            "ignoring coupons. What is the percentage price return, in percent, "
            "rounded to two decimals?"
        ),
        # (1000/980 - 1) * 100 ≈ 2.04%
        "answer": "2.04",
    },
    {
        "id": "fin_011",
        "problem": (
            "A portfolio has an expected annual return of 9 percent and the risk free rate "
            "is 3 percent. The annual volatility of the portfolio is 12 percent. "
            "What is the Sharpe ratio, rounded to two decimals?"
        ),
        # (0.09 - 0.03) / 0.12 = 0.50
        "answer": "0.50",
    },
    {
        "id": "fin_012",
        "problem": (
            "A trading book has a market value of 2 million dollars and a daily volatility "
            "estimate of 1.5 percent. Using a 95 percent confidence level with a z score "
            "of 1.65, what is the one day Value at Risk (VaR) in dollars?"
        ),
        # VaR = 1.65 * 0.015 * 2,000,000 = 49,500
        "answer": "49500",
    },
    {
        "id": "fin_013",
        "problem": (
            "A portfolio worth 8 million dollars has a beta of 1.1 to the market index. "
            "Index futures have a notional value of 200,000 dollars each. "
            "How many index futures contracts should be shorted to hedge the beta exposure?"
        ),
        # 1.1 * 8,000,000 / 200,000 = 44
        "answer": "44",
    },
    {
        "id": "fin_014",
        "problem": (
            "An equity fund has 3 million dollars of investor capital. "
            "It borrows 2 million dollars at a fixed rate of 4 percent and invests the "
            "full 5 million in a portfolio that earns 7 percent over the year. "
            "What is the net return on equity for investors in percent, "
            "after interest on the borrowing, rounded to two decimals?"
        ),
        # Profit = 5M * 7% = 350k; interest = 2M * 4% = 80k; net = 270k
        # ROE = 270k / 3M = 9.00%
        "answer": "9.00",
    },
    {
        "id": "fin_015",
        "problem": (
            "A fund with 5 million dollars in assets suffers an 18 percent drawdown. "
            "What percentage gain on the reduced capital is required to recover back to "
            "5 million dollars, rounded to two decimals?"
        ),
        # New capital = 5M * 0.82 = 4.1M; required gain = 5/4.1 - 1 ≈ 21.95%
        "answer": "21.95",
    },
    {
        "id": "fin_016",
        "problem": (
            "A trader buys 20 call option contracts on a stock. Each contract controls "
            "100 shares. The strike price is 50 dollars and the option premium is "
            "2 dollars per share. At expiration the stock price is 58 dollars. "
            "What is the total profit in dollars from the option position?"
        ),
        # Payoff per share = 8, profit per share = 8 - 2 = 6
        # Total = 20 * 100 * 6 = 12,000
        "answer": "12000",
    },
    {
        "id": "fin_017",
        "problem": (
            "A trader shorts 300 shares of a stock at 40 dollars. Later, the short is "
            "covered at 32 dollars. Ignoring fees and dividends, what is the profit "
            "in dollars on the short sale?"
        ),
        # Profit = (40 - 32) * 300 = 2400
        "answer": "2400",
    },
    {
        "id": "fin_018",
        "problem": (
            "A trader has 100,000 dollars in a margin account. The initial margin "
            "requirement for a futures position is 25 percent of notional exposure. "
            "What is the maximum notional exposure in dollars the trader can take?"
        ),
        # Max notional = 100,000 / 0.25 = 400,000
        "answer": "400000",
    },
    {
        "id": "fin_019",
        "problem": (
            "A volatility targeting fund has 4 million dollars in capital. "
            "The market index has an annual volatility of 20 percent, and the fund "
            "targets a volatility of 10 percent. "
            "What is the target notional exposure to the index in dollars?"
        ),
        # Exposure = capital * (target vol / index vol) = 4M * 10/20 = 2M
        "answer": "2000000",
    },
    {
        "id": "fin_020",
        "problem": (
            "A long short equity fund has 30 million dollars in equity capital. "
            "It runs with 150 percent gross exposure and 30 percent net long exposure. "
            "What is the dollar value of the short book in dollars?"
        ),
        # L + S = 1.5 * 30 = 45; L - S = 0.3 * 30 = 9 -> L = 27, S = 18
        "answer": "18000000",
    },
    {
        "id": "fin_021",
        "problem": (
            "A hedge fund starts the year with 15 million dollars in assets. "
            "By year end, before any fees, the assets have grown to 18.6 million dollars. "
            "The fund charges a 2 percent management fee on beginning assets and a "
            "20 percent performance fee on profits after the management fee. "
            "What is the investors' net return in percent, rounded to two decimals?"
        ),
        # Mgmt fee = 0.02 * 15 = 0.3; profit after mgmt vs start = 18.6 - 15 - 0.3 = 3.3
        # Perf fee = 0.2 * 3.3 = 0.66; final AUM = 18.6 - 0.3 - 0.66 = 17.64
        # Net return = 17.64 / 15 - 1 = 17.60%
        "answer": "17.60",
    },
    {
        "id": "fin_022",
        "problem": (
            "A fund records annual returns of +12 percent, -5 percent, and +9 percent "
            "in three consecutive years. "
            "What is the cumulative return over the three years in percent, "
            "rounded to two decimals?"
        ),
        # (1.12 * 0.95 * 1.09 - 1) * 100 ≈ 15.98%
        "answer": "15.98",
    },
    {
        "id": "fin_023",
        "problem": (
            "A 100,000 dollar portfolio is invested 60 percent in stocks and "
            "40 percent in bonds. During the year, stocks gain 10 percent and bonds "
            "have a 0 percent return. "
            "After these moves, what is the new weight of stocks in the portfolio, "
            "in percent, rounded to two decimals?"
        ),
        # Stocks: 60,000 -> 66,000; bonds: 40,000 -> 40,000; total: 106,000
        # Weight in stocks = 66,000 / 106,000 ≈ 62.26%
        "answer": "62.26",
    },
    {
        "id": "fin_024",
        "problem": (
            "A bond has a face value of 1,000 dollars, a 5 percent annual coupon, "
            "and matures in 3 years. If the yield to maturity is 4 percent, "
            "what is the price of the bond, rounded to two decimals?"
        ),
        # Price = 50/(1.04) + 50/(1.04^2) + 1050/(1.04^3) ≈ 1027.75
        "answer": "1027.75",
    },
    {
        "id": "fin_025",
        "problem": (
            "A company borrows 1 million dollars at a fixed simple annual interest rate "
            "of 5 percent. The loan is interest-only for 3 years, with the principal "
            "repaid at the end of year 3. "
            "How much total interest in dollars is paid over the 3 years?"
        ),
        # Interest = 1,000,000 * 0.05 * 3 = 150,000
        "answer": "150000",
    },
    {
        "id": "fin_026",
        "problem": (
            "A fund charges a 2 percent management fee on assets each year. "
            "An investor wants to earn a net return of 6 percent after the fee. "
            "Assuming fees are charged on beginning assets and there are no "
            "performance fees, what gross return in percent is required before fees, "
            "rounded to two decimals?"
        ),
        # (1 + gross) * 0.98 = 1.06 -> gross = 1.06/0.98 - 1 ≈ 8.16%
        "answer": "8.16",
    },
    {
        "id": "fin_027",
        "problem": (
            "A U.S. investor buys a euro-denominated bond. Over the year the bond "
            "returns 5 percent in euros, and the euro appreciates by 3 percent against "
            "the dollar. Ignoring compounding across time, what is the approximate "
            "total return in percent in dollars, rounded to two decimals?"
        ),
        # (1.05 * 1.03 - 1) * 100 ≈ 8.15%
        "answer": "8.15",
    },
    {
        "id": "fin_028",
        "problem": (
            "An investor buys a stock for 30 dollars. Over the year, the stock pays "
            "a dividend of 1.20 dollars per share and is later sold for 33 dollars. "
            "What is the total holding period return in percent, rounded to two decimals?"
        ),
        # Total profit = 1.2 + 3 = 4.2; return = 4.2 / 30 * 100 = 14.00%
        "answer": "14.00",
    },
    {
        "id": "fin_029",
        "problem": (
            "A savings account pays 0.6 percent interest per month, compounded monthly. "
            "What is the effective annual interest rate in percent, rounded to two decimals?"
        ),
        # (1 + 0.006)^12 - 1 ≈ 7.44%
        "answer": "7.44",
    },
    {
        "id": "fin_030",
        "problem": (
            "A portfolio invests 70 percent in a stock index with a beta of 1.2 and "
            "30 percent in a bond fund with a beta of 0.2 (both relative to the same market). "
            "What is the portfolio's beta, rounded to two decimals?"
        ),
        # 0.7*1.2 + 0.3*0.2 = 0.90
        "answer": "0.90",
    },
    {
        "id": "fin_031",
        "problem": (
            "A trading book has a value of 7 million dollars and an estimated daily "
            "volatility of 2.1 percent. Using a 99 percent confidence level with "
            "a z score of 2.33, and assuming square root of time scaling, "
            "what is the 10 day Value at Risk (VaR) in dollars, rounded to the "
            "nearest whole dollar?"
        ),
        # One day VaR = 2.33 * 0.021 * 7,000,000 = 342,510
        # Ten day VaR ≈ 342,510 * sqrt(10) ≈ 1,083,112
        "answer": "1083112",
    },
    {
        "id": "fin_032",
        "problem": (
            "A firm is expected to generate free cash flows of 250,000, 280,000, and "
            "310,000 dollars over the next 3 years. After year 3, free cash flow is "
            "expected to grow at 2 percent per year forever. The discount rate is "
            "9 percent. Using a discounted cash flow model with a growing perpetuity "
            "starting in year 4, what is the estimated enterprise value in dollars, "
            "rounded to the nearest whole dollar?"
        ),
        # EV ≈ 4,192,468
        "answer": "4192468",
    },
    {
        "id": "fin_033",
        "problem": (
            "A portfolio holds three positions:\n"
            "- Long 200 shares of Stock A, bought at 50 dollars, now worth 56 dollars.\n"
            "- Short 100 shares of Stock B, shorted at 80 dollars, now worth 74 dollars.\n"
            "- Long 10 call option contracts on Stock C (each for 100 shares) with a "
            "strike of 40 dollars and premium of 3 dollars, with the stock now at "
            "46 dollars at expiration.\n"
            "Ignoring fees and dividends, what is the total profit in dollars "
            "across all three positions?"
        ),
        # Long A: 200 * (56 - 50) = 1200
        # Short B: 100 * (80 - 74) = 600
        # Calls: payoff per share = 6, profit per share = 6 - 3 = 3
        # 10 * 100 * 3 = 3000; total = 4800
        "answer": "4800",
    },
    {
        "id": "fin_034",
        "problem": (
            "An investor allocates 100,000 dollars across three funds:\n"
            "- 40,000 dollars in Fund A, which returns 12 percent.\n"
            "- 35,000 dollars in Fund B, which returns 4 percent.\n"
            "- 25,000 dollars in Fund C, which returns -3 percent.\n"
            "What is the overall portfolio return in percent, rounded to two decimals?"
        ),
        # Portfolio profit = 40k*0.12 + 35k*0.04 - 25k*0.03 = 5,450
        # Return = 5450 / 100,000 = 5.45%
        "answer": "5.45",
    },
    {
        "id": "fin_035",
        "problem": (
            "A bank quotes a nominal annual interest rate of 9 percent compounded "
            "quarterly. What is the effective annual rate in percent, "
            "rounded to two decimals?"
        ),
        # (1 + 0.09/4)^4 - 1 ≈ 9.31%
        "answer": "9.31",
    },
    {
        "id": "fin_036",
        "problem": (
            "An investor buys 400 shares of a stock at 50 dollars using 50 percent "
            "initial margin. The investor borrows the remaining amount from the broker. "
            "The maintenance margin requirement is 25 percent. "
            "At approximately what stock price will the investor receive a margin call, "
            "rounded to two decimals?"
        ),
        # Total value at purchase = 400 * 50 = 20,000; loan = 10,000; equity = 10,000
        # Margin call when (V - 10,000)/V = 0.25 -> 0.75V = 10,000 -> V = 13,333.33
        # Price = 13,333.33 / 400 ≈ 33.33
        "answer": "33.33",
    },
    {
        "id": "fin_037",
        "problem": (
            "An investor owns 100 shares of a stock purchased at 45 dollars and sells "
            "a covered call with a strike price of 50 dollars for a premium of "
            "2 dollars per share. At expiration, the stock price is 54 dollars and the "
            "shares are called away. "
            "What is the total profit in dollars on the combined stock and option "
            "position?"
        ),
        # Proceeds from stock sale = 100 * 50 = 5000; premium received = 200
        # Initial cost = 100 * 45 = 4500; profit = 5200 - 4500 = 700
        "answer": "700",
    },
    {
        "id": "fin_038",
        "problem": (
            "An investor owns 1,000 shares of a stock purchased at 30 dollars and buys "
            "protective put options with a strike of 28 dollars for a premium of "
            "1 dollar per share (1,000 shares covered). At expiration the stock price "
            "is 24 dollars. "
            "What is the investor's net loss in dollars on the combined stock and "
            "put position?"
        ),
        # Initial cost = 30,000 + 1,000 = 31,000
        # Final stock value = 24,000; put payoff = (28 - 24) * 1000 = 4000
        # Net final = 24,000 + 4,000 = 28,000; loss = 31,000 - 28,000 = 3,000
        "answer": "3000",
    },
    {
        "id": "fin_039",
        "problem": (
            "A portfolio is invested 60 percent in Asset A and 40 percent in Asset B. "
            "Asset A has an annual volatility of 15 percent, Asset B has an annual "
            "volatility of 10 percent, and the correlation between the two assets "
            "is 0.3. "
            "What is the portfolio's volatility in percent, rounded to two decimals?"
        ),
        # Variance = 0.6^2*0.15^2 + 0.4^2*0.10^2 + 2*0.6*0.4*0.15*0.10*0.3 ≈ 0.01186
        # Vol ≈ sqrt(0.01186) ≈ 10.89%
        "answer": "10.89",
    },
    {
        "id": "fin_040",
        "problem": (
            "Using the CAPM, the risk free rate is 2 percent, the expected market "
            "return is 8 percent, and a stock has a beta of 1.3. "
            "What is the expected return of the stock in percent, rounded to two decimals?"
        ),
        # 2 + 1.3 * (8 - 2) = 9.8%
        "answer": "9.80",
    },
    {
        "id": "fin_041",
        "problem": (
            "A project requires an initial investment of 1,000,000 dollars today and "
            "is expected to generate cash flows of 300,000, 350,000, 400,000, and "
            "450,000 dollars at the end of years 1 through 4. The discount rate is "
            "10 percent per year. "
            "What is the net present value (NPV) of the project in dollars, "
            "rounded to the nearest whole dollar?"
        ),
        # NPV ≈ 169,865
        "answer": "169865",
    },
    {
        "id": "fin_042",
        "problem": (
            "A leveraged fund has 4 million dollars in equity capital and borrows "
            "6 million dollars at an annual interest rate of 3 percent. The fund "
            "invests the full 10 million dollars in a portfolio that returns "
            "7 percent over the year. The manager also charges a 1.5 percent "
            "management fee on total assets (10 million dollars). "
            "What is the investors' net return on equity in percent, "
            "rounded to two decimals?"
        ),
        # Portfolio profit = 10M * 7% = 700k
        # Interest = 6M * 3% = 180k; mgmt fee = 10M * 1.5% = 150k
        # Net profit = 700k - 180k - 150k = 370k; ROE = 370k / 4M = 9.25%
        "answer": "9.25",
    },
    {
        "id": "fin_043",
        "problem": (
            "An investor contributes 500 dollars at the end of each month into an "
            "account that earns 0.5 percent per month. Contributions are made for "
            "12 months. "
            "What is the account value after the 12th contribution, in dollars, "
            "rounded to two decimals?"
        ),
        # FV = 500 * ((1 + 0.005)^12 - 1) / 0.005 ≈ 6,167.78
        "answer": "6167.78",
    },
    {
        "id": "fin_044",
        "problem": (
            "An investor starts with 100,000 dollars in a balanced fund. "
            "In the first year the fund returns 8 percent. At the end of year 1, "
            "the investor withdraws 10,000 dollars. In the second year, the fund "
            "returns 5 percent on the remaining balance. "
            "What is the account value at the end of year 2, in dollars?"
        ),
        # End of year 1: 100,000 * 1.08 = 108,000; after withdrawal: 98,000
        # End of year 2: 98,000 * 1.05 = 102,900
        "answer": "102900",
    },
    {
        "id": "fin_045",
        "problem": (
            "An investor wants to accumulate 50,000 dollars in 5 years in an account "
            "that earns 4 percent interest per year, compounded annually. "
            "The investor plans to make equal contributions at the end of each year. "
            "What is the required annual contribution in dollars, rounded to two decimals?"
        ),
        # Payment = FV * r / ((1 + r)^n - 1)
        # ≈ 50,000 * 0.04 / ((1.04^5 - 1)) ≈ 9,231.36
        "answer": "9231.36",
    },
    {
        "id": "fin_046",
        "problem": (
            "A simple betting game offers even odds (you win 1 dollar for each dollar "
            "bet). The probability of winning is estimated at 55 percent and the "
            "probability of losing is 45 percent. Using the Kelly criterion, "
            "what percentage of capital should be bet each round, rounded to two decimals?"
        ),
        # Kelly fraction f* = (b*p - q) / b, with b = 1 -> (1*0.55 - 0.45)/1 = 0.10 = 10%
        "answer": "10.00",
    },
    {
        "id": "fin_047",
        "problem": (
            "A stock has three possible return outcomes over the next year:\n"
            "- 40 percent chance of +10 percent\n"
            "- 40 percent chance of +5 percent\n"
            "- 20 percent chance of -8 percent\n"
            "What is the expected return in percent, rounded to two decimals?"
        ),
        # E[R] = 0.4*10 + 0.4*5 - 0.2*8 = 4.4%
        "answer": "4.40",
    },
    {
        "id": "fin_048",
        "problem": (
            "A bank holds a 2 million dollar loan. The probability of default (PD) "
            "is estimated at 2 percent and the loss given default (LGD) is 40 percent. "
            "What is the expected credit loss in dollars?"
        ),
        # ECL = 2,000,000 * 0.02 * 0.40 = 16,000
        "answer": "16000",
    },
    {
        "id": "fin_049",
        "problem": (
            "A bond has a face value of 1,000 dollars and a 6 percent annual coupon "
            "paid semiannually. It matures in 5 years. The yield to maturity is "
            "5 percent per year, compounded semiannually. "
            "What is the price of the bond in dollars, rounded to two decimals?"
        ),
        # Semiannual coupon = 30; semiannual yield = 2.5%; periods = 10
        # Price ≈ 1,043.76
        "answer": "1043.76",
    },
    {
        "id": "fin_050",
        "problem": (
            "A fund records yearly returns of +12 percent, -6 percent, and +9 percent "
            "in three consecutive years. "
            "What is the geometric average annual return in percent over the "
            "three year period, rounded to two decimals?"
        ),
        # Geo = (1.12 * 0.94 * 1.09)^(1/3) - 1 ≈ 4.69%
        "answer": "4.69",
    },
]

out_path = Path("data/financial_quant.jsonl")
out_path.parent.mkdir(parents=True, exist_ok=True)

with out_path.open("w", encoding="utf-8") as f:
    for p in problems:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"Wrote {len(problems)} financial problems to {out_path}")
