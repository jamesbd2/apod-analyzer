
# 📊 APOD Analyzer

This Streamlit app allows real estate investors and agents to analyze rental properties quickly using APOD (Annual Property Operating Data) metrics.

## ✨ Features

- 📂 Upload MLS CSV exports
- 🛠️ Interactive sliders for rent, units, vacancy, down payment, and interest rate
- 🧮 Auto-calculates:
  - Net Operating Income (NOI)
  - Cap Rate
  - Cash Flow
  - Cash-on-Cash Return
- 🖼️ Displays property photos (optional)
- 🌍 Embedded maps using property address
- 📥 Download detailed investment analysis as PDF or CSV

## 🏗️ Tech Stack

- Python 🐍
- Streamlit
- Pandas, NumPy
- Jinja2 + xhtml2pdf (for PDF generation)
- Folium + Geopy (for mapping)

## 🚀 How to Run Locally

1. Clone the repository  
```bash
git clone https://github.com/jamesbd2/apod-analyzer.git
cd apod-analyzer
```

2. Create a virtual environment (optional but recommended)  
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

3. Install dependencies  
```bash
pip install -r requirements.txt
```

4. Run the app  
```bash
streamlit run streamlit_app.py
```

## 📄 License

MIT License — free to use and customize.

---

Built by [@jamesbd2](https://github.com/jamesbd2) to automate and streamline rental property analysis.
