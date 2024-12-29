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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Add Order", "Search Orders", "View All Orders","Modify Orders","Customers with Multiple Orders","Orders View"])

with tab1:
    st.header("Add New Order")
    with st.form("order_form"):
        customer_name = st.text_input("Customer Name")
        customer_phone_1 = st.text_input("Customer Phone 1")
        customer_phone_2 = st.text_input("Customer Phone 2 (Optional)", value="")
        email = st.text_input("Email (Optional)", value="")
        ship_company = st.text_input("Shipping Company")
        region = st.text_input("Region")
        order_number = st.text_input("Order Number")
        order_price = st.number_input("Order Price", min_value=0.0, step=0.01)
        submit = st.form_submit_button("Add Order")

        if submit:
            if not customer_name.strip():
                st.error("Customer Name is required.")
            elif not customer_phone_1.strip():
                st.error("Customer Phone 1 is required.")
            elif not ship_company.strip():
                st.error("Shipping Company is required.")
            elif not region.strip():
                st.error("Region is required.")
            elif not order_number.strip():
                st.error("Order Number is required.")
            else:
                if any(
                    bool(re.search(r'[\u0600-\u06FF]', field))
                    for field in [customer_name, ship_company, region]
                ):
                    st.error("Arabic characters are not allowed in Customer Name, Shipping Company, or Region.")
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
                            "INSERT INTO orders (customer_id, ship_company, region, order_price, order_number) VALUES (%s, %s, %s, %s, %s)",
                            (customer_id, ship_company, region, order_price, order_number)
                        )

                        conn.commit()
                        st.success("Order added successfully!")
                    
                    conn.close()


with tab2:
    st.header("Search Orders")
    search_option = st.radio("Search by", ("Customer Phone 1", "Name", "Email"))
    search_query = st.text_input("Enter Search Term")

    if search_query:
        conn = create_connection()
        cursor = conn.cursor()

        if search_option == "Customer Phone 1":
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
    
    sort_by = st.selectbox("Sort by", ["Order Number", "Order Price"])
    sort_order = st.radio("Sort orders", ["Ascending", "Descending"])
    
    conn = create_connection()
    cursor = conn.cursor()

    sort_column = "o.order_number" if sort_by == "Order Number" else "o.order_price"
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
                    self.set_font("Arial", size=14, style="B")
                    self.cell(0, 10, "Order Data", border=False, ln=True, align="C")
                    self.ln(10)
        
                def cell_with_wrapping(self, width, height, text, border, align):
                    # Wrap text if it's too long for the cell
                    if len(text) > width / 3:  # Adjust factor based on font size
                        words = text.split(" ")
                        wrapped_text = ""
                        line = ""
                        for word in words:
                            if self.get_string_width(line + word + " ") < width:
                                line += word + " "
                            else:
                                wrapped_text += line + "\n"
                                line = word + " "
                        wrapped_text += line
                        self.multi_cell(width, height, wrapped_text, border=border, align=align)
                    else:
                        self.cell(width, height, text, border=border, align=align)
        
            pdf = PDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=10)
        
            # Calculate dynamic column widths based on max content length
            col_widths = [
                max(pdf.get_string_width(str(val)) for val in [col] + dataframe[col].astype(str).tolist()) + 10
                for col in dataframe.columns
            ]
        
            total_width = sum(col_widths)
            page_width = 190  # Page width excluding margins
            scaling_factor = page_width / total_width if total_width > page_width else 1
            col_widths = [width * scaling_factor for width in col_widths]
        
            # Header row
            for i, col in enumerate(dataframe.columns):
                pdf.cell(col_widths[i], 10, col, border=1, align="C")
            pdf.ln()
        
            # Data rows
            for _, row in dataframe.iterrows():
                for i, cell in enumerate(row):
                    cell_text = str(cell) if cell else "-"
                    pdf.cell_with_wrapping(col_widths[i], 10, cell_text, border=1, align="C")
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
    
    sort_by = st.selectbox("Sort by", ["Order Number", "Total Price"])
    sort_order = st.radio("Sort order", ["Ascending", "Descending"])
    
    conn = create_connection()
    cursor = conn.cursor()
    
    sort_column = "ARRAY_AGG(o.order_number)" if sort_by == "Order Number" else "SUM(o.order_price)"
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
        
        st.write("Orders:")
        st.dataframe(data)
    else:
        st.write("No orders found.")
