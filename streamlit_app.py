import streamlit as st
import pandas as pd
import io

def process_and_display_tables(df, start_row, end_row):
    """
    Processes the DataFrame for a given row range and displays a table
    for each row containing only non-blank values.
    """
    # Clean the header to remove any leading/trailing whitespace.
    df.columns = [col.strip() for col in df.columns]

    # Iterate through each row in the selected range.
    for index, row in df.iloc[start_row-1:end_row].iterrows():
        # Assume the first column contains the person's name.
        person_name = row.iloc[0]
        if not isinstance(person_name, str) or pd.isna(person_name):
            person_name = f"Row {index + 1}"

        st.subheader(f"--- {person_name} ---")

        # Filter out blank values.
        # Convert empty strings to NaN first, then drop NaN values.
        row_data = row.replace('', pd.NA).dropna()

        # Create a new DataFrame for the table.
        # We skip the first column as it's used for the person's name.
        filtered_data = pd.DataFrame(
            {'Column': row_data.index[1:], 'Value': row_data.iloc[1:].values}
        )

        # Convert the 'Value' column to string to prevent type-related errors
        # when displaying the table in Streamlit.
        filtered_data['Value'] = filtered_data['Value'].astype(str)

        # Display the table.
        st.table(filtered_data)

st.title("CSV Data Viewer")
st.markdown("Upload a CSV file and select a row range to view the data in individual tables.")

# File uploader widget
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        # To read the file as a string stream
        string_io = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        df = pd.read_csv(string_io)
    except UnicodeDecodeError:
        # Handle a potential encoding error
        string_io = io.StringIO(uploaded_file.getvalue().decode("latin1"))
        df = pd.read_csv(string_io, encoding='latin1')
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
        st.stop()

    num_rows = df.shape[0]

    if num_rows > 0:
        st.success("File uploaded and read successfully!")

        # Number inputs for start and end rows
        col1, col2 = st.columns(2)
        with col1:
            start_row = st.number_input(
                "Start Row:",
                min_value=1,
                max_value=num_rows,
                value=1
            )
        with col2:
            end_row = st.number_input(
                "End Row:",
                min_value=1,
                max_value=num_rows,
                value=min(10, num_rows)
            )
        
        # Validate that the start row is not greater than the end row
        if start_row > end_row:
            st.error("Error: The start row cannot be greater than the end row.")
        else:
            st.write(f"Displaying rows from {start_row} to {end_row}.")
            # Display the processed tables
            process_and_display_tables(df, start_row, end_row)

    else:
        st.warning("The uploaded CSV file is empty.")
