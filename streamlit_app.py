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

def process_and_display_tables(df, start_row, end_row, column_headers, show_done_payments):
    """
    Processes the DataFrame for a given row range and displays a table
    for each row containing only non-blank values.
    """
    # Check if the button to show blank "Contact by" items has been clicked
    show_only_blank_contact = st.session_state.get('show_only_blank_contact', False)

    # Iterate through each row in the selected range.
    # The start_row is 1-based, so we adjust for the 0-based index.
    for index, row in df.iloc[start_row-2:end_row-1].iterrows():
        # Check for 'payment done' in the entire row before processing
        if not show_done_payments:
            # Convert the entire row to a string for case-insensitive search
            row_str = row.astype(str).str.strip().str.lower()
            if 'done' in row_str.values:
                continue # Skip this entire row and do not display a table for it
        
        # Check for 'Contact by' blank values
        contact_by_col_index = -1
        try:
            contact_by_col_index = column_headers.index('Contact by')
        except ValueError:
            pass # 'Contact by' column not found, no filtering needed
        
        # Filtering logic based on the button state
        contact_by_is_blank = False
        if contact_by_col_index != -1:
            if pd.isna(row.iloc[contact_by_col_index]) or row.iloc[contact_by_col_index] == '':
                contact_by_is_blank = True
        
        # If the button has been clicked, skip rows where "Contact by" is not blank
        if show_only_blank_contact and not contact_by_is_blank:
            continue
        
        # Assume the first column contains the person's name.
        person_name = row.iloc[0]
        if not isinstance(person_name, str) or pd.isna(person_name):
            person_name = f"Row {index + 2}" # +2 because index is 0-based and we skipped the header

        # Use markdown to create a centered heading for the person's name, with the row number
        st.markdown(f"<h3 style='text-align: center;'>--- Row {index + 2}: {person_name} ---</h3>", unsafe_allow_html=True)

        # Create a list to store the data for the new DataFrame
        data_rows = []
        
        # Initialize variables for the message text
        var1 = ""
        var2 = ""

        # Get indices for specific columns
        takeaway_col_index = -1
        payment_col_index = -1
        try:
            # CORRECTED: Changed 'ORDER WILL COLLECT TAKE AWAY point' to 'ORDER WILL COLLECT  TAKE AWAY point'
            takeaway_col_index = column_headers.index('ORDER WILL COLLECT  TAKE AWAY point')
        except ValueError:
            pass
        try:
            # CORRECTED: Changed 'Payment Status' to 'payment' based on user's CSV
            payment_col_index = column_headers.index('payment')
        except ValueError:
            pass

        # Corrected logic for `var1`: check for nan or not 'YES'
        if takeaway_col_index != -1:
            # Ensure we can check the value safely, even if it's NaN
            takeaway_value = row.iloc[takeaway_col_index]
            if pd.isna(takeaway_value) or str(takeaway_value).strip().upper() != 'YES':
                var1 = "- whether you will be collecting on site or at the take away point (Please note that the time of collection for Take Aways ranges from 16:30 to 20:00, kindly let us know at what time you will come and collect your order)."

        # Check conditions for `var2`
        if payment_col_index != -1 and (pd.isna(row.iloc[payment_col_index]) or str(row.iloc[payment_col_index]).strip().lower() != 'done'):
            var2 = """
For the payment of your order:
MCB Account Number for Payment: 000 452 303 990\n
Send proof of payment to 54591307
"""
          
        # Iterate over the row data and column headers together
        for i, value in enumerate(row):
            # Skip the first column, which contains the person's name
            if i == 0:
                continue
            
            # Get the original column header and clean it for comparison
            original_header = column_headers[i].strip()
            
            # Map to a new header if a match is found
            display_header = original_header
            if original_header == 'ORDER WILL COLLECT  TAKE AWAY point':
                display_header = 'Order will be collected at take away point'
            elif original_header == 'TIME OF ORDER WILL COLLECTED':
                display_header = 'TIME AT WHICH ORDER WILL BE COLLECTED'
            elif original_header == 'ORDER LIST CONNFIMED WITH CLIENT':
                continue # Skip this column entirely

            # Check if the value is not blank (empty string or NaN)
            if pd.notna(value) and value != '':
                data_rows.append({'Column': display_header, 'Value': str(value)})

        # Create the new DataFrame from the list of dictionaries.
        filtered_data = pd.DataFrame(data_rows)
        
        # If the filtered data is not empty, display the table
        if not filtered_data.empty:
            # Convert the DataFrame to an HTML table string without the index
            html_table = filtered_data.to_html(index=False)
            
            # Add inline styling to the <th> tags to center the headings
            html_table = html_table.replace("<th>", "<th style='text-align: center;'>")
            
            # Display the HTML table using st.markdown
            st.markdown(html_table, unsafe_allow_html=True)
            
            # Add the message below the table
            st.markdown(f"""
Assalamu Allaikum wa Rahmatullahi wa Barakatuhu

We are contacting you to confirm your order for mina bazar on the 6th of September.

Please confirm:
- the amount of each item
{var1}

{var2}

Please respond to this message to confirm your order.

Jazakumullah \n
Wassalam
""")
        else:
            st.info("No data to display for this row after filtering.")

# Main app logic
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
        
        # Add a checkbox to toggle visibility of 'done' payments
        show_done_payments = st.checkbox('Show "payment done" items', value=True)
        
        # Validate that the start row is not greater than the end row
        if start_row > end_row:
            st.error("Error: The start row cannot be greater than the end row.")
        else:
            st.write(f"Displaying rows from {start_row} to {end_row}.")
            # Display the processed tables
            process_and_display_tables(df, start_row, end_row, column_headers, show_done_payments)
    
    else:
        st.warning("The uploaded CSV file is empty.")