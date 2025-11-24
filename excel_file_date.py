import pandas as pd

def load_excel_events(file_path="appointments.xlsx"):
    try:
        df = pd.read_excel(file_path)
        # Ensure correct column names exist
        required_cols = {"title", "start", "end"}
        if not required_cols.issubset(df.columns):
            st.error("Excel file must contain: title, start, end")
            return []

        # Convert timestamps to strings for the calendar widget
        df["start"] = pd.to_datetime(df["start"]).astype(str)
        df["end"] = pd.to_datetime(df["end"]).astype(str)

        # Convert to list of dicts
        return df.to_dict(orient="records")
    except Exception as e:
        st.error(f"Error loading Excel appointments: {e}")
        return []
