import streamlit as st
import pandas as pd
import hashlib
import io
from datetime import datetime

def generate_deterministic_unique_id_with_initials(first_name, middle_name, last_name, kendra, zone, email, phone=""):
    """
    YOUR ORIGINAL FUNCTION - keeping exact same logic for consistency
    Only added NaN handling for pandas DataFrame compatibility
    """
    # Handle NaN values by converting to empty string (only change from original)
    first_name = str(first_name) if pd.notna(first_name) else ""
    last_name = str(last_name) if pd.notna(last_name) else ""
    middle_name = str(middle_name) if pd.notna(middle_name) else ""
    kendra = str(kendra) if pd.notna(kendra) else ""
    zone = str(zone) if pd.notna(zone) else ""
    email = str(email) if pd.notna(email) else ""
    phone = str(phone) if pd.notna(phone) else ""
    
    # ORIGINAL LOGIC BELOW - UNCHANGED
    # Check if first_name and last_name are not empty
    if first_name and last_name:
        # Use the first letter of the first and last name, uppercased
        initials = f"{first_name[0].upper()}{last_name[0].upper()}"
    else:
        initials = ""

    # Combine the inputs into a single string for hashing
    primary_contact = phone if phone else email
    combined_string = f"{first_name}{middle_name}{last_name}{kendra}{zone}{primary_contact}"

    # Use SHA-256 hash function to generate a consistent hash value
    hash_object = hashlib.sha256(combined_string.encode())

    # Convert the hash to a decimal number then take the last 5 digits
    unique_number = int(hash_object.hexdigest(), 16) % 100000  # Ensuring the ID is within a 5-digit limit

    # Combine initials with the unique number, formatted to 5 digits
    unique_id = f"{initials}-{unique_number:05d}"  # Formats the number to a fixed width of 5, padding with zeros if necessary

    return unique_id

def process_dataframe(df, column_mapping):
    """
    Process the dataframe to generate unique IDs
    """
    # Create a copy of the dataframe
    processed_df = df.copy()
    
    # Generate unique IDs for each row
    unique_ids = []
    for index, row in df.iterrows():
        try:
            unique_id = generate_deterministic_unique_id_with_initials(
                first_name=row.get(column_mapping['first_name'], ''),
                middle_name=row.get(column_mapping['middle_name'], ''),
                last_name=row.get(column_mapping['last_name'], ''),
                kendra=row.get(column_mapping['kendra'], ''),
                zone=row.get(column_mapping['zone'], ''),
                email=row.get(column_mapping['email'], ''),
                phone=row.get(column_mapping.get('phone', ''), '')
            )
            unique_ids.append(unique_id)
        except Exception as e:
            st.error(f"Error processing row {index + 1}: {str(e)}")
            unique_ids.append("ERROR")
    
    # Add unique IDs to the dataframe
    processed_df.insert(0, 'Unique_ID', unique_ids)
    
    return processed_df

def main():
    st.set_page_config(
        page_title="Unique ID Generator",
        page_icon="🆔",
        layout="wide"
    )
    
    st.title("🆔 Unique ID Generator")
    st.markdown("Generate unique IDs individually or in bulk from CSV/Excel files")
    
    # Tab selection
    tab1, tab2 = st.tabs(["🧑 Individual ID Generator", "📄 Bulk ID Generator"])
    
    with tab1:
        st.subheader("Generate Single Unique ID")
        st.markdown("Enter the details below to generate an individual unique ID")
        
        # Individual input fields
        col1, col2 = st.columns(2)
        
        with col1:
            individual_first_name = st.text_input("First Name *", key="ind_first_name", help="Required field")
            individual_middle_name = st.text_input("Middle Name", key="ind_middle_name", help="Optional field")
            individual_last_name = st.text_input("Last Name *", key="ind_last_name", help="Required field")
        
        with col2:
            individual_kendra = st.text_input("Kendra", key="ind_kendra", help="Optional field")
            individual_zone = st.text_input("Zone", key="ind_zone", help="Optional field")
            individual_phone = st.text_input("Phone", key="ind_phone", help="Optional field")
            individual_email = st.text_input("Email", key="ind_email", help="Optional field")
        
        # Generate individual ID
        if st.button("🚀 Generate Individual ID", type="primary", key="generate_individual"):
            if individual_first_name.strip() and individual_last_name.strip():
                with st.spinner("Generating unique ID..."):
                    # Use the exact same function
                    unique_id = generate_deterministic_unique_id_with_initials(
                        first_name=individual_first_name.strip(),
                        middle_name=individual_middle_name.strip(),
                        last_name=individual_last_name.strip(),
                        kendra=individual_kendra.strip(),
                        zone=individual_zone.strip(),
                        email=individual_email.strip(),
                        phone=individual_phone.strip()
                    )
                
                # Display result
                st.success("✅ Unique ID Generated Successfully!")
                
                # Show the generated ID prominently
                st.markdown("### Generated Unique ID:")
                st.code(unique_id, language=None)
                
                # Show input summary
                with st.expander("📋 Input Summary"):
                    input_data = {
                        "Field": ["First Name", "Middle Name", "Last Name", "Kendra", "Zone", "Phone", "Email"],
                        "Value": [
                            individual_first_name.strip() or "Not provided",
                            individual_middle_name.strip() or "Not provided", 
                            individual_last_name.strip() or "Not provided",
                            individual_kendra.strip() or "Not provided",
                            individual_zone.strip() or "Not provided",
                            individual_phone.strip() or "Not provided",
                            individual_email.strip() or "Not provided"
                        ]
                    }
                    st.table(pd.DataFrame(input_data))
                
                # Copy to clipboard option
                st.markdown("📋 **Copy the ID above** - The same inputs will always generate the same ID")
                
            else:
                st.error("❌ Please provide both First Name and Last Name to generate a unique ID")
        
        # Add some spacing and information
        st.markdown("---")
        st.info("💡 **Tip**: The same person details will always generate the same unique ID due to deterministic hashing")
    
    with tab2:
        st.subheader("Generate IDs from File")
        st.markdown("Upload your CSV or Excel file to generate unique IDs for multiple users")
        
        # File upload
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload a file containing user information to generate unique IDs. Required: First Name, Last Name. Optional: Middle Name, Kendra, Zone, Phone, Email. If Phone is present, it will be preferred over Email for ID generation."
    )
    
    if uploaded_file is not None:
        try:
            # Read the file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"File uploaded successfully! Found {len(df)} records.")
            
            # Show preview of uploaded data
            with st.expander("📋 Preview of uploaded data"):
                st.dataframe(df.head(10))
            
            # Column mapping section
            st.subheader("📍 Map Your Columns")
            st.info("Please map your file columns to the required fields for ID generation. Phone is preferred over Email if both are present.")
            
            # Get available columns
            available_columns = [''] + list(df.columns)
            
            col1, col2 = st.columns(2)
            
            with col1:
                first_name_col = st.selectbox("First Name Column", available_columns, key="first_name")
                middle_name_col = st.selectbox("Middle Name Column", available_columns, key="middle_name")
                last_name_col = st.selectbox("Last Name Column", available_columns, key="last_name")
            
            with col2:
                kendra_col = st.selectbox("Kendra Column", available_columns, key="kendra")
                zone_col = st.selectbox("Zone Column", available_columns, key="zone")
                phone_col = st.selectbox("Phone Column", available_columns, key="phone")
                email_col = st.selectbox("Email Column", available_columns, key="email")
            
            # Create column mapping
            column_mapping = {
                'first_name': first_name_col,
                'middle_name': middle_name_col,
                'last_name': last_name_col,
                'kendra': kendra_col,
                'zone': zone_col,
                'phone': phone_col,
                'email': email_col
            }
            
            # Check if at least first name and last name are mapped
            if first_name_col and last_name_col:
                if st.button("🚀 Generate Unique IDs", type="primary"):
                    with st.spinner("Generating unique IDs..."):
                        processed_df = process_dataframe(df, column_mapping)
                    
                    st.success(f"Successfully generated {len(processed_df)} unique IDs!")
                    
                    # Show preview of processed data
                    with st.expander("👀 Preview of generated IDs"):
                        st.dataframe(processed_df.head(10))
                    
                    # Download section
                    st.subheader("📥 Download Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # CSV download
                        csv_buffer = io.StringIO()
                        processed_df.to_csv(csv_buffer, index=False)
                        csv_data = csv_buffer.getvalue()
                        
                        st.download_button(
                            label="📄 Download as CSV",
                            data=csv_data,
                            file_name=f"unique_ids_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        # Excel download
                        excel_buffer = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                            processed_df.to_excel(writer, sheet_name='Data_with_IDs', index=False)
                        excel_data = excel_buffer.getvalue()
                        
                        st.download_button(
                            label="📊 Download as Excel",
                            data=excel_data,
                            file_name=f"unique_ids_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    # Statistics
                    st.subheader("📊 Statistics")
                    
                    stats_col1, stats_col2, stats_col3 = st.columns(3)
                    
                    with stats_col1:
                        st.metric("Total Records", len(processed_df))
                    
                    with stats_col2:
                        unique_count = processed_df['Unique_ID'].nunique()
                        st.metric("Unique IDs Generated", unique_count)
                    
                    with stats_col3:
                        duplicate_count = len(processed_df) - unique_count
                        st.metric("Duplicate IDs", duplicate_count)
                    
                    if duplicate_count > 0:
                        st.warning("⚠️ Some duplicate IDs were found. This might indicate duplicate records in your data.")
                        
                        with st.expander("View Duplicate IDs"):
                            duplicates = processed_df[processed_df.duplicated(subset=['Unique_ID'], keep=False)]
                            st.dataframe(duplicates.sort_values('Unique_ID'))
            
            else:
                st.warning("⚠️ Please map at least the 'First Name' and 'Last Name' columns to generate unique IDs.")
        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.info("Please make sure your file is a valid CSV or Excel file.")
    
    # Instructions
    with st.sidebar:
        st.markdown("### 📋 Instructions")
        
        st.markdown("#### 🧑 Individual ID Generation:")
        st.markdown("""
        1. Go to **Individual ID Generator** tab
        2. Fill in the person's details
        3. Click **Generate Individual ID**
        4. Copy the generated unique ID
        """)
        
        st.markdown("#### 📄 Bulk ID Generation:")
        st.markdown("""
        1. Go to **Bulk ID Generator** tab
        2. **Upload File**: Choose a CSV or Excel file containing user data
        3. **Map Columns**: Select which columns correspond to each required field
        4. **Generate IDs**: Click the button to generate unique IDs
        5. **Download**: Get your results in CSV or Excel format
        """)
        
        st.markdown("### 📝 Required Fields")
        st.markdown("""
        - **First Name** (Required)
        - **Last Name** (Required)
        - Middle Name (Optional)
        - Kendra (Optional)
        - Zone (Optional)
        - Phone (Optional, preferred over Email)
        - Email (Optional, used if Phone is not provided)
        """)
        
        st.markdown("### ℹ️ About Unique IDs")
        st.markdown("""
        The unique ID format is: **{Initials}-{5-digit-number}**
        
        Example: **JD-12345**
        - JD = John Doe's initials
        - 12345 = Generated from all provided information
        
        **🔒 Deterministic**: Same person details = Same unique ID every time
        """)
        
        st.markdown("### 🔒 Privacy Note")
        st.info("All processing is done locally. Your data is not stored or transmitted anywhere.")

if __name__ == "__main__":
    main()