# Superstore Sales Analytics Dashboard

A 20-page Streamlit dashboard for the Sample Superstore dataset.

## Run locally in VS Code

1. Open this folder (`superstore_dashboard`) in VS Code.
2. Open a terminal (Terminal → New Terminal).
3. Create a virtual environment (recommended):
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the app:
   ```
   streamlit run app.py
   ```
6. Your browser will open automatically at `http://localhost:8501`.
   If not, open that URL manually.

## Project structure
```
superstore_dashboard/
    app.py                     <- main app, all 20 pages (sidebar navigation)
    requirements.txt
    data/
        sample_superstore.csv  <- your uploaded data, converted to CSV
    utils/
        data_loader.py         <- data loading + common sidebar filters
        kpis.py                <- KPI helper functions
```

## Notes
- Your original `superstore.xls` was converted to `data/sample_superstore.csv` for
  fast, dependency-light loading (no need for `xlrd` at runtime).
- All 20 pages from the design spec are implemented in a single `app.py` using
  `st.sidebar.radio` navigation (equivalent to Streamlit's multipage `pages/`
  folder, just consolidated for simplicity — easy to split later if desired).
- Charts use Plotly for interactivity (hover, zoom, legend toggling).
