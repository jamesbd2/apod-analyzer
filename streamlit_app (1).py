
import streamlit as st
import pandas as pd

DEFAULT_RENT = 1300
DEFAULT_VACANCY_RATE = 0.05
DEFAULT_INSURANCE_RATE = 0.004
DEFAULT_MAINTENANCE = 100
DEFAULT_PM_RATE = 0.08
DEFAULT_DOWN_PAYMENT_PCT = 0.2
DEFAULT_INTEREST_RATE = 0.07
DEFAULT_LOAN_TERM_YEARS = 30

st.set_page_config(page_title="APOD Analyzer - Test", layout="wide")
st.title("🧪 Test: Basic APOD Analyzer")

uploaded_file = st.file_uploader("📂 Upload your MLS CSV export", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded!")

    address_col = st.selectbox("Select Address Column", df.columns)
    price_col = st.selectbox("Select List Price Column", df.columns)
    tax_col = st.selectbox("Select Property Tax Column", [col for col in df.columns if 'tax' in col.lower()])

    properties = []
    for idx, row in df.iterrows():
        with st.container():
            st.markdown(f"---\n#### 🏠 Property #{idx+1}: {row[address_col]}")

            rent = st.slider(f"💵 Monthly Rent (per unit)", 500, 5000, DEFAULT_RENT, 50, key=f"rent_{idx}")
            units = st.slider(f"🏘️ Units", 1, 20, 2, key=f"units_{idx}")
            vacancy = st.slider(f"📉 Vacancy Rate (%)", 0, 15, int(DEFAULT_VACANCY_RATE * 100), key=f"vacancy_{idx}") / 100
            down_payment_pct = st.slider("💰 Down Payment (%)", 0, 100, int(DEFAULT_DOWN_PAYMENT_PCT * 100), key=f"dp_{idx}") / 100
            interest_rate = st.slider("📈 Interest Rate (%)", 0.0, 15.0, DEFAULT_INTEREST_RATE * 100, 0.1, key=f"int_{idx}") / 100

            list_price = float(row[price_col])
            taxes = float(row[tax_col]) if pd.notnull(row[tax_col]) else 0
            insurance = list_price * DEFAULT_INSURANCE_RATE
            maintenance = DEFAULT_MAINTENANCE * units * 12

            gross_income = rent * units * 12
            effective_income = gross_income * (1 - vacancy)
            pm_cost = effective_income * DEFAULT_PM_RATE
            operating_expenses = taxes + insurance + maintenance + pm_cost
            noi = effective_income - operating_expenses
            cap_rate = (noi / list_price) * 100

            loan_amt = list_price * (1 - down_payment_pct)
            r = interest_rate / 12
            n = DEFAULT_LOAN_TERM_YEARS * 12
            pmt = loan_amt * (r * (1 + r)**n) / ((1 + r)**n - 1)
            annual_debt_service = pmt * 12
            cash_flow = noi - annual_debt_service
            cash_on_cash = (cash_flow / (list_price * down_payment_pct)) * 100

            col1, col2, col3 = st.columns(3)
            col1.metric("💸 NOI", f"${noi:,.0f}")
            col2.metric("📈 Cap Rate", f"{cap_rate:.2f}%")
            col3.metric("💰 Cash Flow", f"${cash_flow:,.0f}")

            properties.append({
                "Address": row[address_col],
                "Price": list_price,
                "Rent": rent,
                "NOI": round(noi, 2),
                "CapRate": round(cap_rate, 2),
                "CashFlow": round(cash_flow, 2),
                "CoCReturn": round(cash_on_cash, 2)
            })

    st.markdown("### 📊 Portfolio Summary")
    st.dataframe(pd.DataFrame(properties))
