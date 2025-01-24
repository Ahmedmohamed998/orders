import streamlit as st
import psycopg2
import re
import pandas as pd
import io
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
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
def custom_number_input(label, value=0, min_value=0, step=1):
    value = st.text_input(label, value=str(value))

    try:
        numeric_value = int(value)
        if numeric_value < min_value:
            st.error(f"Value must be at least {min_value}")
            numeric_value = min_value
    except ValueError:
        st.error("Please enter a valid integer.")
        numeric_value = value

    return numeric_value

st.sidebar.title("Order Type")
page = st.sidebar.radio("Select a page", ["Completed Orders", "Cancelled Orders","Returned Orders","Shipping Problems"])
egypt_governorates = [
        "Cairo", "Alexandria", "Giza", "Dakahlia", "Red Sea", "Beheira",
        "Fayoum", "Gharbia", "Ismailia", "Menofia", "Minya", "Qaliubiya",
        "New Valley", "Suez", "Aswan", "Assiut", "Beni Suef", "Port Said",
        "Damietta", "Sharkia", "South Sinai", "Kafr El Sheikh", "Matruh",
        "Luxor", "Qena", "North Sinai", "Sohag"
    ]
reasons=['Customer','Delivery Man']
reasons_1=['Customer','Out Of Stock','Team']
reasons_2=['Customer','Delivery Man','Team']
Status=['Returned','Exchanged','Reshipping','Team']
Options= ["No", "Yes"]
if page == "Completed Orders":
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Add Order", "Search Orders", "View All Orders","Modify Orders","Customers with Multiple Orders","Orders View","Delete Orders"])
    with tab1:
        st.header("Add New Order")
        with st.form("order_form"):
            customer_name = st.text_input("Customer Name")
            
            customer_phone_1 = st.text_input("Customer Phone 1")

            def correct_phone_number(phone):
                if re.search(r"[^\d]", phone):
                    phone = re.sub(r"[^\d]", "", phone)
                    return phone, False,True 
                elif not phone.startswith("01"):
                    phone="01"+phone
                    return phone, False,True
                if len(phone) == 11:
                    return phone, True,True 
                else:
                    return phone, False,False

            corrected_phone_1, is_valid_1, is_valid_11 = correct_phone_number(customer_phone_1)

            if customer_phone_1:
                if not is_valid_11:
                    st.markdown(
                        f"<div style='color: red;'>(Invalid Length): {corrected_phone_1}</div>",
                        unsafe_allow_html=True,
                    )
                elif not is_valid_1:
                    st.markdown(
                        f"<div style='color: orange;'>Corrected Phone 1 (Invalid Format): {corrected_phone_1}</div>",
                        unsafe_allow_html=True,
                    )

            customer_phone_2 = st.text_input("Customer Phone 2 (Optional)", value="")
            corrected_phone_2, is_valid_2, is_valid_22 = correct_phone_number(customer_phone_2)

            if customer_phone_2:
                if not is_valid_22:
                    st.markdown(
                        f"<div style='color: red;'>(Invalid Length): {corrected_phone_2}</div>",
                        unsafe_allow_html=True,
                    )
                elif not is_valid_2:
                    st.markdown(
                        f"<div style='color: orange;'>Corrected Phone 2 (Invalid Format): {corrected_phone_2}</div>",
                        unsafe_allow_html=True,
                    )

            email = st.text_input("Email (Optional)", value="")
            def correct_email(email):
                if ' ' in email:
                    email = re.sub(r"\s+", "", email)
                    return email, False
                else:
                    return email, True
            corrected_email,is_valid=correct_email(email)
            if email:
                if not is_valid:
                    st.markdown(
                        f"<div style='color: orange;'>Corrected email (Invalid Format): {corrected_email}</div>",
                        unsafe_allow_html=True,
                    )
            ship_company = st.text_input("Shipping Company")
            region = st.selectbox("Region",egypt_governorates)
            order_number = st.text_input("Order Code")
            hoodies = custom_number_input("Number Of Products", min_value=0,step=1)
            order_price = custom_number_input("Order Price", min_value=0, step=1)
            shipping_price = custom_number_input("Shipping Price", min_value=0, step=1)
            days_to_receive = custom_number_input("Days to Receive Order",min_value=0,step=1)
            submit = st.form_submit_button("Add Order")

            def contains_arabic(text):
                return bool(re.search(r'[\u0600-\u06FF]', text))

            if submit:
                if not customer_name.strip():
                    st.error("Customer Name is required.")
                elif contains_arabic(customer_name):
                    st.error("Customer Name cannot contain Arabic characters.")
                elif not is_valid_1:
                    st.error("Customer Phone 1 is invalid. Please correct the number.")
                elif contains_arabic(ship_company):
                    st.error("Shipping Company cannot contain Arabic characters.")
                elif contains_arabic(region):
                    st.error("Region cannot contain Arabic characters.")
                elif customer_phone_2 and not is_valid_2:
                    st.error("Customer Phone 2 is invalid. Please correct the number.")
                elif email and not is_valid :
                    st.error("Email is invalid. Please correct the email")
                elif not ship_company.strip():
                    st.error("Shipping Company is required.")
                elif not region.strip():
                    st.error("Region is required.")
                elif not order_number.strip():
                    st.error("Order Number is required.")
                elif order_price is None or order_price < 0:
                    st.error("Order Price is required.")
                elif shipping_price is None or shipping_price < 0:
                    st.error("Shipping Price is required.")
                elif hoodies is None or hoodies==0:
                    st.error("Number of Products is required.")
                else:
                    conn = create_connection()
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT 1 FROM orders WHERE order_number = %s",
                        (order_number,)
                    )
                    existing_order = cursor.fetchone()

                    if existing_order:
                        st.error("Order Number already exists. Please enter a unique Order Number.")
                    else:
                        cursor.execute(
                            "SELECT customer_id FROM customers WHERE customer_phone_1 = %s",
                            (corrected_phone_1,)
                        )
                        customer = cursor.fetchone()

                        if customer:
                            customer_id = customer[0]
                        else:
                            cursor.execute(
                                "INSERT INTO customers (customer_name, customer_phone_1, customer_phone_2, email) VALUES (%s, %s, %s, %s) RETURNING customer_id",
                                (customer_name, corrected_phone_1, corrected_phone_2, email)
                            )
                            customer_id = cursor.fetchone()[0]

                        cursor.execute(
                            "INSERT INTO orders (customer_id, ship_company, region, order_price, order_number,days_to_receive,hoodies,shipping_price) VALUES (%s, %s, %s, %s, %s,%s,%s,%s)",
                            (customer_id, ship_company, region, order_price, order_number,days_to_receive,hoodies,shipping_price)
                        )

                        conn.commit()
                        st.success("Order added successfully!")
                        
                    conn.close()


    with tab2:
        st.header("Search Orders")
        search_option = st.radio("Search by", ("Order Code", "Customer Phone 1", "Name", "Email"))
        search_query = st.text_input("Enter Search Term")

        if search_query:
            conn = create_connection()
            cursor = conn.cursor()

            if search_option == "Order Code":
                search_condition = "o.order_number = %s"
            elif search_option == "Customer Phone 1":
                search_condition = "c.customer_phone_1 = %s"
            elif search_option == "Name":
                search_condition = "c.customer_name ILIKE %s"
                search_query = f"%{search_query}%" 
            else:
                search_condition = "c.email ILIKE %s"
                search_query = f"%{search_query}%"

            cursor.execute(
                f"""
                SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                    c.email, o.ship_company, o.region, o.order_price,o.shipping_price,o.days_to_receive,o.hoodies
                FROM orders o
                INNER JOIN customers c ON o.customer_id = c.customer_id
                WHERE {search_condition}
                """,
                (search_query,)
            )

            results = cursor.fetchall()

            if results:
                st.write("Search Results:")
                st.table(results)
                total_price = sum(order[7] for order in results)
                total_hoodies = sum(int(order[9]) for order in results)
                st.write(f"Total Amount Spent: {total_price}")
                st.write(f"Total Number of Products: {total_hoodies}")
            else:
                st.write("No orders found for the given query.")

            conn.close()
            
    with tab3:
        st.header("All Orders")
        
        sort_by = st.selectbox("Sort by", ["Order Code", "Order Price"])
        sort_order = st.radio("Sort orders", ["Ascending", "Descending"])
        
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT ship_company FROM orders")
        ship_companies = [row[0] for row in cursor.fetchall()]
        selected_ship_company = st.selectbox("Filter by Shipping Company", ["All"] + ship_companies)
        sort_column = "CAST(o.order_number AS INTEGER)" if sort_by == "Order Code" else "o.order_price"
        sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
        
        query = f"""
        SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
            c.email, o.ship_company, o.region, o.order_price,o.days_to_receive,o.hoodies,shipping_price
        FROM orders o
        INNER JOIN customers c ON o.customer_id = c.customer_id
        """
        if selected_ship_company != "All":
            query += f" WHERE o.ship_company = '{selected_ship_company}'"
        query += f" ORDER BY {sort_column} {sort_direction}"

        cursor.execute(query)
        all_orders = cursor.fetchall()

        total_query = "SELECT COUNT(*),COALESCE(SUM(hoodies),0), COALESCE(SUM(order_price), 0), COALESCE(SUM(shipping_price), 0) FROM orders"
        if selected_ship_company != "All":
            total_query += f" WHERE ship_company = '{selected_ship_company}'"
        cursor.execute(total_query)
        total_orders,total_hoodies,total_price,total_shipping_price = cursor.fetchone()

        conn.close()

        if all_orders:
            data = []
            for order in all_orders:
                data.append({
                    "Order Number": order[0],
                    "Customer Name": order[1],
                    "Phone 1": order[2],
                    "Phone 2": order[3],
                    "Email": order[4],
                    "Shipping Company": order[5],
                    "Region": order[6],
                    "Order Price": f"{order[7]}",
                    "Shipping Price":order[10],
                    "Order Profit": (order[7] or 0) - (order[10] or 0),
                    "Days to Receive":order[8],
                    "Number of Products":order[9]
                })
            df = pd.DataFrame(data)
            st.write("All Orders:")
            st.dataframe(df)
            st.write(f"**Total Orders:** {total_orders}")
            st.write(f"**Total Price:** {int(total_price):,}".replace(",", "."))
            st.write(f"**Total Shipping Price:** {int(total_shipping_price):,}".replace(",", "."))
            total_order_profit = df["Order Profit"].sum()
            st.write(f"**Total Order Profit:** {int(total_order_profit):,}".replace(",", "."))
            st.write(f"**Total Products:** {total_hoodies}")
            st.write("Download Data:")
            
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name="orders.csv",
                mime="text/csv"
            )
            
            excel_data = io.BytesIO()
            with pd.ExcelWriter(excel_data, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Orders")
            excel_data.seek(0)
            st.download_button(
                label="Download as Excel",
                data=excel_data,
                file_name="orders.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            def generate_pdf_with_reportlab(dataframe):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
                
                data = [dataframe.columns.tolist()] + dataframe.values.tolist()
                
                col_widths = [
                    70,  
                    100,  
                    80,  
                    80,  
                    180,  
                    100, 
                    70,  
                    75,
                    20,
                    15,
                    15,   
                ]
                
                table = Table(data, colWidths=col_widths)
                table.setStyle(
                    TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ])
                )
                
                elements = [table]
                doc.build(elements)
                
                buffer.seek(0)
                return buffer.read()

            pdf_data = generate_pdf_with_reportlab(df)
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="orders.pdf",
                mime="application/pdf"
            )

        else:
            st.write("No orders found.")

    with tab4:
        st.header("Update or Remove Orders")
        
        st.subheader("Select an Order")
        search_order_number = st.text_input("Enter Order Code")

        if search_order_number:
            conn = create_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2,
                    c.email, o.ship_company, o.region, o.order_price,o.days_to_receive,o.hoodies,o.shipping_price
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
                    new_name=st.text_input("Customer Name",value=order_details[1])
                    new_phone1=st.text_input("Customer Phone 1",value=order_details[2])
                    new_phone2=st.text_input("Customer Phone 1",value=order_details[3])
                    new_email=st.text_input("Email",value=order_details[4])
                    new_ship_company = st.text_input("Shipping Company", value=order_details[5])
                    new_region = st.selectbox("Region",egypt_governorates,index=egypt_governorates.index(order_details[6]))
                    new_order_price = custom_number_input("Order Price",value=order_details[7],min_value=0,step=1)
                    new_shipping_price = custom_number_input("Shipping Price",value=order_details[10],min_value=0,step=1)
                    new_days_to_receive=st.text_input("Days_to_receive",value=order_details[8])
                    new_hoodies=custom_number_input("Number of Produtcs",value=order_details[9],min_value=0,step=1)
                    update_submit = st.form_submit_button("Update Order")

                    if update_submit:
                            cursor.execute(
                                """
                                UPDATE customers
                                SET customer_name = %s, customer_phone_1 = %s, customer_phone_2 = %s, email = %s
                                WHERE customer_id = (
                                    SELECT customer_id 
                                    FROM orders 
                                    WHERE order_number = %s
                                )
                                """,
                                (new_name, new_phone1, new_phone2, new_email, search_order_number)
                            )
                            
                            cursor.execute(
                                """
                                UPDATE orders
                                SET ship_company = %s, region = %s, order_price = %s,days_to_receive=%s,hoodies=%s,shipping_price=%s
                                WHERE order_number = %s
                                """,
                                (new_ship_company, new_region, new_order_price, new_days_to_receive, new_hoodies, new_shipping_price,search_order_number)
                            )

                            conn.commit()
                            st.success("Order updated successfully!")

                st.subheader("Remove Order")
                with st.form("delete_order_form"):
                    delete_password = st.text_input("Enter Password to Confirm Deletion", type="password")
                    delete_submit = st.form_submit_button("Delete Order")

                    if delete_submit:
                        if delete_password == "admin":
                            cursor.execute(
                                "DELETE FROM orders WHERE order_number = %s", (search_order_number,)
                            )
                            conn.commit()
                            st.success("Order deleted successfully!")
                        else:
                            st.error("Incorrect password. Order deletion canceled.")
            else:
                st.write("No order found with the given Order Number.")
            
            conn.close()
    with tab5:
        st.header("Customers with Multiple Orders")

        sort_by = st.selectbox("Sort by", ["Order Code", "Total Price"], key="sort_by_selectbox")
        sort_order = st.radio("Sort order", ["Ascending", "Descending"], key="sort_order_selectbox")

        conn = create_connection()
        cursor = conn.cursor()

        sort_column = "MIN(CAST(o.order_number AS INTEGER))" if sort_by == "Order Code" else "SUM(o.order_price)"
        sort_direction = "ASC" if sort_order == "Ascending" else "DESC"

        query = f"""
                SELECT c.customer_name, c.customer_phone_1, c.email,
                    ARRAY_AGG(o.order_number ORDER BY o.order_number) AS order_numbers,
                    COUNT(o.order_number) AS order_count,
                    SUM(o.order_price) AS total_price,
                    SUM(o.hoodies) AS total_products,
                    SUM(o.shipping_price) AS total_shipping,
                    ROUND(AVG(CAST(o.days_to_receive AS NUMERIC)), 2) AS avg_days_to_receive
                FROM customers c
                INNER JOIN orders o ON c.customer_id = o.customer_id
                GROUP BY c.customer_name, c.customer_phone_1, c.email
                HAVING COUNT(o.order_number) > 1
                ORDER BY {sort_column} {sort_direction}
                """

        cursor.execute(query)
        multiple_orders = cursor.fetchall()

        if multiple_orders:
            data = []
            total_price = 0
            total_products = 0
            total_shipping = 0
            for row in multiple_orders:
                customer_name, customer_phone_1, email, order_numbers, order_count, customer_total_price, customer_total_products,customer_total_shipping ,avg_days_to_receive = row
                customer_total_products = customer_total_products or 0
                total_price += customer_total_price
                total_shipping += customer_total_shipping or 0
                total_products += customer_total_products
                data.append({
                    "Customer Name": customer_name,
                    "Phone Number": customer_phone_1,
                    "Email": email,
                    "Order Numbers": ", ".join(order_numbers),
                    "Order Count": order_count,
                    "Total Price": f"{customer_total_price}",
                    "Total Shipping Price": f"{customer_total_shipping}",
                    "Total order Profit": f"{(customer_total_price or 0) - (customer_total_shipping or 0)}",
                    "Total Products": f"{customer_total_products}",
                    "Avg Days to Receive": avg_days_to_receive
                })
            num_customers = len(multiple_orders)
            st.write("Customers with Multiple Orders:")
            st.dataframe(data)
            st.write(f"**Number of Customers with Multiple Orders:** {num_customers}")
            st.write(f"**Total Price:** {int(total_price):,}".replace(",", "."))
            st.write(f"**Total Shipping Price:** {int(total_shipping):,}".replace(",", "."))
            st.write(f"**Total Profit:** {int((total_price or 0)-(total_shipping or 0)):,}".replace(",", "."))
            st.write(f"**Total Products of Their Orders:** {total_products}")
        else:
            st.write("No customers with multiple orders found.")

        conn.close()


    with tab6:
        st.header("Orders View")
        
        sort_by = st.selectbox("Sort by", ["Order Code", "Total Price"])
        sort_order = st.radio("Sort order", ["Ascending", "Descending"])
        
        conn = create_connection()
        cursor = conn.cursor()
        
        sort_column = "ARRAY_AGG(CAST(o.order_number AS INTEGER))" if sort_by == "Order Code" else "SUM(o.order_price)"
        sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
        
        query = f"""
        SELECT c.customer_name, c.customer_phone_1,c.email,
            ARRAY_AGG(o.order_number) AS order_numbers,
            COUNT(o.order_number) AS order_count,
            SUM(o.order_price) AS total_price,
            SUM(o.hoodies) AS total_product,
            SUM(o.shipping_price) AS total_shipping
        FROM customers c
        INNER JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_name, c.customer_phone_1,c.email
        ORDER BY {sort_column} {sort_direction}
        """
        
        cursor.execute(query)
        consolidated_orders = cursor.fetchall()

        total_query = """
        SELECT COUNT(o.order_number), COALESCE(SUM(o.hoodies),0),COALESCE(SUM(o.order_price), 0),COALESCE(SUM(o.shipping_price), 0)
        FROM orders o
        """
        cursor.execute(total_query)
        total_orders,total_products, total_prices, total_shipping_prices = cursor.fetchone()

        conn.close()

        if consolidated_orders:
            data = []
            for row in consolidated_orders:
                customer_name, customer_phone_1,email, order_numbers, order_count, total_price,total_product,total_shipping = row
                data.append({
                    "Customer Name": customer_name,
                    "Phone Number": customer_phone_1,
                    "Email": email,
                    "Order Numbers": ", ".join(order_numbers),
                    "Order Count": order_count,
                    "Total Price": f"{total_price}",
                    "Total Shipping Price": f"{total_shipping}",
                    "Total Order Profit": f"{(total_price or 0) - (total_shipping or 0)}",
                    "Total Products": f"{total_product}"
                })
            
            df = pd.DataFrame(data)
            st.write("Orders:")
            st.dataframe(df)
            st.write(f"**Total Orders:** {total_orders}")
            st.write(f"**Total Price:** {int(total_prices):,}".replace(",", "."))
            st.write(f"**Total Shipping:** {int(total_shipping_prices):,}".replace(",", "."))
            st.write(f"**Total Profit:** {int((total_prices or 0) - (total_shipping_prices or 0)):,}".replace(",", "."))
            st.write(f"**Total Products:** {total_products}")
            st.write("Download Data:")
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name="orders_view.csv",
                mime="text/csv"
            )
            
            excel_data = io.BytesIO()
            with pd.ExcelWriter(excel_data, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Orders View")
            excel_data.seek(0)
            st.download_button(
                label="Download as Excel",
                data=excel_data,
                file_name="orders_view.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            def generate_pdf_with_reportlab(dataframe):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))  
                
                data = [dataframe.columns.tolist()] + dataframe.values.tolist()
                
                col_widths = [
                    100,  
                    80,  
                    200, 
                    100, 
                    100,  
                    80,
                    80    
                ]
                
                table = Table(data, colWidths=col_widths)
                table.setStyle(
                    TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ])
                )
                
                elements = [table]
                doc.build(elements)
                
                buffer.seek(0)
                return buffer.read()

            pdf_data = generate_pdf_with_reportlab(df)
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="orders_view.pdf",
                mime="application/pdf"
            )
            
        else:
            st.write("No orders found.")


    with tab7:
        st.header("Delete Orders")
        
        query = """
        SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
            c.email, o.ship_company, o.region, o.order_price, o.days_to_receive, 
            o.hoodies, o.shipping_price
        FROM orders o
        INNER JOIN customers c ON o.customer_id = c.customer_id
        """
        
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            all_orders = cursor.fetchall()

        if not all_orders:
            st.write("No orders found.")
        else:
            orders_data = [
                {
                    "Order Number": int(order[0]), 
                    "Customer Name": order[1],
                    "Phone 1": order[2],
                    "Phone 2": order[3],
                    "Email": order[4],
                    "Ship Company": order[5],
                    "Region": order[6],
                    "Order Price": order[7],
                    "Days to Receive": order[8],
                    "Hoodies": order[9],
                    "Shipping Price": order[10],
                }
                for order in all_orders
            ]
            
            gb = GridOptionsBuilder.from_dataframe(pd.DataFrame(orders_data))
            gb.configure_selection("multiple", use_checkbox=True) 
            gb.configure_column("Order Number", sort="asc")  
            grid_options = gb.build()
            
            grid_response = AgGrid(
                pd.DataFrame(orders_data),
                gridOptions=grid_options,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                height=400,
                theme="streamlit",  
            )
            
            selected_rows = grid_response["selected_rows"]

            if selected_rows is None or selected_rows.empty:
                st.warning("No orders selected.")
            else:
                st.write("Selected Rows:", selected_rows)  
                if "Order Number" in selected_rows.columns:
                    selected_order_numbers = selected_rows["Order Number"].astype(str).tolist()
                else:
                    st.error("The 'Order Number' column is missing in the selected rows.")
                    selected_order_numbers = []

                if st.button("Delete Selected Orders"):
                    if not selected_order_numbers:
                        st.warning("No valid orders selected for deletion.")
                    else:
                        orders_tuple = tuple(selected_order_numbers)

                        if len(orders_tuple) == 1:
                            orders_tuple = (orders_tuple[0],)

                        delete_query = "DELETE FROM orders WHERE order_number IN %s"
                        try:
                            with create_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute(delete_query, (orders_tuple,))
                                conn.commit()
                                st.success(f"Successfully deleted {len(selected_order_numbers)} orders.")
                        except Exception as e:
                            st.error(f"Error deleting orders: {e}")


elif page == "Cancelled Orders":
    tab_1, tab_2, tab_3, tab_4 = st.tabs(["Add Order", "Search Orders", "View All Orders","Modify Orders"])
    with tab_1:
        st.header("Add Cancelled Order")
        def correct_phone_number(phone):
            if re.search(r"[^\d]", phone):
                phone = re.sub(r"[^\d]", "", phone)
                return phone, False, True
            elif not phone.startswith("01"):
                phone = "01" + phone
                return phone, False, True
            if len(phone) == 11:
                return phone, True, True
            else:
                return phone, False, False
        def correct_email(email):
            if ' ' in email:
                email = re.sub(r"\s+", "", email)
                return email, False
            else:
                return email, True

        def contains_arabic(text):
            return bool(re.search(r'[\u0600-\u06FF]', text))

        with st.form("cancelled_order_form"):
            customer_name = st.text_input("Customer Name")
            customer_phone_1 = st.text_input("Customer Phone 1")
            corrected_phone_1, is_valid_1, is_valid_11 = correct_phone_number(customer_phone_1)
            if customer_phone_1:
                if not is_valid_11:
                    st.markdown(
                        f"<div style='color: red;'>(Invalid Length): {corrected_phone_1}</div>",
                        unsafe_allow_html=True,
                    )
                elif not is_valid_1:
                    st.markdown(
                        f"<div style='color: orange;'>Corrected Phone 1 (Invalid Format): {corrected_phone_1}</div>",
                        unsafe_allow_html=True,
                    )
            customer_phone_2 = st.text_input("Customer Phone 2 (Optional)", value="")
            corrected_phone_2, is_valid_2, is_valid_22 = correct_phone_number(customer_phone_2)
            if customer_phone_2:
                if not is_valid_22:
                    st.markdown(
                        f"<div style='color: red;'>(Invalid Length): {corrected_phone_2}</div>",
                        unsafe_allow_html=True,
                    )
                elif not is_valid_2:
                    st.markdown(
                        f"<div style='color: orange;'>Corrected Phone 2 (Invalid Format): {corrected_phone_2}</div>",
                        unsafe_allow_html=True,
                    )
            email = st.text_input("Email (Optional)", value="")
            corrected_email, is_valid_email = correct_email(email)
            if email:
                if not is_valid_email:
                    st.markdown(
                        f"<div style='color: orange;'>Corrected email (Invalid Format): {corrected_email}</div>",
                        unsafe_allow_html=True,
                    )
            region = st.selectbox("Region", egypt_governorates)
            order_number = st.text_input("Order Code")
            hoodies = custom_number_input("Number Of Products", min_value=0,step=1)
            order_price=custom_number_input("Order Price",min_value=0,step=1)
            cancelled_reason=st.selectbox("Reason",reasons_1)
            submit = st.form_submit_button("Add Cancelled Order")

            if submit:
                if not customer_name.strip():
                    st.error("Customer Name is required.")
                elif contains_arabic(customer_name):
                    st.error("Customer Name cannot contain Arabic characters.")
                elif not customer_phone_1.strip():
                    st.error("Customer Phone 1 is required.")
                elif not is_valid_1:
                    st.error("Customer Phone 1 is invalid. Please correct the number.")
                elif customer_phone_2 and not is_valid_2:
                    st.error("Customer Phone 2 is invalid. Please correct the number.")
                elif email and not is_valid_email:
                    st.error("Email is invalid. Please correct the email.")
                elif contains_arabic(region):
                    st.error("Region cannot contain Arabic characters.")
                elif not region.strip():
                    st.error("Region is required.")
                elif not order_number.strip():
                    st.error("Order Number is required.")
                elif not cancelled_reason.strip():
                    st.error("Reason is required")
                elif hoodies is None or hoodies==0:
                    st.error("Number Of Products is required.")
                elif order_price is None or order_price<0:
                    st.error("Order Price is required.")
                else:
                    conn = create_connection()
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT 1 FROM cancelled_orders WHERE order_number = %s",
                        (order_number,)
                    )
                    existing_order = cursor.fetchone()

                    if existing_order:
                        st.error("Order Number already exists. Please enter a unique Order Number.")
                    else:
                        cursor.execute(
                            "SELECT customer_id FROM customers WHERE customer_phone_1 = %s",
                            (corrected_phone_1,)
                        )
                        customer = cursor.fetchone()

                        if customer:
                            customer_id = customer[0]
                        else:
                            cursor.execute(
                                "INSERT INTO customers (customer_name, customer_phone_1, customer_phone_2, email) VALUES (%s, %s, %s, %s) RETURNING customer_id",
                                (customer_name, corrected_phone_1, corrected_phone_2, corrected_email)
                            )
                            customer_id = cursor.fetchone()[0]
                        cursor.execute( """
                                            INSERT INTO cancelled_orders 
                                            (customer_id, region, order_number,reason,hoodies,order_price) 
                                            VALUES (%s, %s, %s,%s,%s,%s)
                                            """,
                                            (customer_id, region, order_number,cancelled_reason,hoodies,order_price),
                                        )
                        conn.commit()
                        st.success("Cancelled order added successfully!")

                    conn.close()
    with tab_2:
        st.header("Search Orders")
        search_option = st.radio("Search by", ("Order Code", "Customer Phone 1", "Name", "Email"))
        search_query = st.text_input("Enter Search Term")

        if search_query:
            conn = create_connection()
            cursor = conn.cursor()

            if search_option == "Order Code":
                search_condition = "o.order_number = %s"
            elif search_option == "Customer Phone 1":
                search_condition = "c.customer_phone_1 = %s"
            elif search_option == "Name":
                search_condition = "c.customer_name ILIKE %s"
                search_query = f"%{search_query}%" 
            else:
                search_condition = "c.email ILIKE %s"
                search_query = f"%{search_query}%"

            cursor.execute(
                f"""
                SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                    c.email,o.region,o.reason,o.hoodies,o.order_price
                FROM cancelled_orders o
                INNER JOIN customers c ON o.customer_id = c.customer_id
                WHERE {search_condition}
                """,
                (search_query,)
            )

            results = cursor.fetchall()

            if results:
                st.write("Search Results:")
                st.table(results)
            else:
                st.write("No orders found for the given query.")

            conn.close()
    with tab_3:
        st.header("All Orders")
        
        sort_by = st.selectbox("Sort by", ["Order Code"])
        sort_order = st.radio("Sort orders", ["Ascending", "Descending"])
        
        conn = create_connection()
        cursor = conn.cursor()
        sort_column = "CAST(o.order_number AS INTEGER)"
        sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
        
        query = f"""
        SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
            c.email,o.region,o.reason,o.hoodies,o.order_price
        FROM cancelled_orders o
        INNER JOIN customers c ON o.customer_id = c.customer_id
        """
        query += f" ORDER BY {sort_column} {sort_direction}"
        
        cursor.execute(query)
        all_orders = cursor.fetchall()
        total_query = "COALESCE(SUM(hoodies),0), COALESCE(SUM(order_price), 0) FROM orders"
        total_query = """
        SELECT COUNT(o.order_number), COALESCE(SUM(o.hoodies),0),COALESCE(SUM(o.order_price), 0)
        FROM cancelled_orders o
        """
        cursor.execute(total_query)
        total_orders,total_products, total_price = cursor.fetchone()
        conn.close()        
        if all_orders:
            data = []
            for order in all_orders:
                data.append({
                    "Order Number": order[0],
                    "Customer Name": order[1],
                    "Phone 1": order[2],
                    "Phone 2": order[3],
                    "Email": order[4],
                    "Region": order[5],
                    "Reason":order[6],
                    "Number of Hoodies":order[7],
                    "Order Price":order[8],
                })
            df = pd.DataFrame(data)
            st.write("All Orders:")
            st.dataframe(df)
            st.write(f"**Total Orders:** {total_orders}")
            st.write(f"**Total Price:** {int(total_price):,}".replace(",", "."))
            st.write(f"**Total Products:** {total_products}")           
            st.write("Download Data:")
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name="cancelled orders.csv",
                mime="text/csv"
            )
            
            excel_data = io.BytesIO()
            with pd.ExcelWriter(excel_data, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Orders")
            excel_data.seek(0)
            st.download_button(
                label="Download as Excel",
                data=excel_data,
                file_name="cancelled orders.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            def generate_pdf_with_reportlab(dataframe):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=landscape(letter)) 
                
                data = [dataframe.columns.tolist()] + dataframe.values.tolist()
                
                col_widths = [
                    70,  
                    100, 
                    80,  
                    80,  
                    180,  
                    100,
                    80,
                    80,
                    80,
                ]
                
                table = Table(data, colWidths=col_widths)
                table.setStyle(
                    TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ])
                )
                
                elements = [table]
                doc.build(elements)
                
                buffer.seek(0)
                return buffer.read()

            pdf_data = generate_pdf_with_reportlab(df)
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="cancelled orders.pdf",
                mime="application/pdf"
            )
        else:
            st.write("No orders found.")

    with tab_4:
        st.header("Update or Remove Orders")
        
        st.subheader("Select an Order")
        search_order_number = st.text_input("Enter Order Code")

        if search_order_number:
            conn = create_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2,
                    c.email, o.region,o.reason,o.hoodies,o.order_price
                FROM cancelled_orders o
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
                    new_name=st.text_input("Customer Name",value=order_details[1])
                    new_phone1=st.text_input("Customer Phone 1",value=order_details[2])
                    new_phone2=st.text_input("Customer Phone 1",value=order_details[3])
                    new_email=st.text_input("Email",value=order_details[4])
                    new_region = st.selectbox("Region",egypt_governorates,index=egypt_governorates.index(order_details[5]))
                    new_cancel_reason=st.selectbox("Reason",reasons_1)
                    new_cancel_hoodies=custom_number_input("Number Of Products",value=order_details[7])
                    new_cancel_price=custom_number_input("Order Price",value=order_details[8])
                    update_submit = st.form_submit_button("Update Order")    
                    if update_submit:
                            cursor.execute(
                                """
                                UPDATE customers
                                SET customer_name = %s, customer_phone_1 = %s, customer_phone_2 = %s, email = %s
                                WHERE customer_id = (
                                    SELECT customer_id 
                                    FROM cancelled_orders 
                                    WHERE order_number = %s
                                )
                                """,
                                (new_name, new_phone1, new_phone2, new_email, search_order_number)
                            )
                            
                            cursor.execute(
                                """
                                UPDATE cancelled_orders
                                SET region = %s,reason=%s,hoodies=%s,order_price=%s
                                WHERE order_number = %s
                                """,
                                (new_region, new_cancel_reason, new_cancel_hoodies, new_cancel_price, search_order_number)
                            )

                            conn.commit()
                            st.success("Order updated successfully!")

                st.subheader("Remove Order")
                with st.form("delete_order_form"):
                    delete_password = st.text_input("Enter Password to Confirm Deletion", type="password")
                    delete_submit = st.form_submit_button("Delete Order")

                    if delete_submit:
                        if delete_password == "admin":
                            cursor.execute(
                                "DELETE FROM cancelled_orders WHERE order_number = %s", (search_order_number,)
                            )
                            conn.commit()
                            st.success("Order deleted successfully!")
                        else:
                            st.error("Incorrect password. Order deletion canceled.")
            else:
                st.write("No order found with the given Order Number.")
            
            conn.close()
elif page == "Returned Orders":
    tab_1, tab_2, tab_3, tab_4 = st.tabs(["Add Order", "Search Orders", "View All Orders","Modify Orders"])
    with tab_1:
        st.header("Add Returned Order")
        def correct_phone_number(phone):
            if re.search(r"[^\d]", phone):
                phone = re.sub(r"[^\d]", "", phone)
                return phone, False, True
            elif not phone.startswith("01"):
                phone = "01" + phone
                return phone, False, True
            if len(phone) == 11:
                return phone, True, True
            else:
                return phone, False, False
        def correct_email(email):
            if ' ' in email:
                email = re.sub(r"\s+", "", email)
                return email, False
            else:
                return email, True

        def contains_arabic(text):
            return bool(re.search(r'[\u0600-\u06FF]', text))

        with st.form("returned_order_form"):
            customer_name = st.text_input("Customer Name")
            customer_phone_1 = st.text_input("Customer Phone 1")
            corrected_phone_1, is_valid_1, is_valid_11 = correct_phone_number(customer_phone_1)
            if customer_phone_1:
                if not is_valid_11:
                    st.markdown(
                        f"<div style='color: red;'>(Invalid Length): {corrected_phone_1}</div>",
                        unsafe_allow_html=True,
                    )
                elif not is_valid_1:
                    st.markdown(
                        f"<div style='color: orange;'>Corrected Phone 1 (Invalid Format): {corrected_phone_1}</div>",
                        unsafe_allow_html=True,
                    )
            customer_phone_2 = st.text_input("Customer Phone 2 (Optional)", value="")
            corrected_phone_2, is_valid_2, is_valid_22 = correct_phone_number(customer_phone_2)
            if customer_phone_2:
                if not is_valid_22:
                    st.markdown(
                        f"<div style='color: red;'>(Invalid Length): {corrected_phone_2}</div>",
                        unsafe_allow_html=True,
                    )
                elif not is_valid_2:
                    st.markdown(
                        f"<div style='color: orange;'>Corrected Phone 2 (Invalid Format): {corrected_phone_2}</div>",
                        unsafe_allow_html=True,
                    )
            email = st.text_input("Email (Optional)", value="")
            corrected_email, is_valid_email = correct_email(email)
            if email:
                if not is_valid_email:
                    st.markdown(
                        f"<div style='color: orange;'>Corrected email (Invalid Format): {corrected_email}</div>",
                        unsafe_allow_html=True,
                    )
            ship_company = st.text_input("Shipping Company")
            region = st.selectbox("Region", egypt_governorates)
            order_number = st.text_input("Order Code")
            reason=st.selectbox("Reason",reasons)
            hoodies = custom_number_input("Number Of Products", min_value=0,step=1)
            order_price = custom_number_input("Order Price", min_value=0,step=1)
            shipping_price = custom_number_input("Shipping Price", min_value=0,step=1)
            submit = st.form_submit_button("Add Returned Order")

            if submit:
                if not customer_name.strip():
                    st.error("Customer Name is required.")
                elif contains_arabic(customer_name):
                    st.error("Customer Name cannot contain Arabic characters.")
                elif not customer_phone_1.strip():
                    st.error("Customer Phone 1 is required.")
                elif not is_valid_1:
                    st.error("Customer Phone 1 is invalid. Please correct the number.")
                elif customer_phone_2 and not is_valid_2:
                    st.error("Customer Phone 2 is invalid. Please correct the number.")
                elif email and not is_valid_email:
                    st.error("Email is invalid. Please correct the email.")
                elif contains_arabic(ship_company):
                    st.error("Shipping Company cannot contain Arabic characters.")
                elif contains_arabic(region):
                    st.error("Region cannot contain Arabic characters.")
                elif not ship_company.strip():
                    st.error("Shipping Company is required.")
                elif not region.strip():
                    st.error("Region is required.")
                elif not order_number.strip():
                    st.error("Order Number is required.")
                elif not reason.strip():
                    st.error("Reason is required.")
                elif hoodies is None or hoodies==0:
                    st.error("Number Of Products is required.")
                elif order_price is None or order_price<0:
                    st.error("Order Price is required.")
                elif shipping_price is None or shipping_price<0:
                    st.error("Shipping Price is required.")
                else:
                    conn = create_connection()
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT 1 FROM returned_orders WHERE order_number = %s",
                        (order_number,)
                    )
                    existing_order = cursor.fetchone()

                    if existing_order:
                        st.error("Order Number already exists. Please enter a unique Order Number.")
                    else:
                        cursor.execute(
                            "SELECT customer_id FROM customers WHERE customer_phone_1 = %s",
                            (corrected_phone_1,)
                        )
                        customer = cursor.fetchone()

                        if customer:
                            customer_id = customer[0]
                        else:
                            cursor.execute(
                                "INSERT INTO customers (customer_name, customer_phone_1, customer_phone_2, email) VALUES (%s, %s, %s, %s) RETURNING customer_id",
                                (customer_name, corrected_phone_1, corrected_phone_2, corrected_email)
                            )
                            customer_id = cursor.fetchone()[0]
                        cursor.execute(
                            "INSERT INTO returned_orders (customer_id, ship_company, region, order_number,reason,hoodies,order_price,shipping_price) VALUES (%s, %s, %s, %s,%s,%s,%s,%s)",
                            (customer_id, ship_company, region, order_number,reason,hoodies,order_price,shipping_price)
                        )

                        conn.commit()
                        st.success("Returned order added successfully!")

                    conn.close()
    with tab_2:
        st.header("Search Orders")
        search_option = st.radio("Search by", ("Order Code", "Customer Phone 1", "Name", "Email"))
        search_query = st.text_input("Enter Search Term")

        if search_query:
            conn = create_connection()
            cursor = conn.cursor()

            if search_option == "Order Code":
                search_condition = "o.order_number = %s"
            elif search_option == "Customer Phone 1":
                search_condition = "c.customer_phone_1 = %s"
            elif search_option == "Name":
                search_condition = "c.customer_name ILIKE %s"
                search_query = f"%{search_query}%" 
            else:
                search_condition = "c.email ILIKE %s"
                search_query = f"%{search_query}%"

            cursor.execute(
                f"""
                SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                    c.email, o.ship_company, o.region,o.reason,o.hoodies,o.order_price,o.shipping_price
                FROM returned_orders o
                INNER JOIN customers c ON o.customer_id = c.customer_id
                WHERE {search_condition}
                """,
                (search_query,)
            )

            results = cursor.fetchall()

            if results:
                st.write("Search Results:")
                st.table(results)
            else:
                st.write("No orders found for the given query.")
            conn.close()
    with tab_3:
        st.header("All Orders")
        
        sort_by = st.selectbox("Sort by", ["Order Code"])
        sort_order = st.radio("Sort orders", ["Ascending", "Descending"])
        
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT ship_company FROM returned_orders")
        ship_companies = [row[0] for row in cursor.fetchall()]
        selected_ship_company = st.selectbox("Filter by Shipping Company", ["All"] + ship_companies)
        sort_column = "CAST(o.order_number AS INTEGER)"
        sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
        
        query = f"""
        SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
            c.email, o.ship_company, o.region, o.reason,o.hoodies,o.order_price,o.shipping_price
        FROM returned_orders o
        INNER JOIN customers c ON o.customer_id = c.customer_id
        """
        if selected_ship_company != "All":
            query += f" WHERE o.ship_company = '{selected_ship_company}'"
        
        query += f" ORDER BY {sort_column} {sort_direction}"
            
        cursor.execute(query)
        all_orders = cursor.fetchall()
        total_query = """
        SELECT COUNT(o.order_number), COALESCE(SUM(o.hoodies),0),COALESCE(SUM(o.order_price), 0),COALESCE(SUM(o.shipping_price), 0)
        FROM returned_orders o
        """
        cursor.execute(total_query)
        total_orders,total_products, total_price, total_shipping_price = cursor.fetchone()
        conn.close()
        
        if all_orders:
            data = []
            for order in all_orders:
                data.append({
                    "Order Number": order[0],
                    "Customer Name": order[1],
                    "Phone 1": order[2],
                    "Phone 2": order[3],
                    "Email": order[4],
                    "Shipping Company": order[5],
                    "Region": order[6],
                    "Reason": order[7],
                    "Number Of Products":order[8],
                    "Order Price":order[9],
                    "Shipping Price":order[10],
                    "Order Profit": (order[9] or 0) - (order[10] or 0),
                })
            df = pd.DataFrame(data)
            st.write("All Orders:")
            st.dataframe(df)
            st.write(f"**Total Orders:** {total_orders}")
            st.write(f"**Total Price:** {int(total_price):,}".replace(",", "."))
            st.write(f"**Total Shipping Price:** {int(total_shipping_price):,}".replace(",", "."))
            total_order_profit = df["Order Profit"].sum()
            st.write(f"**Total Order Profit:** {int(total_order_profit):,}".replace(",", "."))
            st.write(f"**Total Products:** {total_products}")            
            st.write("Download Data:")
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name="cancelled orders.csv",
                mime="text/csv"
            )
            
            excel_data = io.BytesIO()
            with pd.ExcelWriter(excel_data, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Orders")
            excel_data.seek(0)
            st.download_button(
                label="Download as Excel",
                data=excel_data,
                file_name="cancelled orders.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            def generate_pdf_with_reportlab(dataframe):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=landscape(letter)) 
                
                data = [dataframe.columns.tolist()] + dataframe.values.tolist()
                
                col_widths = [
                    70,  
                    100, 
                    80,  
                    80,  
                    180,  
                    100,  
                    100,  
                    30,
                    30,
                    30,
                    30,
                ]
                
                table = Table(data, colWidths=col_widths)
                table.setStyle(
                    TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ])
                )
                
                elements = [table]
                doc.build(elements)
                
                buffer.seek(0)
                return buffer.read()

            pdf_data = generate_pdf_with_reportlab(df)
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="returned orders.pdf",
                mime="application/pdf"
            )
        else:
            st.write("No orders found.")

    with tab_4:
        st.header("Update or Remove Orders")
        
        st.subheader("Select an Order")
        search_order_number = st.text_input("Enter Order Code")

        if search_order_number:
            conn = create_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2,
                    c.email, o.ship_company, o.region,o.reason,o.hoodies,o.order_price,o.shipping_price
                FROM returned_orders o
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
                    new_name=st.text_input("Customer Name",value=order_details[1])
                    new_phone1=st.text_input("Customer Phone 1",value=order_details[2])
                    new_phone2=st.text_input("Customer Phone 1",value=order_details[3])
                    new_email=st.text_input("Email",value=order_details[4])
                    new_ship_company = st.text_input("Shipping Company", value=order_details[5])
                    new_region = st.selectbox("Region",egypt_governorates,index=egypt_governorates.index(order_details[6]))
                    new_reason = st.selectbox("Reason",reasons)
                    new_number_of_hoodies=custom_number_input("Number Of Products",value=order_details[8])
                    new_price=custom_number_input("Order Price",value=order_details[9])
                    new_shipping_price=custom_number_input("Shipping Price",value=order_details[10])
                    update_submit = st.form_submit_button("Update Order")    
                    if update_submit:
                            cursor.execute(
                                """
                                UPDATE customers
                                SET customer_name = %s, customer_phone_1 = %s, customer_phone_2 = %s, email = %s
                                WHERE customer_id = (
                                    SELECT customer_id 
                                    FROM returned_orders 
                                    WHERE order_number = %s
                                )
                                """,
                                (new_name, new_phone1, new_phone2, new_email, search_order_number)
                            )
                            
                            cursor.execute(
                                """
                                UPDATE returned_orders
                                SET ship_company = %s, region = %s,reason=%s,hoodies=%s,order_price=%s,shipping_price=%s
                                WHERE order_number = %s
                                """,
                                (new_ship_company, new_region, new_reason, new_number_of_hoodies, new_price, new_shipping_price, search_order_number)
                            )

                            conn.commit()
                            st.success("Order updated successfully!")

                st.subheader("Remove Order")
                with st.form("delete_order_form"):
                    delete_password = st.text_input("Enter Password to Confirm Deletion", type="password")
                    delete_submit = st.form_submit_button("Delete Order")

                    if delete_submit:
                        if delete_password == "admin":
                            cursor.execute(
                                "DELETE FROM returned_orders WHERE order_number = %s", (search_order_number,)
                            )
                            conn.commit()
                            st.success("Order deleted successfully!")
                        else:
                            st.error("Incorrect password. Order deletion canceled.")
            else:
                st.write("No order found with the given Order Number.")
            
            conn.close()

elif page == "Shipping Problems":
    tab_1, tab_2, tab_3, tab_4 = st.tabs(["Add Order", "Search Orders", "View All Orders","Modify Orders"])
    with tab_1:
        st.header("Add Order")
        def correct_phone_number(phone):
            if re.search(r"[^\d]", phone):
                phone = re.sub(r"[^\d]", "", phone)
                return phone, False, True
            elif not phone.startswith("01"):
                phone = "01" + phone
                return phone, False, True
            if len(phone) == 11:
                return phone, True, True
            else:
                return phone, False, False
        def correct_email(email):
            if ' ' in email:
                email = re.sub(r"\s+", "", email)
                return email, False
            else:
                return email, True

        def contains_arabic(text):
            return bool(re.search(r'[\u0600-\u06FF]', text))

        with st.form("returned_order_form"):
            customer_name = st.text_input("Customer Name")
            customer_phone_1 = st.text_input("Customer Phone 1")
            corrected_phone_1, is_valid_1, is_valid_11 = correct_phone_number(customer_phone_1)
            if customer_phone_1:
                if not is_valid_11:
                    st.markdown(
                        f"<div style='color: red;'>(Invalid Length): {corrected_phone_1}</div>",
                        unsafe_allow_html=True,
                    )
                elif not is_valid_1:
                    st.markdown(
                        f"<div style='color: orange;'>Corrected Phone 1 (Invalid Format): {corrected_phone_1}</div>",
                        unsafe_allow_html=True,
                    )
            customer_phone_2 = st.text_input("Customer Phone 2 (Optional)", value="")
            corrected_phone_2, is_valid_2, is_valid_22 = correct_phone_number(customer_phone_2)
            if customer_phone_2:
                if not is_valid_22:
                    st.markdown(
                        f"<div style='color: red;'>(Invalid Length): {corrected_phone_2}</div>",
                        unsafe_allow_html=True,
                    )
                elif not is_valid_2:
                    st.markdown(
                        f"<div style='color: orange;'>Corrected Phone 2 (Invalid Format): {corrected_phone_2}</div>",
                        unsafe_allow_html=True,
                    )
            email = st.text_input("Email (Optional)", value="")
            corrected_email, is_valid_email = correct_email(email)
            if email:
                if not is_valid_email:
                    st.markdown(
                        f"<div style='color: orange;'>Corrected email (Invalid Format): {corrected_email}</div>",
                        unsafe_allow_html=True,
                    )
            ship_company = st.text_input("Shipping Company")
            region = st.selectbox("Region", egypt_governorates)
            order_number = st.text_input("Order Code")
            status=st.selectbox("Status",Status)
            hoodies = custom_number_input("Number Of Products", min_value=0,step=1)
            problem_reason=st.selectbox("Reason",reasons_2)
            shipping_price = custom_number_input("Shipping Price", min_value=0,step=1)
            submit = st.form_submit_button("Add Order")

            if submit:
                if not customer_name.strip():
                    st.error("Customer Name is required.")
                elif contains_arabic(customer_name):
                    st.error("Customer Name cannot contain Arabic characters.")
                elif not customer_phone_1.strip():
                    st.error("Customer Phone 1 is required.")
                elif not is_valid_1:
                    st.error("Customer Phone 1 is invalid. Please correct the number.")
                elif customer_phone_2 and not is_valid_2:
                    st.error("Customer Phone 2 is invalid. Please correct the number.")
                elif email and not is_valid_email:
                    st.error("Email is invalid. Please correct the email.")
                elif contains_arabic(ship_company):
                    st.error("Shipping Company cannot contain Arabic characters.")
                elif contains_arabic(region):
                    st.error("Region cannot contain Arabic characters.")
                elif not ship_company.strip():
                    st.error("Shipping Company is required.")
                elif not region.strip():
                    st.error("Region is required.")
                elif not order_number.strip():
                    st.error("Order Number is required.")
                elif not status.strip():
                    st.error("Status is required.")
                elif shipping_price is None or shipping_price<0:
                    st.error("Order Price is required.")
                elif hoodies is None or hoodies==0:
                    st.error("Number Of Products is required.")
                elif not problem_reason.strip():
                    st.error('Reason is required')
                else:
                    conn = create_connection()
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT 1 FROM shipping WHERE order_number = %s",
                        (order_number,)
                    )
                    existing_order = cursor.fetchone()

                    if existing_order:
                        st.error("Order Number already exists. Please enter a unique Order Number.")
                    else:
                        cursor.execute(
                            "SELECT customer_id FROM customers WHERE customer_phone_1 = %s",
                            (corrected_phone_1,)
                        )
                        customer = cursor.fetchone()

                        if customer:
                            customer_id = customer[0]
                        else:
                            cursor.execute(
                                "INSERT INTO customers (customer_name, customer_phone_1, customer_phone_2, email) VALUES (%s, %s, %s, %s) RETURNING customer_id",
                                (customer_name, corrected_phone_1, corrected_phone_2, corrected_email)
                            )
                            customer_id = cursor.fetchone()[0]
                        cursor.execute(
                            "INSERT INTO shipping (customer_id, ship_company, region, order_number,status,shipping_price,reason,hoodies) VALUES (%s, %s, %s, %s,%s,%s,%s,%s)",
                            (customer_id, ship_company, region, order_number,status,shipping_price,problem_reason,hoodies)
                        )

                        conn.commit()
                        st.success("order added successfully!")

                    conn.close()
    with tab_2:
        st.header("Search Orders")
        search_option = st.radio("Search by", ("Order Code", "Customer Phone 1", "Name", "Email"))
        search_query = st.text_input("Enter Search Term")

        if search_query:
            conn = create_connection()
            cursor = conn.cursor()

            if search_option == "Order Code":
                search_condition = "o.order_number = %s"
            elif search_option == "Customer Phone 1":
                search_condition = "c.customer_phone_1 = %s"
            elif search_option == "Name":
                search_condition = "c.customer_name ILIKE %s"
                search_query = f"%{search_query}%" 
            else:
                search_condition = "c.email ILIKE %s"
                search_query = f"%{search_query}%"

            cursor.execute(
                f"""
                SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                    c.email, o.ship_company, o.region,o.status,o.shipping_price,o.hoodies,o.reason
                FROM shipping o
                INNER JOIN customers c ON o.customer_id = c.customer_id
                WHERE {search_condition}
                """,
                (search_query,)
            )

            results = cursor.fetchall()

            if results:
                st.write("Search Results:")
                st.table(results)
            else:
                st.write("No orders found for the given query.")
            conn.close()
    with tab_3:
        st.header("All Orders")
        
        sort_by = st.selectbox("Sort by", ["Order Code"])
        sort_order = st.radio("Sort orders", ["Ascending", "Descending"])
        
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT ship_company FROM shipping")
        ship_companies = [row[0] for row in cursor.fetchall()]
        selected_ship_company = st.selectbox("Filter by Shipping Company", ["All"] + ship_companies)
        sort_column = "CAST(o.order_number AS INTEGER)"
        sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
        
        query = f"""
        SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
            c.email, o.ship_company, o.region, o.status,o.shipping_price,o.hoodies,o.reason
        FROM shipping o
        INNER JOIN customers c ON o.customer_id = c.customer_id
        """
        if selected_ship_company != "All":
            query += f" WHERE o.ship_company = '{selected_ship_company}'"
        
        query += f" ORDER BY {sort_column} {sort_direction}"
            
        cursor.execute(query)
        all_orders = cursor.fetchall()
        total_query = """
        SELECT COUNT(o.order_number), COALESCE(SUM(o.hoodies),0),COALESCE(SUM(o.shipping_price), 0)
        FROM shipping o
        """
        cursor.execute(total_query)
        total_orders,total_products, total_price = cursor.fetchone()
        conn.close()
        
        if all_orders:
            data = []
            for order in all_orders:
                data.append({
                    "Order Number": order[0],
                    "Customer Name": order[1],
                    "Phone 1": order[2],
                    "Phone 2": order[3],
                    "Email": order[4],
                    "Shipping Company": order[5],
                    "Region": order[6],
                    "Status": order[7],
                    "Reason":order[10],
                    "Shipping Price":order[8],
                    "Number of Products":order[9]
                })
            df = pd.DataFrame(data)
            st.write("All Orders:")
            st.dataframe(df)
            st.write(f"**Total Orders:** {total_orders}")
            st.write(f"**Total Shipping Price:** {int(total_price):,}".replace(",", "."))
            st.write(f"**Total Products:** {total_products}")       
            st.write("Download Data:")
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name="orders.csv",
                mime="text/csv"
            )
            
            excel_data = io.BytesIO()
            with pd.ExcelWriter(excel_data, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Orders")
            excel_data.seek(0)
            st.download_button(
                label="Download as Excel",
                data=excel_data,
                file_name="orders.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            def generate_pdf_with_reportlab(dataframe):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=landscape(letter)) 
                
                data = [dataframe.columns.tolist()] + dataframe.values.tolist()
                
                col_widths = [
                    70,  
                    100, 
                    80,  
                    80,  
                    180,  
                    100,  
                    100,  
                    30,
                    30,
                    30,
                ]
                
                table = Table(data, colWidths=col_widths)
                table.setStyle(
                    TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ])
                )
                
                elements = [table]
                doc.build(elements)
                
                buffer.seek(0)
                return buffer.read()

            pdf_data = generate_pdf_with_reportlab(df)
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="orders.pdf",
                mime="application/pdf"
            )
        else:
            st.write("No orders found.")

    with tab_4:
        st.header("Update or Remove Orders")
        
        st.subheader("Select an Order")
        search_order_number = st.text_input("Enter Order Code")

        if search_order_number:
            conn = create_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2,
                    c.email, o.ship_company, o.region,o.status,o.shipping_price,o.hoodies,o.reason
                FROM shipping o
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
                    new_name=st.text_input("Customer Name",value=order_details[1])
                    new_phone1=st.text_input("Customer Phone 1",value=order_details[2])
                    new_phone2=st.text_input("Customer Phone 1",value=order_details[3])
                    new_email=st.text_input("Email",value=order_details[4])
                    new_ship_company = st.text_input("Shipping Company", value=order_details[5])
                    new_region = st.selectbox("Region",egypt_governorates,index=egypt_governorates.index(order_details[6]))
                    new_status = st.selectbox("Status",Status)
                    new_price=custom_number_input("Shipping Price",value=order_details[8])
                    new_produtcs=custom_number_input("Number Of Products",value=order_details[9])
                    new_problem_reason= st.selectbox("Reason",reasons_2)
                    update_submit = st.form_submit_button("Update Order")    
                    if update_submit:
                            cursor.execute(
                                """
                                UPDATE customers
                                SET customer_name = %s, customer_phone_1 = %s, customer_phone_2 = %s, email = %s
                                WHERE customer_id = (
                                    SELECT customer_id 
                                    FROM shipping
                                    WHERE order_number = %s
                                )
                                """,
                                (new_name, new_phone1, new_phone2, new_email, search_order_number)
                            )
                            
                            cursor.execute(
                                """
                                UPDATE shipping
                                SET ship_company = %s, region = %s,status=%s,shipping_price=%s,hoodies=%s,reason=%s
                                WHERE order_number = %s
                                """,
                                (new_ship_company, new_region, new_status,new_price, new_produtcs, new_problem_reason, search_order_number)
                            )

                            conn.commit()
                            st.success("Order updated successfully!")

                st.subheader("Remove Order")
                with st.form("delete_order_form"):
                    delete_password = st.text_input("Enter Password to Confirm Deletion", type="password")
                    delete_submit = st.form_submit_button("Delete Order")

                    if delete_submit:
                        if delete_password == "admin":
                            cursor.execute(
                                "DELETE FROM shipping WHERE order_number = %s", (search_order_number,)
                            )
                            conn.commit()
                            st.success("Order deleted successfully!")
                        else:
                            st.error("Incorrect password. Order deletion canceled.")
            else:
                st.write("No order found with the given Order Number.")
            
            conn.close()
