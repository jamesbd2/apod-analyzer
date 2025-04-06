
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from jinja2 import Template
import pdfkit
from streamlit_folium import folium_static
import folium
from geopy.geocoders import Nominatim

# ---------- Default Configs ----------
DEFAULT_RENT = 1300
DEFAULT_VACANCY_RATE = 0.05
DEFAULT_INSURANCE_RATE = 0.004
DEFAULT_MAINTENANCE = 100
DEFAULT_PM_RATE = 0.08
DEFAULT_DOWN_PAYMENT_PCT = 0.2
DEFAULT_INTEREST_RATE = 0.07
DEFAULT_LOAN_TERM_YEARS = 30

geolocator = Nominatim(user_agent="apod_geocoder")

st.set_page_config(page_title="APOD Analyzer", layout="wide")
st.title("📊 Real Estate Investment Packet Generator")

uploaded_file = st.file_uploader("📂 Upload your MLS CSV export", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded!")

    st.markdown("### 🛠️ Field Mapping")
    address_col = st.selectbox("Select Address Column", df.columns)
    price_col = st.selectbox("Select List Price Column", df.columns)
    tax_col = st.selectbox("Select Property Tax Column", [col for col in df.columns if 'tax' in col.lower()])
    photo_col = st.selectbox("Optional: Select Photo URL Column", ["None"] + list(df.columns))

    properties = []
    for idx, row in df.iterrows():
        with st.container():
            st.markdown(f"---\n#### 🏠 Property #{idx+1}: {row[address_col]}")

            default_rent = DEFAULT_RENT
            default_units = 2
            default_vacancy = DEFAULT_VACANCY_RATE * 100.0

            col1, col2, col3 = st.columns(3)
            with col1:
                rent = st.slider(f"💵 Monthly Rent (per unit)", min_value=500, max_value=5000, value=default_rent, step=50, key=f"rent_{idx}")
            with col2:
                units = st.slider(f"🏘️ Units", min_value=1, max_value=20, value=default_units, key=f"units_{idx}")
            with col3:
                vacancy = st.slider(f"📉 Vacancy Rate (%)", min_value=0, max_value=15, value=int(default_vacancy), key=f"vacancy_{idx}") / 100

            col4, col5 = st.columns(2)
            with col4:
                down_payment_pct = st.slider("💰 Down Payment (%)", min_value=0, max_value=100, value=int(DEFAULT_DOWN_PAYMENT_PCT * 100), key=f"dp_{idx}") / 100
            with col5:
                interest_rate = st.slider("📈 Interest Rate (%)", min_value=0.0, max_value=15.0, value=DEFAULT_INTEREST_RATE * 100, step=0.1, key=f"int_{idx}") / 100

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
            col2.metric("📈 Cap Rate", f"{cap_rate:.2f}%", delta_color="off")
            col3.metric("📊 Cash Flow", f"${cash_flow:,.0f}", delta_color="inverse")

            # Optional image display
            if photo_col != "None" and pd.notnull(row[photo_col]):
                st.image(row[photo_col], caption="📷 MLS Photo", use_column_width=True)

            # Optional map display
            try:
                location = geolocator.geocode(row[address_col])
                if location:
                    m = folium.Map(location=[location.latitude, location.longitude], zoom_start=15)
                    folium.Marker([location.latitude, location.longitude], popup=row[address_col]).add_to(m)
                    folium_static(m)
            except:
                st.warning("🌍 Could not locate property on map.")

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
    results_df = pd.DataFrame(properties)
    st.dataframe(results_df)

    csv_download = results_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV", data=csv_download, file_name="apod_results.csv", mime="text/csv")

    if st.button("📄 Generate Investment Report PDF"):
        html_template = Template("""...PDF TEMPLATE REMAINS HERE...""")
        rendered_html = html_template.render(properties=properties)
        pdf_bytes = pdfkit.from_string(rendered_html, False)
        st.download_button("📥 Download Investment Report PDF", data=pdf_bytes, file_name="Investment_Report.pdf", mime="application/pdf")
