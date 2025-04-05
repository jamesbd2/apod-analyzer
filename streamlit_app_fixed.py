import streamlit as st
import pandas as pd
import numpy as np

# ---------- Default Configs ----------
DEFAULT_RENT = 1300  # per unit
DEFAULT_VACANCY_RATE = 0.05
DEFAULT_INSURANCE_RATE = 0.004  # 0.4%
DEFAULT_MAINTENANCE = 100  # per unit per month
DEFAULT_PM_RATE = 0.08  # Property management 8%
DEFAULT_DOWN_PAYMENT_PCT = 0.2
DEFAULT_INTEREST_RATE = 0.07
DEFAULT_LOAN_TERM_YEARS = 30

st.title("📊 APOD Analyzer for MLS Exports")

uploaded_file = st.file_uploader("Upload your MLS CSV export", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")

    # Try to auto-locate essential fields
    st.subheader("🔍 Field Mapping & Overrides")
    address_col = st.selectbox("Select Address Column", df.columns)
    price_col = st.selectbox("Select List Price Column", df.columns)
    tax_col = st.selectbox("Select Property Tax Column", [col for col in df.columns if 'tax' in col.lower()])

    # Create editable table to set assumptions per property
    properties = []
    for idx, row in df.iterrows():
        st.markdown(f"### Property #{idx+1}: {row[address_col]}")
        list_price = row[price_col]
        taxes = float(row[tax_col]) if pd.notnull(row[tax_col]) else 0

        rent = st.number_input(f"Monthly Rent (per unit) - {row[address_col]}", value=DEFAULT_RENT, key=f"rent_{idx}")
        units = st.number_input(f"Units", value=2, min_value=1, max_value=20, key=f"units_{idx}")
        vacancy = st.number_input("Vacancy Rate (%)", value=DEFAULT_VACANCY_RATE*100.0, step=0.1, key=f"vacancy_{idx}") / 100
        insurance = list_price * DEFAULT_INSURANCE_RATE
        maintenance = DEFAULT_MAINTENANCE * units * 12

        gross_income = rent * units * 12
        effective_income = gross_income * (1 - vacancy)
        pm_cost = effective_income * DEFAULT_PM_RATE

        operating_expenses = taxes + insurance + maintenance + pm_cost
        noi = effective_income - operating_expenses
        cap_rate = (noi / list_price) * 100

        loan_amt = list_price * (1 - DEFAULT_DOWN_PAYMENT_PCT)
        r = DEFAULT_INTEREST_RATE / 12
        n = DEFAULT_LOAN_TERM_YEARS * 12
        pmt = loan_amt * (r * (1 + r)**n) / ((1 + r)**n - 1)
        annual_debt_service = pmt * 12

        cash_flow = noi - annual_debt_service
        cash_on_cash = (cash_flow / (list_price * DEFAULT_DOWN_PAYMENT_PCT)) * 100

        properties.append({
            "Address": row[address_col],
            "Price": list_price,
            "Rent": rent,
            "NOI": round(noi, 2),
            "Cap Rate %": round(cap_rate, 2),
            "Cash Flow": round(cash_flow, 2),
            "CoC Return %": round(cash_on_cash, 2)
        })

    results_df = pd.DataFrame(properties)
    st.subheader("📈 APOD Summary")
    st.dataframe(results_df)

    csv_download = results_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results as CSV", data=csv_download, file_name="apod_results.csv", mime="text/csv")
