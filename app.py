import streamlit as st
import psycopg2
import re
import pandas as pd
import io
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
st.sidebar.title("Order Type")
page = st.sidebar.radio("Select a page", ["Completed Orders", "Cancelled Orders"])
egypt_governorates = [
        "Cairo", "Alexandria", "Giza", "Dakahlia", "Red Sea", "Beheira",
        "Fayoum", "Gharbia", "Ismailia", "Menofia", "Minya", "Qaliubiya",
        "New Valley", "Suez", "Aswan", "Assiut", "Beni Suef", "Port Said",
        "Damietta", "Sharkia", "South Sinai", "Kafr El Sheikh", "Matruh",
        "Luxor", "Qena", "North Sinai", "Sohag"
    ]
if page == "Completed Orders":
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Add Order", "Search Orders", "View All Orders","Modify Orders","Customers with Multiple Orders","Orders View"])
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
            order_price = st.number_input("Order Price", min_value=0.0, step=0.01)
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
                            "INSERT INTO orders (customer_id, ship_company, region, order_price, order_number) VALUES (%s, %s, %s, %s, %s)",
                            (customer_id, ship_company, region, order_price, order_number)
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
                    c.email, o.ship_company, o.region, o.order_price
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
                st.write(f"Total Amount Spent: ${total_price:.2f}")
            else:
                st.write("No orders found for the given query.")

            conn.close()
            
    with tab3:
        st.header("All Orders")
        
        sort_by = st.selectbox("Sort by", ["Order Code", "Order Price"])
        sort_order = st.radio("Sort orders", ["Ascending", "Descending"])
        
        conn = create_connection()
        cursor = conn.cursor()

        sort_column = "o.order_number" if sort_by == "Order Code" else "o.order_price"
        sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
        
        query = f"""
        SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
            c.email, o.ship_company, o.region, o.order_price
        FROM orders o
        INNER JOIN customers c ON o.customer_id = c.customer_id
        ORDER BY {sort_column} {sort_direction}
        """
        cursor.execute(query)
        all_orders = cursor.fetchall()
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
                    "Order Price": f"${order[7]:.2f}"
                })
            df = pd.DataFrame(data)
            st.write("All Orders:")
            st.dataframe(df)
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
            
            def generate_pdf(dataframe):
                from fpdf import FPDF
            
                class PDF(FPDF):
                    def header(self):
                        self.set_font("Arial", style="B", size=10)  
                        self.cell(0, 8, "Order Data", border=False, ln=True, align="C")
                        self.ln(6)
            
                pdf = PDF()
                pdf.set_auto_page_break(auto=True, margin=10)  
                pdf.add_page()
            
                pdf.set_font("Arial", size=8)
            
                total_width = 150  
                min_col_width = 20 
                max_col_width = 50  
                max_widths = dataframe.applymap(lambda x: len(str(x))).max().values
                total_max_width = sum(max_widths)
                col_widths = [
                    max(min_col_width, min(max_col_width, (max_width / total_max_width) * total_width))
                    for max_width in max_widths
                ]
            
                pdf.set_font("Arial", style="B", size=8)
                for i, col in enumerate(dataframe.columns):
                    pdf.cell(col_widths[i], 8, str(col), border=1, align="C") 
                pdf.ln()
            
                pdf.set_font("Arial", size=7)  
                for _, row in dataframe.iterrows():
                    for i, cell in enumerate(row):
                        cell_text = str(cell) if pd.notnull(cell) else "N/A"
                        if len(cell_text) > 15:
                            cell_text = cell_text[:12] + "..."
                        pdf.cell(col_widths[i], 8, cell_text, border=1, align="C")  
                    pdf.ln()
            
                return pdf.output(dest="S").encode("latin1")

            pdf_data = generate_pdf(df)
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
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT c.customer_name, c.customer_phone_1, 
                ARRAY_AGG(o.order_number) AS order_numbers,
                COUNT(o.order_number) AS order_count,
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
                customer_name, customer_phone_1, order_numbers, order_count, total_price = row
                data.append({
                    "Customer Name": customer_name,
                    "Phone Number": customer_phone_1,
                    "Order Numbers": ", ".join(order_numbers),
                    "Order Count": order_count,
                    "Total Price": f"${total_price:.2f}"
                })

            st.write("Customers with Multiple Orders:")
            st.dataframe(data)
        else:
            st.write("No customers with multiple orders found.")

        conn.close()
    with tab6:
        st.header("Orders View")
        
        sort_by = st.selectbox("Sort by", ["Order Code", "Total Price"])
        sort_order = st.radio("Sort order", ["Ascending", "Descending"])
        
        conn = create_connection()
        cursor = conn.cursor()
        
        sort_column = "ARRAY_AGG(o.order_number)" if sort_by == "Order Code" else "SUM(o.order_price)"
        sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
        
        query = f"""
        SELECT c.customer_name, c.customer_phone_1, 
            ARRAY_AGG(o.order_number) AS order_numbers,
            COUNT(o.order_number) AS order_count,
            SUM(o.order_price) AS total_price
        FROM customers c
        INNER JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_name, c.customer_phone_1
        ORDER BY {sort_column} {sort_direction}
        """
        
        cursor.execute(query)
        consolidated_orders = cursor.fetchall()
        conn.close()
        
        if consolidated_orders:
            data = []
            for row in consolidated_orders:
                customer_name, customer_phone_1, order_numbers, order_count, total_price = row
                data.append({
                    "Customer Name": customer_name,
                    "Phone Number": customer_phone_1,
                    "Order Numbers": ", ".join(order_numbers),
                    "Order Count": order_count,
                    "Total Price": f"${total_price:.2f}"
                })
            
            df = pd.DataFrame(data)
            st.write("Orders:")
            st.dataframe(df)
            
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
            
            def generate_pdf(dataframe):
                from fpdf import FPDF
            
                class PDF(FPDF):
                    def header(self):
                        self.set_font("Arial", style="B", size=10)  
                        self.cell(0, 8, "Orders View Data", border=False, ln=True, align="C")
                        self.ln(6)
            
                pdf = PDF()
                pdf.set_auto_page_break(auto=True, margin=10)  
                pdf.add_page()
            
                pdf.set_font("Arial", size=8)
            
                total_width = 150  
                min_col_width = 20 
                max_col_width = 50  
                max_widths = dataframe.applymap(lambda x: len(str(x))).max().values
                total_max_width = sum(max_widths)
                col_widths = [
                    max(min_col_width, min(max_col_width, (max_width / total_max_width) * total_width))
                    for max_width in max_widths
                ]
            
                pdf.set_font("Arial", style="B", size=8)
                for i, col in enumerate(dataframe.columns):
                    pdf.cell(col_widths[i], 8, str(col), border=1, align="C") 
                pdf.ln()
            
                pdf.set_font("Arial", size=7)  
                for _, row in dataframe.iterrows():
                    for i, cell in enumerate(row):
                        cell_text = str(cell) if pd.notnull(cell) else "N/A"
                        if len(cell_text) > 15:
                            cell_text = cell_text[:12] + "..."
                        pdf.cell(col_widths[i], 8, cell_text, border=1, align="C")  
                    pdf.ln()
            
                return pdf.output(dest="S").encode("latin1")

            pdf_data = generate_pdf(df)
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="orders_view.pdf",
                mime="application/pdf"
            )
        else:
            st.write("No orders found.")

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
            ship_company = st.text_input("Shipping Company")
            region = st.selectbox("Region", egypt_governorates)
            order_number = st.text_input("Order Code")

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
                        cursor.execute(
                            "INSERT INTO cancelled_orders (customer_id, ship_company, region, order_number) VALUES (%s, %s, %s, %s)",
                            (customer_id, ship_company, region, order_number)
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
                    c.email, o.ship_company, o.region
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

        sort_column = "o.order_number"
        sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
        
        query = f"""
        SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
            c.email, o.ship_company, o.region
        FROM cancelled_orders o
        INNER JOIN customers c ON o.customer_id = c.customer_id
        ORDER BY {sort_column} {sort_direction}
        """
        cursor.execute(query)
        all_orders = cursor.fetchall()
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
                })
            df = pd.DataFrame(data)
            st.write("All Orders:")
            st.dataframe(df)
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
            
            def generate_pdf(dataframe):
                from fpdf import FPDF
            
                class PDF(FPDF):
                    def header(self):
                        self.set_font("Arial", style="B", size=10)  
                        self.cell(0, 8, "Order Data", border=False, ln=True, align="C")
                        self.ln(6)
            
                pdf = PDF()
                pdf.set_auto_page_break(auto=True, margin=10)  
                pdf.add_page()
            
                pdf.set_font("Arial", size=8)
            
                total_width = 150  
                min_col_width = 20 
                max_col_width = 50  
                max_widths = dataframe.applymap(lambda x: len(str(x))).max().values
                total_max_width = sum(max_widths)
                col_widths = [
                    max(min_col_width, min(max_col_width, (max_width / total_max_width) * total_width))
                    for max_width in max_widths
                ]
            
                pdf.set_font("Arial", style="B", size=8)
                for i, col in enumerate(dataframe.columns):
                    pdf.cell(col_widths[i], 8, str(col), border=1, align="C") 
                pdf.ln()
            
                pdf.set_font("Arial", size=7)  
                for _, row in dataframe.iterrows():
                    for i, cell in enumerate(row):
                        cell_text = str(cell) if pd.notnull(cell) else "N/A"
                        if len(cell_text) > 15:
                            cell_text = cell_text[:12] + "..."
                        pdf.cell(col_widths[i], 8, cell_text, border=1, align="C")  
                    pdf.ln()
            
                return pdf.output(dest="S").encode("latin1")

            pdf_data = generate_pdf(df)
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
                    c.email, o.ship_company, o.region
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
                    new_ship_company = st.text_input("Shipping Company", value=order_details[5])
                    new_region = st.text_input("Region", value=order_details[6])
                    update_submit = st.form_submit_button("Update Order")

                    if update_submit:
                        cursor.execute(
                            """
                            UPDATE cancelled_orders
                            SET ship_company = %s, region = %s
                            WHERE order_number = %s
                            """,
                            (new_ship_company, new_region, search_order_number)
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
