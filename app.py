import streamlit as st
import psycopg2

db_host = st.secrets["database"]["host"]
db_user = st.secrets["database"]["user"]
db_password = st.secrets["database"]["password"]
db_name = st.secrets["database"]["database"]

def create_connection():
    return psycopg2.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        dbname=db_name,
        port=23208  
    )

st.set_page_config(page_title="Orders System",layout='wide')
st.title("Order Management System")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Add Order", "Search Orders", "View All Orders","Modify Orders","Customers with Multiple Orders"])

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

           
            cursor.execute(
                "SELECT customer_id FROM customers WHERE customer_phone_1 = %s",
                (customer_phone_1,)
            )
            customer = cursor.fetchone()

            if customer:
               
                customer_id = customer[0]
            else:
               
                cursor.execute(
                    "INSERT INTO customers (customer_name, customer_phone_1, customer_phone_2, email) VALUES (%s, %s, %s, %s) RETURNING customer_id",
                    (customer_name, customer_phone_1, customer_phone_2, email)
                )
                customer_id = cursor.fetchone()[0]

            
            cursor.execute(
                "INSERT INTO orders (customer_id, ship_company, region, order_price,order_number) VALUES (%s, %s, %s, %s,%s)",
                (customer_id, ship_company, region, order_price,order_number)
            )

            conn.commit()
            conn.close()
            st.success("Order added successfully!")


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
           
            st.write("Search Results:")
            st.table(results)

           
            total_price = sum(order[7] for order in results)  
            st.write(f"Total Amount Spent: ${total_price:.2f}")
        else:
            st.write("No orders found for the given query.")

        conn.close()


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

with tab4:
    st.header("Update or Remove Orders")
    
    
    st.subheader("Select an Order")
    search_order_number = st.text_input("Enter Order Number")

    if search_order_number:
        conn = create_connection()
        cursor = conn.cursor()
        
        
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
            
            
            st.subheader("Update Order")
            with st.form("update_order_form"):
                new_ship_company = st.text_input("Shipping Company", value=order_details[5])
                new_region = st.text_input("Region", value=order_details[6])
                
                new_order_price = st.number_input(
                    "Order Price", 
                    value=float(order_details[7]), 
                    min_value=0.0, 
                    step=0.01
                )
                update_submit = st.form_submit_button("Update Order")

                if update_submit:
                   
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


           
            st.subheader("Remove Order")
            if st.button("Delete Order"):
                
                cursor.execute(
                    "DELETE FROM orders WHERE order_number = %s", (search_order_number,)
                )
                conn.commit()
                st.success("Order deleted successfully!")
        else:
            st.write("No order found with the given Order Number.")
        
        conn.close()

with tab5:
    st.header("Customers with Multiple Orders")
    conn = create_connection()
    cursor = conn.cursor()

    
    cursor.execute(
        """
        SELECT c.customer_name, c.customer_phone_1, 
               ARRAY_AGG(o.order_number) AS order_numbers,
               SUM(o.order_price) AS total_price
        FROM customers c
        INNER JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.customer_name, c.customer_phone_1
        HAVING COUNT(o.order_number) > 1
        """
    )
    multiple_orders = cursor.fetchall()

    if multiple_orders:
       
        data = []
        for row in multiple_orders:
            customer_name, customer_phone_1, order_numbers, total_price = row
            data.append({
                "Customer Name": customer_name,
                "Phone Number": customer_phone_1,
                "Order Numbers": ", ".join(order_numbers),
                "Total Price": f"${total_price:.2f}"
            })

        
        st.write("Customers with Multiple Orders:")
        st.dataframe(data)
    else:
        st.write("No customers with multiple orders found.")

    conn.close()
