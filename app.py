import streamlit as st
import psycopg2

# Database connection details from Streamlit secrets
db_host = st.secrets["database"]["host"]
db_user = st.secrets["database"]["user"]
db_password = st.secrets["database"]["password"]
db_name = st.secrets["database"]["database"]

# Function to create a PostgreSQL connection
def create_connection():
    return psycopg2.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        dbname=db_name,
        port=58946  # Specify the port if needed (25453 for the provided URL)
    )

# App Title
st.set_page_config(page_title="Orders System",layout='wide')
st.title("Order Management System")

# Tabs for functionality
tab1, tab2, tab3, tab4 = st.tabs(["Add Order", "Search Orders", "View All Orders","Modify Orders"])

# Tab 1: Add Order
with tab1:
    st.header("Add New Order")
    with st.form("order_form"):
        customer_name = st.text_input("Customer Name")
        customer_phone_1 = st.text_input("Customer Phone 1")
        customer_phone_2 = st.text_input("Customer Phone 2 (Optional)", value="")
        email = st.text_input("Email")
        ship_company = st.text_input("Shipping Company")
        region = st.text_input("Region")
        order_number = st.text_input("order_number")
        order_price = st.number_input("Order Price", min_value=0.0, step=0.01)
        submit = st.form_submit_button("Add Order")

        if submit:
            conn = create_connection()
            cursor = conn.cursor()

            # Check if the customer exists
            cursor.execute(
                "SELECT customer_id FROM customers WHERE customer_phone_1 = %s",
                (customer_phone_1,)
            )
            customer = cursor.fetchone()

            if customer:
                # If the customer exists, use their customer_id
                customer_id = customer[0]
            else:
                # If the customer doesn't exist, create a new customer
                cursor.execute(
                    "INSERT INTO customers (customer_name, customer_phone_1, customer_phone_2, email) VALUES (%s, %s, %s, %s) RETURNING customer_id",
                    (customer_name, customer_phone_1, customer_phone_2, email)
                )
                customer_id = cursor.fetchone()[0]

            # Insert the new order
            cursor.execute(
                "INSERT INTO orders (customer_id, ship_company, region, order_price,order_number) VALUES (%s, %s, %s, %s,%s)",
                (customer_id, ship_company, region, order_price,order_number)
            )

            conn.commit()
            conn.close()
            st.success("Order added successfully!")

# Tab 2: Search Orders
with tab2:
    st.header("Search Orders")
    search_option = st.radio("Search by", ("Customer Phone 1"))
    search_query = st.text_input("Enter Search Term")

    if search_query:
        conn = create_connection()
        cursor = conn.cursor()
        if search_option == "Customer Phone 1":
            cursor.execute(
                """
                SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                       c.email, o.ship_company, o.region, o.order_price
                FROM orders o
                INNER JOIN customers c ON o.customer_id = c.customer_id
                WHERE c.customer_phone_1 = %s
                """,
                (search_query,)
            )

        results = cursor.fetchall()

        if results:
            # Display the orders in a table
            st.write("Search Results:")
            st.table(results)

            # Calculate and display the total order price for this customer
            total_price = sum(order[7] for order in results)  # Assuming order_price is at index 7
            st.write(f"Total Amount Spent: ${total_price:.2f}")
        else:
            st.write("No orders found for the given query.")

        conn.close()

# Tab 3: View All Orders
with tab3:
    st.header("All Orders")
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
               c.email, o.ship_company, o.region, o.order_price
        FROM orders o
        INNER JOIN customers c ON o.customer_id = c.customer_id
        """
    )
    all_orders = cursor.fetchall()

    if all_orders:
        st.table(all_orders)
    else:
        st.write("No orders found.")

    conn.close()
# Tab 4: Update/Remove Orders
with tab4:
    st.header("Update or Remove Orders")
    
    # Section for selecting an order to update or delete
    st.subheader("Select an Order")
    search_order_number = st.text_input("Enter Order Number")

    if search_order_number:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Fetch the order details by order number
        cursor.execute(
            """
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2,
                   c.email, o.ship_company, o.region, o.order_price
            FROM orders o
            INNER JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_number = %s
            """,
            (search_order_number,)
        )
        order_details = cursor.fetchone()

        if order_details:
            st.write("Order Details:")
            st.table([order_details])
            
            # Update Section
            st.subheader("Update Order")
            with st.form("update_order_form"):
                new_ship_company = st.text_input("Shipping Company", value=order_details[5])
                new_region = st.text_input("Region", value=order_details[6])
                # Convert order_details[7] to float to avoid type mismatch
                new_order_price = st.number_input(
                    "Order Price", 
                    value=float(order_details[7]),  # Explicitly cast to float
                    min_value=0.0, 
                    step=0.01
                )
                update_submit = st.form_submit_button("Update Order")

                if update_submit:
                    # Update the order in the database
                    cursor.execute(
                        """
                        UPDATE orders
                        SET ship_company = %s, region = %s, order_price = %s
                        WHERE order_number = %s
                        """,
                        (new_ship_company, new_region, new_order_price, search_order_number)
                    )
                    conn.commit()
                    st.success("Order updated successfully!")


            # Remove Section
            st.subheader("Remove Order")
            if st.button("Delete Order"):
                # Delete the order from the database
                cursor.execute(
                    "DELETE FROM orders WHERE order_number = %s", (search_order_number,)
                )
                conn.commit()
                st.success("Order deleted successfully!")
        else:
            st.write("No order found with the given Order Number.")
        
        conn.close()
