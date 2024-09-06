import streamlit as st
import pandas as pd
import sqlite3
import datetime

# Database setup and connection
conn = sqlite3.connect('fieldlist.db')
c = conn.cursor()

# Function to drop the old table and create the new one without 'earnings'
def reset_database():
    # Drop the old table if it exists
    c.execute('DROP TABLE IF EXISTS field')
    
    # Create the new table
    c.execute('''
    CREATE TABLE IF NOT EXISTS field (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        destination TEXT,
        product_name TEXT,
        date TEXT,
        quantity INTEGER,
        weight REAL,
        driver_name TEXT,
        truck TEXT,
        toll_fees REAL,
        food_costs REAL,
        amount_charged REAL,
        driver_due REAL,
        owner_due REAL
    )
    ''')
    conn.commit()

# Call the reset_database function to reset the database
reset_database()

# Function to load data from the database
def load_data():
    query = 'SELECT * FROM field'
    df = pd.read_sql(query, conn)
    return df

# Function to add data to the database
def add_to_db(source, destination, product_name, date, quantity, weight, driver_name, truck, toll_fees, food_costs, amount_charged):
    total_expenses = toll_fees + food_costs
    driver_due = 0.10 * (amount_charged - total_expenses)  # Driver gets 10% of net earnings
    owner_due = amount_charged - total_expenses - driver_due  # Owner gets the remaining amount

    # Insert into the database
    c.execute('''
        INSERT INTO field (
            source, destination, product_name, date, quantity, weight,
            driver_name, truck, toll_fees, food_costs, amount_charged, driver_due, owner_due
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''',
        (source, destination, product_name, date, quantity, weight, driver_name, truck, toll_fees, food_costs, amount_charged, driver_due, owner_due))
    conn.commit()

# Authentication and login system using session_state
def login():
    st.title('Kai Logistics Solutions - Login')

    # Store login state in session_state
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["role"] = None

    if st.session_state["logged_in"]:
        st.success(f'Logged in as {st.session_state["username"]}')
    else:
        # Prompt for username and password
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')

        if st.button('Login'):
            if username in users and users[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = users[username]["role"]
                st.success(f'Logged in as {username}')
            else:
                st.error('Invalid username or password')

# Function to check if user is logged in
def check_login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["role"] = None
    return st.session_state["logged_in"]

# Function to log out
def logout():
    st.session_state.clear()  # Clear the entire session state
    st.experimental_rerun()  # Refresh to go back to the login page

# User credentials and roles
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "driver": {"password": "driver123", "role": "driver"},
    "manager": {"password": "manager123", "role": "manager"}
}

# Role-based access control
def role_based_access():
    role = st.session_state["role"]
    
    if role in ["admin", "manager", "driver"]:
        st.markdown("### 🚚 **Add a New Record**")
        with st.container():
            st.write("Fill in the details for the new logistics record.")
            col1, col2 = st.columns(2)
            with col1:
                source = st.text_input('Enter Source Location')
                destination = st.text_input('Enter Destination Location')
                product_name = st.text_input('Product Name')
            with col2:
                date = st.date_input('Date of Shipment')
                quantity = st.number_input('Quantity (件)', min_value=1)
                weight = st.number_input('Weight (KG)', min_value=1.0)

            # Additional Information (toll fees, food costs, and charges)
            st.markdown("---")
            st.markdown("### 📝 **Additional Information**")
            driver_name = st.text_input('Driver Name')
            truck = st.selectbox('Truck', options=['Benz', 'Volvo'])
            toll_fees = st.number_input('Toll Fees', min_value=0.0)
            food_costs = st.number_input('Food Costs', min_value=0.0)
            amount_charged = st.number_input('Amount Charged for the Trip', min_value=0.0)

            # Validation to ensure all fields are filled in before adding the record
            if not source or not destination or not product_name or not driver_name or not truck or amount_charged <= 0:
                st.warning("Please fill in all the fields before submitting.")
            else:
                # Automatic Calculations for Driver and Owner Dues
                total_expenses = toll_fees + food_costs
                driver_due = 0.10 * (amount_charged - total_expenses)
                owner_due = amount_charged - total_expenses - driver_due

                # Button to add record to the database
                if st.button("Add Record"):
                    add_to_db(source, destination, product_name, date.strftime('%Y-%m-%d'), quantity, weight, driver_name, truck, toll_fees, food_costs, amount_charged)
                    st.success("Record added successfully!")

    # Only admin and manager can view records
    if role in ["admin", "manager"]:
        st.markdown("---")
        st.markdown("### 📊 **Data Dashboard**")
        st.write("View and export your data records.")
        with st.expander("View Records"):
            data = load_data()
            st.dataframe(data)

        if st.button("Export to Excel"):
            st.success("Data exported to Excel!")

# Main app logic
if check_login():
    st.sidebar.write(f'Logged in as {st.session_state["username"]} ({st.session_state["role"]})')

    # Add a logout button in the sidebar
    if st.sidebar.button("Logout"):
        logout()

    # Handle role-based access
    role_based_access()
else:
    login()
