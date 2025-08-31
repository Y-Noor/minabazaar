import streamlit as st
import pandas as pd
import io

# Custom CSS to center the main content on the page and center tables
st.markdown("""
<style>
.main-content {
    max-width: 800px;
    margin: 0 auto;
}
table {
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

def process_and_display_tables(df, start_row, end_row, column_headers):
    """
    Processes the DataFrame for a given row range and displays a table
    for each row containing only non-blank values.
    """
    # Iterate through each row in the selected range.
    # The start_row is 1-based, so we adjust for the 0-based index.
    for index, row in df.iloc[start_row-2:end_row-1].iterrows():
        # Assume the first column contains the person's name.
        person_name = row.iloc[0]
        if not isinstance(person_name, str) or pd.isna(person_name):
            person_name = f"Row {index + 2}" # +2 because index is 0-based and we skipped the header

        # Use markdown to create a centered heading for the person's name
        st.markdown(f"<h3 style='text-align: center;'>--- {person_name} ---</h3>", unsafe_allow_html=True)

        # Create a list to store the data for the new DataFrame
        data_rows = []
        
        # Iterate over the row data and column headers together
        for i, value in enumerate(row):
            # Skip the first column, which contains the person's name
            if i == 0:
                continue

            # Check if the value is not blank (empty string or NaN)
            if pd.notna(value) and value != '':
                data_rows.append({'Column': column_headers[i], 'Value': str(value)})

        # Create the new DataFrame from the list of dictionaries.
        # This guarantees that the 'Column' and 'Value' arrays will have the same length.
        filtered_data = pd.DataFrame(data_rows)
        
        # Convert the DataFrame to an HTML table string without the index
        html_table = filtered_data.to_html(index=False)
        
        # Add inline styling to the <th> tags to center the headings
        html_table = html_table.replace("<th>", "<th style='text-align: center;'>")
        
        # Display the HTML table using st.markdown
        st.markdown(html_table, unsafe_allow_html=True)

st.title("CSV Data Viewer")
st.markdown("Upload a CSV file and select a row range to view the data in individual tables.")

# File uploader widget
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        # To read the file as a string stream
        string_io = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        
        # Read the header row separately
        header_df = pd.read_csv(string_io, nrows=1)
        column_headers = list(header_df.columns)
        
        # Reset the stream to the beginning to read the data
        string_io.seek(0)
        
        # Read the rest of the file, skipping the header row
        df = pd.read_csv(string_io, skiprows=1, header=None, names=column_headers)
        
    except UnicodeDecodeError:
        # Handle a potential encoding error
        string_io = io.StringIO(uploaded_file.getvalue().decode("latin1"))
        
        # Read the header row separately
        header_df = pd.read_csv(string_io, nrows=1, encoding='latin1')
        column_headers = list(header_df.columns)
        
        # Reset the stream
        string_io.seek(0)
        
        # Read the rest of the file, skipping the header
        df = pd.read_csv(string_io, skiprows=1, header=None, names=column_headers, encoding='latin1')
        
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
                min_value=2,
                max_value=num_rows + 1,
                value=2
            )
        with col2:
            end_row = st.number_input(
                "End Row:",
                min_value=2,
                max_value=num_rows + 1,
                value=min(num_rows + 1, 11)
            )
        
        # Validate that the start row is not greater than the end row
        if start_row > end_row:
            st.error("Error: The start row cannot be greater than the end row.")
        else:
            st.write(f"Displaying rows from {start_row} to {end_row}.")
            # Display the processed tables
            process_and_display_tables(df, start_row, end_row, column_headers)

    else:
        st.warning("The uploaded CSV file is empty.")
