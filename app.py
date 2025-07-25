import streamlit as st
import psycopg2
import re
import pandas as pd
import io
import pytz
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from streamlit_option_menu import option_menu
import streamlit_shadcn_ui as ui
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import requests
from dateutil.parser import parse
db_host = st.secrets["database"]["host"]
db_user = st.secrets["database"]["user"]
db_password = st.secrets["database"]["password"]
db_name = st.secrets["database"]["database"]
SHOP_NAME = 'e6rs1y-km'
ACCESS_TOKEN = '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'

def create_connection():
    return psycopg2.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        dbname=db_name,
        port=23208 
    )

if "logged_in" in st.session_state and st.session_state.logged_in:
    st.set_page_config(page_title="Orders System", layout='wide')
    st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
    )   
else:
    st.set_page_config(page_title="Login")
    st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
    )
def log_action(username, action, details=None):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activity_log (username, action, details) VALUES (%s, %s, %s)",
        (username, action, details)
    )
    conn.commit()
    cursor.close()
    conn.close()

users = {
    "walid": "12345678",
    "shams": "91011121",
    "ahmed":"998",
    "heba":"56781234"
}

def login_page():
    col1, col2, col3 = st.columns([1, 1.6, 1.2])  
    with col2:
        st.markdown("") 
        st.markdown("") 
        st.markdown("") 
        st.markdown("") 
        st.markdown("") 
        st.image(r"logo.png", width=350)
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    with st.form('loginform'):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit=st.form_submit_button("Login")
        if submit:
            if username in users and users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.selected_season = None 
                log_action(username, "Login", "Successful login")
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
def season_selection_page():
    st.markdown("<h1 style='text-align: center; color:white; margin-top: -60px; '>🌍 Seasons</h1>", unsafe_allow_html=True)
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h1 style='text-align: center; color:rgb(5, 150, 254); margin-top: 50px; '>❄️ Winter Season</h1>", unsafe_allow_html=True)
        st.markdown("")

        if st.button("Select Winter", key="winter", use_container_width=True):
            st.session_state.selected_season = "Winter"
            st.rerun()
        new_season=st.text_input("New Season Name")
        st.button("Add Season")
    with col2:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: 50px; '>🌳 Summer Season</h1>", unsafe_allow_html=True)
        st.markdown("")
        if st.button("Select Summer", key="summer", use_container_width=True):
            st.session_state.selected_season = "Summer"
            st.rerun()
def season_selection_page_1():
    st.markdown("<h1 style='text-align: center; color:white; margin-top: -60px; '>🌍 Seasons</h1>", unsafe_allow_html=True)
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h1 style='text-align: center; color:rgb(5, 150, 254); margin-top: 50px; '>❄️ Winter Season</h1>", unsafe_allow_html=True)
        st.markdown("")

        if st.button("Select Winter", key="winter", use_container_width=True):
            st.session_state.selected_season = "Winter"
            st.rerun()
        
    with col2:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: 50px; '>🌳 Spring Season</h1>", unsafe_allow_html=True)
        st.markdown("")
        if st.button("Select Summer", key="summer", use_container_width=True):
            st.session_state.selected_season = "Summer"
            st.rerun()    
def orders_management_page(orders,returned_orders,cancelled_orders,shipping,on_hole,customers):
    def custom_number_input(label, value=0, min_value=0, step=1,key=None):
        value = st.text_input(label, value=str(value),key=key)

        try:
            numeric_value = int(value)
            if numeric_value < min_value:
                st.error(f"Value must be at least {min_value}")
                numeric_value = min_value
        except ValueError:
            st.error("Please enter a valid integer.")
            numeric_value = value

        return numeric_value
        
    if (st.session_state.username=="walid" or st.session_state.username=="ahmed"):
        with st.sidebar:
            page=option_menu("Orders Management", ["Completed Orders", 'Cancelled Orders','Returned Orders','Problems','On Hold','Customers','Analysis','Information','Activity Logs'],icons=['check-circle', 'ban','arrow-left','exclamation-circle','exclamation-circle','people','graph-up','exclamation-circle','clock'], menu_icon="list", default_index=0)
            if st.button("Logout"):
                st.session_state.logged_in = False
                log_action(st.session_state.username, "Logout", "Successful logout")
                st.rerun()
    else:
        with st.sidebar:
            page=option_menu("Orders Management", ["Completed Orders", 'Cancelled Orders','Returned Orders','Problems','On Hold','Customers','Information'],icons=['check-circle', 'ban','arrow-left','exclamation-circle','exclamation-circle','people','exclamation-circle'], menu_icon="list", default_index=0)
            if st.button("Logout"):
                st.session_state.logged_in = False
                log_action(st.session_state.username, "Logout", "Successful logout")
                st.rerun()
 
    egypt_governorates = [
        "Cairo", "Alexandria", "Giza", "Dakahlia", "Red Sea", "Beheira",
        "Fayoum", "Gharbia", "Ismailia", "Menofia", "Minya", "Qaliubiya",
        "New Valley", "Suez", "Aswan", "Assiut", "Beni Suef", "Port Said",
        "Damietta", "Sharkia", "South Sinai", "Kafr El Sheikh", "Matruh",
        "Luxor", "Qena", "North Sinai", "Sohag", "Monufia", "Qalyubia", "Al Sharqia", "Kafr el-Sheikh",
        "New Valley", "North Sinai", "Port Said", "Qalyubia", "Qena", "Red Sea",
        "Sohag", "South Sinai", "Suez",
        "6th of October", "Al Sharqia", "Alexandria", "Aswan", "Asyut", "Beheira",
        "Beni Suef", "Cairo", "Dakahlia", "Damietta", "Faiyum", "Gharbia", "Giza",
        "Helwan", "Ismailia", "Kafr el-Sheikh", "Luxor", "Matrouh", "Minya", "Monufia"
    ]

    reasons=['Customer','Delivery Man']
    reasons_1=['Customer','Out Of Stock','Team']
    reasons_2=['Customer','Delivery Man','Team']
    Status=['Returned','Exchanged','Reshipping','Team']
    products=['Set','Dxlr T-Shirt','T-Shirt','Sweatpants','Short']
    company=['BOSTA','WALID','SALAH']
    Options= ["No", "Yes"]
    if page == 'On Hold':
        st.title("🛍 Shopify Orders Retriever")
        selected_4 = option_menu(
                menu_title=None,
                options=["Retrive Orders","View All Orders","Modify Orders"],
                icons=['cart',"list-task",'gear'],
                menu_icon="cast",
                default_index=0,
                orientation="horizontal",
                styles={
                    'container': {
                        'width': '100%',
                        'margin': '30',
                        'padding': '0',
                    }
                }
            )
        if selected_4=="Retrive Orders":
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")

            if start_date > end_date:
                st.error("Start date must be before end date.")
            else:
                if st.button("📦 Retrieve Orders"):

                    all_orders = []

                    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2024-04/orders.json?limit=250&status=any&created_at_min={start_date}T00:00:00-00:00&created_at_max={end_date}T23:59:59-00:00"

                    headers = {
                        "X-Shopify-Access-Token": ACCESS_TOKEN,
                        "Content-Type": "application/json"
                    }

                    with st.spinner("Retrieving orders..."):
                        while url:
                            response = requests.get(url, headers=headers)
                            if response.status_code != 200:
                                st.error(f"❌ Error: {response.status_code} - {response.text}")
                                break

                            data = response.json().get("orders", [])
                            for order in data:
                                order_number = order.get("order_number")
                                total_price = order.get("total_price")
                                subtotal_price = order.get("subtotal_price")
                                total_tax = order.get("total_tax")
                                total_discounts = order.get("total_discounts")
                                shipping_price = order.get("total_shipping_price_set", {}).get("shop_money", {}).get("amount", "0.00")
                                financial_status = order.get("financial_status", "N/A")

                                # Products and details
                                line_items = order.get("line_items", [])
                                products_details = []
                                for item in line_items:
                                    title = item.get("title")
                                    quantity = item.get("quantity")
                                    price = float(item.get("price", 0)) 
                                    total_discount = item.get("total_discount")
                                    line_price = item.get("line_price")
                                    details = f"{title} | Qty: {quantity} | Price: £{price} | Discount: £{total_discount} | Line Total: £{line_price}"
                                    products_details.append(details)
                                products_str = ", ".join([f"{item.get('title')}: {item.get('quantity')}" for item in line_items])
                                products_prices = ", ".join([f"{item.get('title')}: {item.get('price',0)}" for item in line_items])
                                product_count = len(line_items)
                                region = order.get("billing_address", {}).get("province", "N/A")
                                created_at_raw = order.get("created_at")
                                created_date = parse(created_at_raw).date() if created_at_raw else None

                                all_orders.append({
                                    "order_number": order_number,
                                    "Date": created_date,
                                    "Region": region,
                                    "products": products_str,
                                    "Product Count": product_count,
                                    "Product Prices": products_prices,
                                    "Subtotal": f"£{subtotal_price}",
                                    "Discounts": f"£{total_discounts}",
                                    "Shipping": int(float(shipping_price)),
                                    "Tax": f"£{total_tax}",
                                    "Total Price":total_price,
                                    "Status": financial_status,
                                })

                            # Pagination
                            link_header = response.headers.get("Link")
                            if link_header and 'rel="next"' in link_header:
                                parts = link_header.split(",")
                                next_url = [part.split(";")[0].strip("<> ") for part in parts if 'rel="next"' in part]
                                url = next_url[0] if next_url else None
                            else:
                                url = None

                    if all_orders:
                        df = pd.DataFrame(all_orders)
                        def classify_product(product_name):
                            product_name = product_name.lower()  
                            if "straight sweatpants" in product_name:
                                return "Sweatpants"
                            elif "ya zaman (black)" in product_name or "ya zaman (white)" in product_name:
                                return "Dxlr T-Shirt"
                            elif "backspace my past" in product_name or "lost my ctrl" in product_name:
                                return "T-Shirt"
                            elif "set" in product_name:
                                return "Set"
                            elif "short" in product_name:
                                return "Short"

                        def map_products_to_types(product_str):
                            products = [p.strip() for p in product_str.split(",") if p.strip()]
                            type_counts = {}

                            for prod in products:
                                prod_type = classify_product(prod)
                                type_counts[prod_type] = type_counts.get(prod_type, 0) + 1

                            return ", ".join([f"{k}:{v}" for k, v in type_counts.items()])
                        def map_product_prices_to_types(prices_str):
                            products = [p.strip() for p in prices_str.split(",") if p.strip()]
                            type_prices = {}

                            for prod in products:
                                # Split by the last colon to separate name and price
                                if ":" in prod:
                                    name_part, price_part = prod.rsplit(":", 1)
                                    prod_type = classify_product(name_part.strip())
                                    try:
                                        price = float(price_part.strip())
                                    except ValueError:
                                        price = 0.0
                                    type_prices[prod_type] = type_prices.get(prod_type, 0) + price

                            return ", ".join([f"{k}: {v:.2f}" for k, v in type_prices.items()])
                        df['Product Prices'] = df["Product Prices"].apply(map_product_prices_to_types)
                        df['products']= df["products"].apply(map_products_to_types)
                        st.dataframe(df)
                        try:
                            conn = create_connection()
                            cursor = conn.cursor()
                            for _, row in df.iterrows():
                                cursor.execute(f"SELECT 1 FROM {on_hole} WHERE order_number = %s", (str(row["order_number"]),))
                                if not cursor.fetchone():
                                    cursor.execute(f"""
                                        INSERT INTO {on_hole} (order_number, total_price, products, product_count, region, date, product_prices,Shipping)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
                                    """, (
                                        row["order_number"],
                                        float(row["Total Price"]),
                                        row["products"],
                                        row["Product Count"],
                                        row["Region"],
                                        row["Date"],
                                        row["Product Prices"],
                                        row["Shipping"],
                                    ))
                            conn.commit()
                            cursor.close()
                            conn.close()
                            st.success("✅ Orders saved to database")
                        except Exception as e:
                            st.error(f"❌ Database error: {e}")
                    else:
                        st.warning("⚠ No orders found for the selected period.")
        elif selected_4=="View All Orders":
            st.header("📋 On-Hold Orders")

            conn = create_connection()
            cursor = conn.cursor()

            try:
                    cursor.execute(f"SELECT * FROM {on_hole}")
                    data = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]

                    if data:
                        df = pd.DataFrame(data, columns=columns)
                        st.dataframe(df)
                    else:
                        st.info("No orders currently in on_hole.")

            except Exception as e:
                    st.error(f"Error retrieving data: {e}")

            finally:
                    cursor.close()
                    conn.close()
        elif selected_4=="Modify Orders":
                st.header("Update or Remove Orders")
                
                st.subheader("Select an Order")
                search_order_number = st.text_input("Enter Order Code")

                if search_order_number:
                    if "last_order_number" not in st.session_state or st.session_state.last_order_number != search_order_number:
                        if "modified_products"  in st.session_state:
                            del st.session_state.modified_products
                        if "new_products"  in st.session_state:
                            del st.session_state.new_products
                        st.session_state.last_order_number = search_order_number
                    conn = create_connection()
                    cursor = conn.cursor()             
                    cursor.execute(f"SELECT * FROM {on_hole} WHERE order_number = %s", (search_order_number,))

                    order_details = cursor.fetchone()
                    if order_details:
                        st.write("Order Details:")
                        st.table([order_details])
                        if order_details[2]:  
                          products_list = [
                            {"Type": p.split(":")[0], "Count": int(p.split(":")[1])}
                            for p in order_details[2].split(", ") if ":" in p
                          ]
                        else:
                          products_list = [] 

                        st.subheader("Update Order")
                        product_prices=order_details[6]
                        new_order_number=st.text_input("Order Number",value=order_details[0])
                        new_name=st.text_input("Customer Name")
                        new_phone1=st.text_input("Customer Phone 1")
                        new_phone2=st.text_input("Customer Phone 2")
                        new_email=st.text_input("Email")
                        new_region = st.selectbox("Region",egypt_governorates,index=egypt_governorates.index(order_details[4]))
                        new_date=st.date_input("Order Date",value=order_details[5])
                        if not products_list:
                           num_products = custom_number_input("Enter the number of products:", min_value=0,step=1)
                           fake_products = []
                           for i in range(num_products):
                             product_type = st.selectbox(f"Enter product type for item {i+1}:",products,key=f"type_{i}")
                             count = custom_number_input(f"Enter count for {product_type}:", min_value=0, step=1, key=f"count_{i}")
                             if product_type:
                               fake_products.append({"Type": product_type, "Count": count})
                           products_list = fake_products
                        if "modified_products" not in st.session_state:
                            st.session_state.modified_products = products_list
                        for i, product in enumerate(st.session_state.modified_products):
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                st.session_state.modified_products[i]["Type"] = st.selectbox(
                                    f"Type {i+1}", products, key=f"product_type_{i}", index=products.index(product["Type"])
                                )
                            with col2:
                                st.session_state.modified_products[i]["Count"] = custom_number_input(
                                    f"Count {i+1}", min_value=0, step=1, key=f"product_count_{i}", value=product["Count"]
                                )
                            with col3:
                                if st.button(f"Remove Product {i+1}", key=f"remove_product_{i}"):
                                    st.session_state.modified_products.pop(i)
                                    st.rerun()
                        if "new_products" not in st.session_state:
                            st.session_state.new_products = []
                        if st.button("Add More Products"):
                            st.session_state.new_products.append({"Type": "", "Count": 1})
                        for i, product in enumerate(st.session_state.new_products):
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                st.session_state.new_products[i]["Type"] = st.selectbox(
                                    f"New Type {i+1}", products, key=f"new_product_type_{i}"
                                )
                            with col2:
                                st.session_state.new_products[i]["Count"] = custom_number_input(
                                    f"New Count {i+1}", min_value=0, step=1, key=f"new_product_count_{i}", value=product["Count"]
                                )
                            with col3:
                                if st.button(f"Remove New Product {i+1}", key=f"remove_new_product_{i}"):
                                    st.session_state.new_products.pop(i)
                                    st.rerun()
                        new_order_price = custom_number_input("Order Price",value=order_details[1],min_value=0,step=1)
                        order_type=st.selectbox("Order Type",options=["Completed","Cancelled","Returned"])
                        if order_type=="Completed":
                            new_ship_company = st.selectbox("Shipping Company",company)
                            new_shipping_price = custom_number_input("Shipping Price Paid By Customer",value=order_details[7],min_value=0,step=1)
                            new_shipping_price_by_company = custom_number_input("Shipping Price Paid To Company",min_value=0,step=1)
                            new_days_to_receive=st.text_input("Days_to_receive")
                            if st.button("Save Completed Order"):
                                # First, check if the customer already exists based on phone number
                                cursor.execute(
                                    f"SELECT customer_id FROM {customers} WHERE customer_phone_1 = %s",
                                    (new_phone1,)
                                )
                                customer = cursor.fetchone()

                                if customer:
                                    customer_id = customer[0]
                                else:
                                    # If not exists, insert new customer
                                    cursor.execute(
                                        f"""
                                        INSERT INTO {customers} (customer_name, customer_phone_1, customer_phone_2, email)
                                        VALUES (%s, %s, %s, %s)
                                        RETURNING customer_id
                                        """,
                                        (new_name, new_phone1, new_phone2, new_email)
                                    )
                                    customer_id = cursor.fetchone()[0]

                                # Prepare products string
                                updated_products = ", ".join(
                                    [f"{item['Type']}:{item['Count']}" for item in (st.session_state.modified_products + st.session_state.new_products)]
                                )

                                # Calculate total product count
                                total_count = sum(item["Count"] for item in (st.session_state.modified_products + st.session_state.new_products))

                                # Insert into orders table
                                cursor.execute(
                                    f"""
                                    INSERT INTO {orders} (customer_id, ship_company, region, order_price, order_number, days_to_receive, hoodies, shipping_price, products, order_date, product_prices,Shipping)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
                                    """,
                                    (
                                        customer_id,
                                        new_ship_company,
                                        new_region,
                                        new_order_price,
                                        new_order_number,  # No order_number provided yet
                                        new_days_to_receive,
                                        total_count,
                                        new_shipping_price,
                                        updated_products,
                                        new_date,
                                        product_prices,
                                        new_shipping_price_by_company,
                                    )
                                )
                                cursor.execute(
                                        f"DELETE FROM {on_hole} WHERE order_number = %s", (search_order_number,)
                                )
                                conn.commit()
                                st.success("✅ Completed order and customer info saved successfully!")
                                log_action(st.session_state.username, "Add Completed Order", f"Customer: {new_name}, Phone: {new_phone1}")
                                del st.session_state.modified_products
                                del st.session_state.new_products
                        elif order_type=="Cancelled":
                                cancelled_reason=st.selectbox("Reason",reasons_1)
                                if st.button("Save Cancelled Order"):
                                    # First, check if the customer already exists based on phone number
                                    cursor.execute(
                                        f"SELECT customer_id FROM {customers} WHERE customer_phone_1 = %s",
                                        (new_phone1,)
                                    )
                                    customer = cursor.fetchone()

                                    if customer:
                                        customer_id = customer[0]
                                    else:
                                        # If not exists, insert new customer
                                        cursor.execute(
                                            f"""
                                            INSERT INTO {customers} (customer_name, customer_phone_1, customer_phone_2, email)
                                            VALUES (%s, %s, %s, %s)
                                            RETURNING customer_id
                                            """,
                                            (new_name, new_phone1, new_phone2, new_email)
                                        )
                                        customer_id = cursor.fetchone()[0]

                                    # Prepare products string
                                    updated_products = ", ".join(
                                        [f"{item['Type']}:{item['Count']}" for item in (st.session_state.modified_products + st.session_state.new_products)]
                                    )

                                    # Calculate total product count
                                    total_count = sum(item["Count"] for item in (st.session_state.modified_products + st.session_state.new_products))

                                    # Insert into orders table
                                    cursor.execute(
                                        f"""
                                        INSERT INTO {cancelled_orders} (customer_id,region, order_price, order_number, hoodies,reason ,products,order_date)
                                        VALUES (%s,%s, %s, %s, %s, %s, %s, %s)
                                        """,
                                        (
                                            customer_id,
                                            new_region,
                                            new_order_price,
                                            new_order_number, 
                                            total_count,
                                            cancelled_reason,
                                            updated_products,
                                            new_date
                                        )
                                    )
                                    cursor.execute(
                                            f"DELETE FROM {on_hole} WHERE order_number = %s", (search_order_number,)
                                    )
                                    conn.commit()
                                    st.success("✅ cancelled order and customer info saved successfully!")
                                    log_action(st.session_state.username, "Add cancelled Order", f"Customer: {new_name}, Phone: {new_phone1}")                                
                                    del st.session_state.modified_products
                                    del st.session_state.new_products
                        elif order_type=="Returned":
                                new_ship_company = st.selectbox("Shipping Company",company)
                                new_status=st.selectbox("Status",["Go Only","Go And Back"])
                                new_reason=st.selectbox("Reason",["Customer","Delivery Man","Quality","Size","Team"])
                                customer_shipping_price=custom_number_input("Shipping Price paid By customer",value=order_details[7], min_value=0,step=1)
                                shipping_price = custom_number_input("Shipping Price Paid To Company",min_value=0,step=1,key=f"shipping_price_by_company_{order_details[0]}")
                                if st.button("Save Returned Order"):
                                    # First, check if the customer already exists based on phone number
                                    cursor.execute(
                                        f"SELECT customer_id FROM {customers} WHERE customer_phone_1 = %s",
                                        (new_phone1,)
                                    )
                                    customer = cursor.fetchone()

                                    if customer:
                                        customer_id = customer[0]
                                    else:
                                        # If not exists, insert new customer
                                        cursor.execute(
                                            f"""
                                            INSERT INTO {customers} (customer_name, customer_phone_1, customer_phone_2, email)
                                            VALUES (%s, %s, %s, %s)
                                            RETURNING customer_id
                                            """,
                                            (new_name, new_phone1, new_phone2, new_email)
                                        )
                                        customer_id = cursor.fetchone()[0]

                                    # Prepare products string
                                    updated_products = ", ".join(
                                        [f"{item['Type']}:{item['Count']}" for item in (st.session_state.modified_products + st.session_state.new_products)]
                                    )

                                    # Calculate total product count
                                    total_count = sum(item["Count"] for item in (st.session_state.modified_products + st.session_state.new_products))
                                    cursor.execute(
                                        f"""
                                        INSERT INTO {returned_orders} (customer_id, ship_company, region, order_number,reason,hoodies,order_price,shipping_price,status,products,order_date,customer_shipping_price)
                                        VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                        """,
                                        (
                                            customer_id,
                                            new_ship_company,
                                            new_region,
                                            new_order_number,
                                            new_reason,
                                            total_count,
                                            new_order_price,
                                            shipping_price,
                                            new_status,
                                            updated_products,
                                            new_date,
                                            customer_shipping_price
                                        )
                                    )
                                    cursor.execute(
                                            f"DELETE FROM {on_hole} WHERE order_number = %s", (search_order_number,)
                                    )
                                    conn.commit()
                                    st.success("✅ Returned order and customer info saved successfully!")
                                    log_action(st.session_state.username, "Add Returned Order", f"Customer: {new_name}, Phone: {new_phone1}")

                                    del st.session_state.modified_products
                                    del st.session_state.new_products


                        st.subheader("Remove Order")
                        with st.form("delete_order_form"):
                            delete_password = st.text_input("Enter Password to Confirm Deletion", type="password")
                            delete_submit = st.form_submit_button("Delete Order")

                            if delete_submit:
                                if delete_password == "admin":
                                    cursor.execute(
                                        f"DELETE FROM {on_hole} WHERE order_number = %s", (search_order_number,)
                                    )
                                    conn.commit()
                                    st.success("Order deleted successfully!")
                                    log_action(st.session_state.username, "Delete Completed Order", f"Order ID: {search_order_number}, Customer: {new_name}")
                                else:
                                    st.error("Incorrect password. Order deletion canceled.")
                    else:
                        st.write("No order found with the given Order Number.")
                    
                    conn.close()
    elif page=='Analysis':
        def metric_card_with_icon(title, content, description,info):
                st.markdown(
                    f"""
                    <div style="background-color: #fff; border: 1px solid #ddd; border-radius: 15px; padding: 15px; 
                                text-align: left; box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.1); position: relative; color: #000; 
                                width: 100%; max-width: 300px;">
                        <div style="position: absolute; top: 8px; right: 8px;" title="{info}">
                            <div style="width: 20px; height: 20px; border: 2px solid #000; border-radius: 50%; display: flex; 
                                        align-items: center; justify-content: center; font-size: 12px; font-weight: bold; color: #000; 
                                        cursor: pointer;">
                                i
                            </div>
                        </div>
                        <h4 style="margin: 5px 10px 0 10px; font-size: 14px; color: #000; padding-left: 10px;">{title}</h4>
                        <p style="margin: -10px 10px 0 10px; font-size: 28px; font-weight: bold; color: #000; padding-left: 10px;">{content}</p>
                        <p style="margin: -7px 10px 5px 10px; font-size: 12px; color: #777; padding-left: 10px;">{description}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        col1,col2,col3,col4=st.columns([1,1,1,1])
        conn = create_connection()
        cursor = conn.cursor()
        total_query = f"""
                SELECT 
                    COALESCE(SUM(o.order_price), 0) AS total_prices
                FROM {orders} o
                """
        cursor.execute(total_query)
        total_prices = cursor.fetchone()[0]

        total_cancelled_query = f"""
                SELECT 
                    COALESCE(SUM(o.order_price), 0) AS total_prices
                FROM {cancelled_orders} o
                """
        cursor.execute(total_cancelled_query)
        total_cancelled=cursor.fetchone()[0]


        total_returned_query = f"""
                SELECT 
                    COALESCE(SUM(o.order_price), 0) AS total_prices
                FROM {returned_orders} o
                """
        cursor.execute(total_returned_query)
        total_returned=cursor.fetchone()[0]
        total_shipping_returned_query = f"""
            SELECT 
                COUNT(o.order_number) AS total_orders, 
                COALESCE(SUM(o.shipping_price), 0)-COALESCE(SUM(o.customer_shipping_price), 0) AS total_shipping_price,
                COALESCE(SUM(o.shipping_price), 0)AS total_shipping_pricee
            FROM {returned_orders} o;
          """
        cursor.execute(total_shipping_returned_query)
        total_returned_orders,total_shipping_returned_price,total_shipping_returned_pricee = cursor.fetchone()
        total_shipping_problems_query = f"""
            SELECT 
                COUNT(o.order_number) AS total_orders, 
                COALESCE(SUM(o.shipping_price), 0)-COALESCE(SUM(o.customer_shipping_price), 0) AS total_shipping_price,
                COALESCE(SUM(o.shipping_price), 0) AS total_shipping_pricee
            FROM {shipping} o;
          """
        cursor.execute(total_shipping_problems_query)
        total_problem_orders,total_shipping_problem_price,total_shipping_problem_pricee = cursor.fetchone()
        total_shipping_completed_query = f"""
            SELECT 
                COALESCE(SUM(o.Shipping), 0)-COALESCE(SUM(o.shipping_price), 0) AS total_shipping_price
            FROM {orders} o;
          """
        cursor.execute(total_shipping_completed_query)
        total_shipping_completed_price = cursor.fetchone()[0]
        total__profit = total_returned - total_shipping_returned_pricee
        total_can_be_gained=total_cancelled+total__profit
        total_profit=total_prices-(total_shipping_problem_pricee+total_shipping_returned_pricee+total_shipping_completed_price)
        total_shipping_price=total_shipping_problem_price+total_shipping_returned_price+total_shipping_completed_price
        completed_query = f"""
            SELECT 
                region, 
                COUNT(order_number) AS total_orders
            FROM {orders}
            GROUP BY region;
        """
        cursor.execute(completed_query)
        completed_data = cursor.fetchall()

        cancelled_query = f"""
            SELECT 
                region, 
                COUNT(order_number) AS total_orders
            FROM {cancelled_orders}
            GROUP BY region;
        """
        cursor.execute(cancelled_query)
        cancelled_data = cursor.fetchall()

        returned_query = f"""
            SELECT 
                region, 
                COUNT(order_number) AS total_orders
            FROM {returned_orders}
            GROUP BY region;
        """
        cursor.execute(returned_query)
        returned_data = cursor.fetchall()
        df_completed = pd.DataFrame(completed_data, columns=["Region", "Completed"])
        df_cancelled = pd.DataFrame(cancelled_data, columns=["Region", "Cancelled"])
        df_returned = pd.DataFrame(returned_data, columns=["Region", "Returned"])

        df = pd.merge(df_completed, df_cancelled, on="Region", how="outer").merge(df_returned, on="Region", how="outer")

        df = df.fillna(0)

        df["Total"] = df["Completed"] + df["Cancelled"] + df["Returned"]

        df["Completed (%)"] = (df["Completed"] / df["Total"]) * 100
        df["Cancelled (%)"] = (df["Cancelled"] / df["Total"]) * 100
        df["Returned (%)"] = (df["Returned"] / df["Total"]) * 100
        completed__query = f"""
            SELECT 
                ship_company, 
                COUNT(order_number) AS total_orders
            FROM {orders}
            GROUP BY ship_company;
        """
        cursor.execute(completed__query)
        completed__data = cursor.fetchall()

        problem__query = f"""
            SELECT 
                ship_company, 
                COUNT(order_number) AS total_orders
            FROM {shipping}
            GROUP BY ship_company;
        """
        cursor.execute(problem__query)
        problem__data = cursor.fetchall()

        returned__query = f"""
            SELECT 
                ship_company, 
                COUNT(order_number) AS total_orders
            FROM {returned_orders}
            GROUP BY ship_company;
        """
        cursor.execute(returned__query)
        returned__data = cursor.fetchall()

        df__completed = pd.DataFrame(completed__data, columns=["ship_company", "Completed"])
        df__problem = pd.DataFrame(problem__data, columns=["ship_company", "Problem"])
        df__returned = pd.DataFrame(returned__data, columns=["ship_company", "Returned"])

        df_ = pd.merge(df__completed, df__problem, on="ship_company", how="outer").merge(df__returned, on="ship_company", how="outer")

        df_ = df_.fillna(0)

        df_["Total"] = df_["Completed"] + df_["Problem"] + df_["Returned"]

        df_["Completed (%)"] = (df_["Completed"] / df_["Total"]) * 100
        df_["Problem (%)"] = (df_["Problem"] / df_["Total"]) * 100
        df_["Returned (%)"] = (df_["Returned"] / df_["Total"]) * 100


        completed_date_query = f"""
            SELECT 
                order_date, 
                COUNT(order_number) AS total_orders
            FROM {orders}
            GROUP BY order_date
            ORDER BY order_date;
        """
        cursor.execute(completed_date_query)
        completed_date_data = cursor.fetchall()

        cancelled_date_query = f"""
            SELECT 
                order_date, 
                COUNT(order_number) AS total_orders
            FROM {cancelled_orders}
            GROUP BY order_date
            ORDER BY order_date;
        """
        cursor.execute(cancelled_date_query)
        cancelled_date_data = cursor.fetchall()

        returned_date_query = f"""
            SELECT 
                order_date, 
                COUNT(order_number) AS total_orders
            FROM {returned_orders}
            GROUP BY order_date
            ORDER BY order_date;
        """
        cursor.execute(returned_date_query)
        returned_date_data = cursor.fetchall()
        df_completed_date = pd.DataFrame(completed_date_data, columns=["Date", "Completed"])
        df_cancelled_date = pd.DataFrame(cancelled_date_data, columns=["Date", "Cancelled"])
        df_returned_date = pd.DataFrame(returned_date_data, columns=["Date", "Returned"])

        df_date = pd.merge(df_completed_date, df_cancelled_date, on="Date", how="outer").merge(df_returned_date, on="Date", how="outer")

        df_date = df_date.fillna(0)

        df_date["Date"] = pd.to_datetime(df_date["Date"])

        df_date = df_date.sort_values(by="Date")

        query=f"""SELECT COUNT(*) AS total_orders
                    FROM (
                        SELECT order_number FROM {orders}
                        UNION ALL
                        SELECT order_number FROM {returned_orders}
                        UNION ALL
                        SELECT order_number FROM {shipping}
                    ) AS all_orders;
                    """
        cursor.execute(query)
        total_orders=cursor.fetchone()[0]
        query = f"""SELECT SUM(hoodies) AS total_products
                FROM (
                    SELECT hoodies FROM {orders}
                    UNION ALL
                    SELECT hoodies FROM {returned_orders}
                    UNION ALL
                    SELECT hoodies FROM {shipping}
                ) AS all_orders;
                """
        cursor.execute(query)
        total_products = cursor.fetchone()[0]
        query = f"""SELECT SUM(o.hoodies) AS total_orders FROM {orders} o"""
        cursor.execute(query)
        completed_products_count = cursor.fetchone()[0]
        query = f"""SELECT Count(o.order_number) AS total_orders FROM {orders} o"""
        cursor.execute(query)
        completed_orders_count = cursor.fetchone()[0]
        total_shipping_price_per_company_query = f"""
            SELECT 
                ship_company, 
                COALESCE(SUM(shipping_price - customer_shipping_price), 0) AS total_shipping_price
            FROM (
                SELECT ship_company, shipping_price, 0 AS customer_shipping_price FROM {orders}
                UNION ALL
                SELECT ship_company, shipping_price, customer_shipping_price FROM {returned_orders}
                UNION ALL
                SELECT ship_company, shipping_price, customer_shipping_price  FROM {shipping}
            ) AS combined_data
            GROUP BY ship_company
            ORDER BY total_shipping_price DESC;

         """
        cursor.execute(total_shipping_price_per_company_query)
        df_shipping_price_per_company = pd.DataFrame(cursor.fetchall(), columns=["ship_company", "total_shipping_price"])
        total_orders_per_company_query = f"""
            SELECT 
                ship_company, 
                COUNT(*) AS total_orders
            FROM (
                SELECT ship_company FROM {orders}
                UNION ALL
                SELECT ship_company FROM {returned_orders}
                UNION ALL
                SELECT ship_company FROM {shipping}
            ) AS combined_data
            GROUP BY ship_company
            ORDER BY total_orders DESC;

         """
        cursor.execute(total_orders_per_company_query)
        df_orders_per_company = pd.DataFrame(cursor.fetchall(), columns=["ship_company", "total_orders"])
        shipping_company_query_products = f"""
                SELECT 
                    o.ship_company AS Shipping_Company,
                    SUM(o.hoodies) AS Total_Products
                FROM {orders} o
                GROUP BY o.ship_company
                ORDER BY Total_Products DESC
                """
        cursor.execute(shipping_company_query_products)
        shipping_data_products = cursor.fetchall()
        df_shipping_products = pd.DataFrame(shipping_data_products, columns=["Shipping Company", "Total Products"])
        conn.close()
        with col1:
            metric_card_with_icon(
                            "Total Shipping Price", 
                            f"{int(total_shipping_price):,}".replace(",", "."),"",
                            "The cost of shipping for all orders."
                        )
            st.markdown("")
            metric_card_with_icon(
                            " AVG Shipping Price", 
                            f"{int(total_shipping_price/completed_products_count):,}".replace(",", "."),"",
                            "Total Shipping Price divide by total Completed Products"
                        )
            st.markdown("")
            result_1 = df_shipping_price_per_company[
            df_shipping_price_per_company["ship_company"] == "SALAH"]["total_shipping_price"]
            result_2=df_shipping_products[
            df_shipping_products["Shipping Company"] == "SALAH"]["Total Products"]
            if not result_1.empty and not result_2.empty:
                    shipping_price_walid = result_1.values[0] / result_2.values[0]
            else:
                shipping_price = 0

        with col2:
            metric_card_with_icon(
                            "Total Profit", 
                            f"{int(total_profit):,}".replace(",", "."),"",
                            "The total money gained from completed orders - total shipping coast."
                        )
            st.markdown("")
            metric_card_with_icon(
                "Average Price Per Order", 
                f"{int(total_prices / completed_orders_count):,}".replace(",", "."), 
                "", 
                "Average Total Price per Order"
            )

            st.markdown("")
            result_1 = df_shipping_price_per_company[
            df_shipping_price_per_company["ship_company"] == "SALAH"]["total_shipping_price"]
            result_2=df_orders_per_company[
            df_shipping_price_per_company["ship_company"] == "SALAH"]["total_orders"]
            if not result_1.empty and not result_2.empty:
                    shipping_price_shipblu = result_1.values[0] / result_2.values[0]
            else:
                shipping_price = 0
        with col3:
            metric_card_with_icon(
                            "Profit could have been achieved", 
                            f"{int(total_can_be_gained):,}".replace(",", "."),"",
                            "The total money could have been achieved which is total profit from cancelled and returned orders"
                        )
            st.markdown("")
            result_1 = df_shipping_price_per_company[
            df_shipping_price_per_company["ship_company"] == "SHIPBLU"]["total_shipping_price"]
            result_2=df_shipping_products[
            df_shipping_products["Shipping Company"] == "SHIPBLU"]["Total Products"]
            if not result_1.empty and not result_2.empty:
                    shipping_price_walid = result_1.values[0] / result_2.values[0]
            else:
                shipping_price = 0
            st.markdown("")
            result_1 = df_shipping_price_per_company[
            df_shipping_price_per_company["ship_company"] == "SHIPBLU"]["total_shipping_price"]
            result_2=df_orders_per_company[
            df_shipping_price_per_company["ship_company"] == "SHIPBLU"]["total_orders"]
            if not result_1.empty and not result_2.empty:
                    shipping_price_shipblu = result_1.values[0] / result_2.values[0]
            else:
                shipping_price = 0
        with col4:
            result_1 = df_shipping_price_per_company[
            df_shipping_price_per_company["ship_company"] == "BOSTA"]["total_shipping_price"]
            result_2=df_shipping_products[
            df_shipping_products["Shipping Company"] == "BOSTA"]["Total Products"]
            if not result_1.empty and not result_2.empty:
                    shipping_price_walid = result_1.values[0] / result_2.values[0]
            else:
                shipping_price = 0
            result_1 = df_shipping_price_per_company[
            df_shipping_price_per_company["ship_company"] == "BOSTA"]["total_shipping_price"]
            result_2=df_orders_per_company[
            df_shipping_price_per_company["ship_company"] == "BOSTA"]["total_orders"]
            if not result_1.empty and not result_2.empty:
                    shipping_price_shipblu = result_1.values[0] / result_2.values[0]
            else:
                shipping_price = 0
            metric_card_with_icon(
                "Average Price Per Product", 
                f"{int(total_profit / completed_products_count):,}".replace(",", "."), 
                "", 
                "Average Total Profit per Product"
            )
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df["Region"],
            y=df["Completed (%)"],
            name="Completed",
            marker_color="green"
        ))
        fig.add_trace(go.Bar(
            x=df["Region"],
            y=df["Cancelled (%)"],
            name="Cancelled",
            marker_color="red"
        ))
        fig.add_trace(go.Bar(
            x=df["Region"],
            y=df["Returned (%)"],
            name="Returned",
            marker_color="orange"
        ))

        fig.update_layout(
            title="Percentage of Orders by Region and Status",
            xaxis_title="Region",
            yaxis_title="Percentage (%)",
            barmode="group",  
            template="plotly_white"
        )

        st.plotly_chart(fig,use_container_width=True)
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_["ship_company"],
            y=df_["Completed (%)"],
            name="Completed",
            marker_color="green"
        ))
        fig.add_trace(go.Bar(
            x=df_["ship_company"],
            y=df_["Problem (%)"],
            name="Problem",
            marker_color="red"
        ))
        fig.add_trace(go.Bar(
            x=df_["ship_company"],
            y=df_["Returned (%)"],
            name="Returned",
            marker_color="orange"
        ))

        fig.update_layout(
            title="Percentage of Orders by shipping_company and Status",
            xaxis_title="shipping_company",
            yaxis_title="Percentage (%)",
            barmode="group", 
            template="plotly_white"
        )

        st.plotly_chart(fig,use_container_width=True)
        # fig = go.Figure()
        # fig.add_trace(go.Scatter(
        #     x=df_date["Date"],
        #     y=df_date["Completed"],
        #     mode="lines",
        #     name="Completed",
        #     line=dict(color="green", width=2)
        # ))
        # fig.add_trace(go.Scatter(
        #     x=df_date["Date"],
        #     y=df_date["Cancelled"],
        #     mode="lines",
        #     name="Cancelled",
        #     line=dict(color="red", width=2, dash="dash")
        # ))
        # fig.add_trace(go.Scatter(
        #     x=df_date["Date"],
        #     y=df_date["Returned"],
        #     mode="lines",
        #     name="Returned",
        #     line=dict(color="orange", width=2, dash="dot")
        # ))

        # fig.update_layout(
        #     title="Number of Orders Over Time by Status",
        #     xaxis_title="Date",
        #     yaxis_title="Number of Orders",
        #     template="plotly_white",
        #     legend_title="Order Status"
        # )

        # st.plotly_chart(fig,use_container_width=True)
    elif page=="Customers":
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: -60px; '>🧑Customers</h1>", unsafe_allow_html=True)
        st.markdown("") 
        st.markdown("")   
        st.markdown("")   
        st.markdown("")   
        st.header("Customers")
        st.markdown("")  
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {customers}")
        customers = cursor.fetchall()
        conn.close()
        
        columns = ["Customer Name", "Customer Phone 1", "Customer Phone 2", "Email","Order Id"] 
        customers_df = pd.DataFrame(customers, columns=columns)
        customers_df.drop("Order Id",axis=1,inplace=True)
        st.dataframe(customers_df) 
        csv_data = customers_df.to_csv(index=False)
        st.download_button(
                    label="Download as CSV",
                    data=csv_data,
                    file_name="Customers.csv",
                    mime="text/csv"
                )     
        excel_data = io.BytesIO()
        with pd.ExcelWriter(excel_data, engine="xlsxwriter") as writer:
            customers_df.to_excel(writer, index=False, sheet_name="Customers")
        excel_data.seek(0)
        st.download_button(
                    label="Download as Excel",
                    data=excel_data,
                    file_name="Customers.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    elif page == "Activity Logs":
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: -60px; '>🕑Activity Logs</h1>", unsafe_allow_html=True)   
        st.markdown("") 
        st.markdown("")   
        st.markdown("")   
        st.markdown("")   
        st.header("Activities")  
        st.markdown("")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM activity_log ORDER BY timestamp DESC")
        logs = cursor.fetchall()
        conn.close()
        
        columns = ["Order iD", "Employee", "Action", "Timestamp", "Details"]
        logs_df = pd.DataFrame(logs, columns=columns)
        logs_df.drop("Order iD",axis=1,inplace=True)
        logs_df["Timestamp"] = pd.to_datetime(logs_df["Timestamp"]) 
        utc_zone = pytz.utc 
        cairo_zone = pytz.timezone("Africa/Cairo")
        logs_df["Timestamp"] = logs_df["Timestamp"].dt.tz_localize(utc_zone).dt.tz_convert(cairo_zone)
        st.dataframe(logs_df) 
        
    elif page == "Completed Orders":
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: -60px; '>📦Completed Orders</h1>", unsafe_allow_html=True)
        if st.session_state.username=="walid" or st.session_state.username=="ahmed":
                selected_3 = option_menu(
                menu_title=None,
                options=["Add Order", "Search Orders", "View All Orders", "Modify Orders","Multiple Orders","Orders View","Delete Orders","Analysis"],
                icons=['cart', 'search', "list-task", 'gear','people','eye','trash','graph-up'],
                menu_icon="cast",
                default_index=0,
                orientation="horizontal",
                styles={
                    'container': {
                        'width': '100%',
                        'margin': '30',
                        'padding': '0',
                    }
                }
            )
        else:
                selected_3 = option_menu(
                    menu_title=None,
                    options=["Add Order", "Search Orders", "View All Orders", "Modify Orders","Multiple Orders","Orders View","Delete Orders"],
                    icons=['cart', 'search', "list-task", 'gear','people','eye','trash'],
                    menu_icon="cast",
                    default_index=0,
                    orientation="horizontal",
                    styles={
                        'container': {
                            'width': '100%',
                            'margin': '30',
                            'padding': '0',
                        }
                    }
                )
        st.markdown("")
        st.markdown("")
        if selected_3=="Add Order":
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
                ship_company = st.selectbox("Shipping Company",company)
                region = st.selectbox("Region",egypt_governorates)
                order_number = st.text_input("Order Code")
                shipping_price = custom_number_input("Shipping Price Paid By Customer",min_value=0,step=1)
                shipping_price_to_company = custom_number_input("Shipping Price Paid To Company",min_value=0,step=1)
                days_to_receive = custom_number_input("Days to Receive Order",min_value=0,step=1)
                if "order_products" not in st.session_state:
                    st.session_state.order_products = []
                if "product_count" not in st.session_state:
                    st.session_state.product_count = 1 

                col1, col2 = st.columns([1, 1])
                col_1, col_2, col_3 = st.columns([1, 1, 25])

                with col_1:
                    if st.button("➕"):
                        st.session_state.product_count += 1
                with col_2:
                    if st.button("➖") and st.session_state.product_count > 1:
                        st.session_state.product_count -= 1
                        st.session_state.order_products.pop()

                for i in range(st.session_state.product_count):
                    col_type, col_count, col_price = st.columns([3, 2, 2])
                    
                    with col_type:
                        type_of_product = st.selectbox(f"Type {i+1}", products, key=f"type_{i}")
                    with col_count:
                        count_of_product = custom_number_input(
                            f"Count {i+1}", min_value=0, step=1, key=f"count_{i}"
                        )
                    with col_price:
                        price_of_product = custom_number_input(
                            f"Price {i+1}", min_value=0.0, step=0.1, key=f"price_{i}"
                        )

                    if len(st.session_state.order_products) <= i:
                        st.session_state.order_products.append(
                            {"Type": type_of_product, "Count": count_of_product, "Price": price_of_product}
                        )
                    else:
                        st.session_state.order_products[i] = {
                            "Type": type_of_product,
                            "Count": count_of_product,
                            "Price": price_of_product
                        }

                order_price = custom_number_input("Order Price", min_value=0, step=1)
                order_date = st.date_input("Order Date")
                def contains_arabic(text):
                    return bool(re.search(r'[\u0600-\u06FF]', text))
                def reset_order_session_states():
                    st.session_state.order_products = []
                    st.session_state.product_count = 1
                if st.button("Add Order"):
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
                    else:
                        conn = create_connection()
                        cursor = conn.cursor()
                        cursor.execute(
                            f"SELECT 1 FROM {orders} WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order = cursor.fetchone()
                        cursor.execute(
                            f"SELECT 1 FROM {cancelled_orders} WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order_1 = cursor.fetchone()
                        cursor.execute(
                            f"SELECT 1 FROM {returned_orders} WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order_2 = cursor.fetchone()
                        if existing_order:
                            st.error("Order Number already exists in Completed Orders. Please enter a unique Order Number.")
                        elif existing_order_1:
                            st.error("Order Number already exists in Cancelled Orders. Please enter a unique Order Number.")
                        elif existing_order_2:
                            st.error("Order Number already exists in Returned Orders. Please enter a unique Order Number.")
                        else:
                            cursor.execute(
                                f"SELECT customer_id FROM {customers} WHERE customer_phone_1 = %s",
                                (corrected_phone_1,)
                            )
                            customer = cursor.fetchone()

                            if customer:
                                customer_id = customer[0]
                            else:
                                cursor.execute(
                                    f"INSERT INTO {customers} (customer_name, customer_phone_1, customer_phone_2, email) VALUES (%s, %s, %s, %s) RETURNING customer_id",
                                    (customer_name, corrected_phone_1, corrected_phone_2, email)
                                )
                                customer_id = cursor.fetchone()[0]
                            total_count = sum(item["Count"] for item in st.session_state.order_products)
                            products_string = ", ".join([f"{item['Type']}:{item['Count']}" for item in st.session_state.order_products])
                            products_prices = ", ".join([f"{item['Type']}:{item['Price']}" for item in st.session_state.order_products])
                            cursor.execute(
                                f"INSERT INTO {orders} (customer_id, ship_company, region, order_price, order_number,days_to_receive,hoodies,shipping_price,products,order_date,product_prices,Shipping) VALUES (%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s)",
                                (customer_id, ship_company, region, order_price, order_number,days_to_receive,total_count,shipping_price,products_string,order_date,products_prices,shipping_price_to_company)
                            )

                            conn.commit()
                            st.success("Order added successfully!")
                            log_action(st.session_state.username, "Add Completed Order", f"Order ID: {order_number}, Customer: {customer_name}")
                            reset_order_session_states()  
                        conn.close()
                        

        elif selected_3=="Search Orders":
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
                        c.email, o.ship_company, o.region, o.order_price,o.days_to_receive,o.hoodies,o.shipping_price,o.products,o.order_date
                    FROM {orders} o
                    INNER JOIN {customers} c ON o.customer_id = c.customer_id
                    WHERE {search_condition}
                    """,
                    (search_query,)
                )

                results = cursor.fetchall()

                if results:
                    st.write("Search Results:")
                    st.table(results)
                    total_price = sum(order[7] for order in results)
                    total_hoodies = sum(order[9] for order in results)
                    st.write(f"Total Amount Spent: {total_price}")
                    st.write(f"Total Number of Products: {total_hoodies}")
                else:
                    st.write("No orders found for the given query.")

                conn.close()
                
        elif selected_3=="View All Orders":
            st.header("All Orders")
            
            sort_by = st.selectbox("Sort by", ["Order Code", "Order Price"])
            sort_order = st.radio("Sort orders", ["Ascending", "Descending"])
            
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT DISTINCT ship_company FROM {orders}")
            ship_companies = [row[0] for row in cursor.fetchall()]
            selected_ship_company = st.selectbox("Filter by Shipping Company", ["All"] + ship_companies)
            sort_column = "CAST(o.order_number AS INTEGER)" if sort_by == "Order Code" else "o.order_price"
            sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
            
            query = f"""
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                c.email, o.ship_company, o.region, o.order_price,o.days_to_receive,o.hoodies,o.shipping_price,o.products,o.order_date,o.product_prices,o.Shipping
            FROM {orders} o
            INNER JOIN {customers} c ON o.customer_id = c.customer_id
            """
            if selected_ship_company != "All":
                query += f" WHERE o.ship_company = '{selected_ship_company}'"
            query += f" ORDER BY {sort_column} {sort_direction}"

            cursor.execute(query)
            all_orders = cursor.fetchall()

            total_query = f"SELECT COUNT(*),COALESCE(SUM(hoodies),0), COALESCE(SUM(order_price), 0), COALESCE(SUM(shipping_price), 0),COALESCE(SUM(Shipping), 0) FROM {orders}"
            if selected_ship_company != "All":
                total_query += f" WHERE ship_company = '{selected_ship_company}'"
            cursor.execute(total_query)
            total_orders,total_hoodies,total_price,total_shipping_price,total_shipping_price_company = cursor.fetchone()

            conn.close()

            if all_orders:
                data = []
                for order in all_orders:
                    data.append({
                        "Order Number": order[0],                     
                        "Date":order[12],
                        "Customer Name": order[1],
                        "Phone 1": order[2],
                        "Phone 2": order[3],
                        "Email": order[4],
                        "Shipping Company": order[5],
                        "Region": order[6],
                        "Order Price": f"{order[7]}",
                        "Shipping Price By Customer":order[10],
                        "Shipping Price To Company":order[14],
                        "Order Profit": (order[7] or 0) - (order[10] or 0),
                        "Days to Receive":order[8],
                        "Type of products":order[11],
                        "price of products":order[13],
                        "Total number of Products":order[9],
                    })
                df = pd.DataFrame(data)
                st.write("All Orders:")
                st.dataframe(df)
                st.write(f"**Total Orders:** {total_orders}")
                st.write(f"**Total Price:** {int(total_price):,}".replace(",", "."))
                st.write(f"**Total Shipping Price:** {int(total_shipping_price_company)-int(total_shipping_price):,}".replace(",", "."))
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

        elif selected_3=="Modify Orders":
                st.header("Update or Remove Orders")
                
                st.subheader("Select an Order")
                search_order_number = st.text_input("Enter Order Code")

                if search_order_number:
                    if "last_order_number" not in st.session_state or st.session_state.last_order_number != search_order_number:
                        if "modified_products"  in st.session_state:
                            del st.session_state.modified_products
                        if "new_products"  in st.session_state:
                            del st.session_state.new_products
                        st.session_state.last_order_number = search_order_number
                    conn = create_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute(
                        f"""
                        SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2,
                            c.email, o.ship_company, o.region, o.order_price,o.days_to_receive,o.hoodies,o.shipping_price,o.order_date,o.products,o.Shipping
                        FROM {orders} o
                        INNER JOIN {customers} c ON o.customer_id = c.customer_id
                        WHERE o.order_number = %s
                        """,
                        (search_order_number,)
                    )
                    order_details = cursor.fetchone()

                    if order_details:
                        st.write("Order Details:")
                        st.table([order_details])
                        if order_details[12]:  
                          products_list = [
                            {"Type": p.split(":")[0], "Count": int(p.split(":")[1])}
                            for p in order_details[12].split(", ") if ":" in p
                          ]
                        else:
                          products_list = [] 

                        st.subheader("Update Order")
                        new_name=st.text_input("Customer Name",value=order_details[1])
                        new_phone1=st.text_input("Customer Phone 1",value=order_details[2])
                        new_phone2=st.text_input("Customer Phone 1",value=order_details[3])
                        new_email=st.text_input("Email",value=order_details[4])
                        new_ship_company = st.selectbox("Shipping Company",company,index=company.index(order_details[5]))
                        new_region = st.selectbox("Region",egypt_governorates,index=egypt_governorates.index(order_details[6]))
                        new_order_price = custom_number_input("Order Price",value=order_details[7],min_value=0,step=1)
                        new_shipping_price = custom_number_input("Shipping Price Paid By Customer",value=order_details[10],min_value=0,step=1)
                        new_shipping_price_to_company = custom_number_input("Shipping Price Paid To Company",value=order_details[13],min_value=0,step=1)
                        new_days_to_receive=st.text_input("Days_to_receive",value=order_details[8])
                        new_date=st.date_input("Order Date",value=order_details[11])
                        if not products_list:
                           num_products = custom_number_input("Enter the number of products:", min_value=0,step=1)
                           fake_products = []
                           for i in range(num_products):
                             product_type = st.selectbox(f"Enter product type for item {i+1}:",products,key=f"type_{i}")
                             count = custom_number_input(f"Enter count for {product_type}:", min_value=0, step=1, key=f"count_{i}")
                             if product_type:
                               fake_products.append({"Type": product_type, "Count": count})
                           products_list = fake_products
                        if "modified_products" not in st.session_state:
                            st.session_state.modified_products = products_list
                        for i, product in enumerate(st.session_state.modified_products):
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                st.session_state.modified_products[i]["Type"] = st.selectbox(
                                    f"Type {i+1}", products, key=f"product_type_{i}", index=products.index(product["Type"])
                                )
                            with col2:
                                st.session_state.modified_products[i]["Count"] = custom_number_input(
                                    f"Count {i+1}", min_value=0, step=1, key=f"product_count_{i}", value=product["Count"]
                                )
                            with col3:
                                if st.button(f"Remove Product {i+1}", key=f"remove_product_{i}"):
                                    st.session_state.modified_products.pop(i)
                                    st.rerun()
                        if "new_products" not in st.session_state:
                            st.session_state.new_products = []
                        if st.button("Add More Products"):
                            st.session_state.new_products.append({"Type": "", "Count": 1})
                        for i, product in enumerate(st.session_state.new_products):
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                st.session_state.new_products[i]["Type"] = st.selectbox(
                                    f"New Type {i+1}", products, key=f"new_product_type_{i}"
                                )
                            with col2:
                                st.session_state.new_products[i]["Count"] = custom_number_input(
                                    f"New Count {i+1}", min_value=0, step=1, key=f"new_product_count_{i}", value=product["Count"]
                                )
                            with col3:
                                if st.button(f"Remove New Product {i+1}", key=f"remove_new_product_{i}"):
                                    st.session_state.new_products.pop(i)
                                    st.rerun()
                        if st.button("Update Order"):
                            updated_products = ", ".join(
                                [f"{item['Type']}:{item['Count']}" for item in (st.session_state.modified_products + st.session_state.new_products)]
                            )
                            cursor.execute(
                                f"""
                                UPDATE {customers}
                                SET customer_name = %s, customer_phone_1 = %s, customer_phone_2 = %s, email = %s
                                WHERE customer_id = (
                                    SELECT customer_id 
                                    FROM {orders} 
                                    WHERE order_number = %s
                                )
                                """,
                                (new_name, new_phone1, new_phone2, new_email, search_order_number)
                            )
                            
                            cursor.execute(
                                f"""
                                UPDATE {orders}
                                SET ship_company = %s, region = %s, order_price = %s, days_to_receive = %s,
                                    hoodies = %s, shipping_price = %s, products = %s, order_date = %s,Shipping= %s
                                WHERE order_number = %s
                                """,
                                (
                                    new_ship_company, new_region, new_order_price, new_days_to_receive,
                                    sum(item["Count"] for item in (st.session_state.modified_products + st.session_state.new_products)),
                                    new_shipping_price, updated_products, new_date,new_shipping_price_to_company, search_order_number
                                )
                            )

                            conn.commit()
                            del st.session_state.modified_products
                            del st.session_state.new_products
                            st.success("Order updated successfully!")
                            log_action(st.session_state.username,"Update Completed Order",f"Order ID: {search_order_number}, Customer: {new_name}")
                        st.subheader("Remove Order")
                        with st.form("delete_order_form"):
                            delete_password = st.text_input("Enter Password to Confirm Deletion", type="password")
                            delete_submit = st.form_submit_button("Delete Order")

                            if delete_submit:
                                if delete_password == "admin":
                                    cursor.execute(
                                        f"DELETE FROM {orders} WHERE order_number = %s", (search_order_number,)
                                    )
                                    conn.commit()
                                    st.success("Order deleted successfully!")
                                    log_action(st.session_state.username, "Delete Completed Order", f"Order ID: {search_order_number}, Customer: {new_name}")
                                else:
                                    st.error("Incorrect password. Order deletion canceled.")
                    else:
                        st.write("No order found with the given Order Number.")
                    
                    conn.close()
        elif selected_3 == "Multiple Orders":
            sort_by = st.selectbox("Sort by", ["Order Code", "Total Price"], key="sort_by_selectbox")
            sort_order = st.radio("Sort order", ["Ascending", "Descending"], key="sort_order_selectbox")

            conn = create_connection()
            cursor = conn.cursor()

            sort_column = "MIN(CAST(o.order_number AS INTEGER))" if sort_by == "Order Code" else "SUM(o.order_price)"
            sort_direction = "ASC" if sort_order == "Ascending" else "DESC"

            query = f"""
                    SELECT 
                        c.customer_name, 
                        c.customer_phone_1, 
                        c.email,
                        ARRAY_AGG(o.order_number ORDER BY o.order_number) AS order_numbers,
                        ARRAY_AGG(o.order_date ORDER BY o.order_date) AS orders_date,
                        COUNT(o.order_number) AS order_count,
                        SUM(o.order_price) AS total_price,
                        SUM(o.hoodies) AS total_products,
                        SUM(o.shipping_price) AS total_shipping,
                        ROUND(AVG(CAST(o.days_to_receive AS NUMERIC)), 2) AS avg_days_to_receive
                    FROM {customers} c
                    INNER JOIN {orders} o ON c.customer_id = o.customer_id
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
                    customer_name, customer_phone_1, email, order_numbers, orders_date, order_count, customer_total_price, customer_total_products, customer_total_shipping, avg_days_to_receive = row

                    customer_total_products = customer_total_products or 0
                    order_numbers = order_numbers or []
                    orders_date = orders_date or []

                    total_price += customer_total_price or 0
                    total_shipping += customer_total_shipping or 0
                    total_products += customer_total_products

                    data.append({
                        "Customer Name": customer_name,
                        "Phone Number": customer_phone_1,
                        "Email": email,
                        "Order Numbers": ", ".join(map(str, order_numbers)),
                        "Date": ", ".join(map(str, orders_date)),
                        "Order Count": order_count,
                        "Total Price": f"{customer_total_price}",
                        "Total Shipping Price": f"{customer_total_shipping}",
                        "Total Order Profit": f"{(customer_total_price or 0) - (customer_total_shipping or 0)}",
                        "Total Products": f"{customer_total_products}",
                        "Avg Days to Receive": avg_days_to_receive
                    })

                num_customers = len(multiple_orders)
                st.write("Customers with Multiple Orders:")
                st.dataframe(data)
                st.write(f"**Number of Customers with Multiple Orders:** {num_customers}")
                st.write(f"**Total Price:** {int(total_price):,}")
                st.write(f"**Total Shipping Price:** {int(total_shipping):,}")
                st.write(f"**Total Profit:** {int((total_price or 0) - (total_shipping or 0)):,}")
                st.write(f"**Total Products of Their Orders:** {total_products}")
            else:
                st.write("No customers with multiple orders found.")

            conn.close()



        elif selected_3=="Orders View":            
            sort_by = st.selectbox("Sort by", ["Order Code", "Total Price"])
            sort_order = st.radio("Sort order", ["Ascending", "Descending"])
            
            conn = create_connection()
            cursor = conn.cursor()
            
            sort_column = "ARRAY_AGG(CAST(o.order_number AS INTEGER))" if sort_by == "Order Code" else "SUM(o.order_price)"
            sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
            
            query = f"""
                SELECT c.customer_name, c.customer_phone_1, c.email,
                    ARRAY_AGG(o.order_number) AS order_numbers,
                    ARRAY_AGG(o.order_date) AS orders_date,
                    COUNT(o.order_number) AS order_count,
                    SUM(o.order_price) AS total_price,
                    SUM(o.shipping_price) AS total_shipping,
                    STRING_AGG(o.products, ', ') AS product_details
                FROM {customers} c
                INNER JOIN {orders} o ON c.customer_id = o.customer_id
                GROUP BY c.customer_name, c.customer_phone_1, c.email
                ORDER BY {sort_column} {sort_direction}
                """
            cursor.execute(query)
            consolidated_orders = cursor.fetchall()

            total_query = f"""
            SELECT COUNT(o.order_number), COALESCE(SUM(o.hoodies),0),COALESCE(SUM(o.order_price), 0),COALESCE(SUM(o.shipping_price), 0)
            FROM {orders} o
            """
            cursor.execute(total_query)
            total_orders,total_products, total_prices, total_shipping_prices = cursor.fetchone()

            conn.close()

            if consolidated_orders:
                data = []
                total_product_count = 0
                product_summary = {}

                for row in consolidated_orders:
                    customer_name, customer_phone_1, email, order_numbers, date, order_count, total_price, total_shipping, product_details = row
                    customer_products = {}

                    if product_details: 
                        for product in product_details.split(', '):
                            if ':' not in product:
                                continue
                            try:
                                product_type, count = product.rsplit(':', 1)
                                count = int(count)
                                customer_products[product_type] = customer_products.get(product_type, 0) + count
                                product_summary[product_type] = product_summary.get(product_type, 0) + count
                                total_product_count += count
                            except ValueError:
                                continue

                    data.append({
                        "Customer Name": customer_name,
                        "Phone Number": customer_phone_1,
                        "Email": email,
                        "Order Numbers": ", ".join(order_numbers),
                        "Date": ", ".join([str(d) for d in (date or ["none"])]),
                        "Order Count": order_count,
                        "Type of Products": ', '.join([f"{name}: {count}" for name, count in customer_products.items()]) if customer_products else "None",
                        "Total Price": f"{total_price}",
                        "Total Shipping Price": f"{total_shipping}",
                        "Total Order Profit": f"{(total_price or 0) - (total_shipping or 0)}",
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


        elif selected_3 == "Delete Orders":
            query = f"""
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                c.email, o.ship_company, o.region, o.order_price, o.days_to_receive, 
                o.hoodies, o.shipping_price, o.order_date
            FROM {orders} o
            INNER JOIN {customers} c ON o.customer_id = c.customer_id
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
                        "Date": order[11], 
                        "Customer Name": order[1],
                        "Phone 1": order[2],
                        "Phone 2": order[3],
                        "Email": order[4],
                        "Ship Company": order[5],
                        "Region": order[6],
                        "Order Price": order[7],
                        "Days to Receive": order[8],
                        "Total Number Of Products": order[9],
                        "Shipping Price": order[10],
                    }
                    for order in all_orders
                ]
                df = pd.DataFrame(orders_data)
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_selection("multiple", use_checkbox=True, header_checkbox=True)
                gb.configure_column("Order Number", sort="asc")  
                grid_options = gb.build()
                grid_response = AgGrid(
                        df,
                        gridOptions=grid_options,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        height=400,
                        theme="streamlit",
                        fit_columns_on_grid_load=True,
                        key="grid",
                )
                selected_rows = grid_response["selected_rows"]

                if selected_rows is None or selected_rows.empty:
                    st.warning("No orders selected.")
                else:
                    st.write("Selected Rows:", selected_rows)  
                    if "Order Number" in selected_rows.columns:
                        selected_order_numbers = selected_rows["Order Number"].astype(str).tolist()
                        selected_customers = selected_rows["Customer Name"].astype(str).tolist()
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

                            delete_query = f"DELETE FROM {orders} WHERE order_number IN %s"
                            try:
                                with create_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute(delete_query, (orders_tuple,))
                                    conn.commit()
                                    st.success(f"Successfully deleted {len(selected_order_numbers)} orders.")
                                    log_action(st.session_state.username, "Delete Completed Order", f"Order ID: {selected_order_numbers}, Customers: {selected_customers}")
                            except Exception as e:
                                st.error(f"Error deleting orders: {e}")
        elif selected_3=="Analysis":
            col1, col2, col3,col4= st.columns([1, 1, 1,1])
            def metric_card_with_icon(title, content, description,info):
                st.markdown(
                    f"""
                    <div style="background-color: #fff; border: 1px solid #ddd; border-radius: 15px; padding: 15px; 
                                text-align: left; box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.1); position: relative; color: #000; 
                                width: 100%; max-width: 300px;">
                        <div style="position: absolute; top: 8px; right: 8px;" title="{info}">
                            <div style="width: 20px; height: 20px; border: 2px solid #000; border-radius: 50%; display: flex; 
                                        align-items: center; justify-content: center; font-size: 12px; font-weight: bold; color: #000; 
                                        cursor: pointer;">
                                i
                            </div>
                        </div>
                        <h4 style="margin: 5px 10px 0 10px; font-size: 14px; color: #000; padding-left: 10px;">{title}</h4>
                        <p style="margin: -10px 10px 0 10px; font-size: 28px; font-weight: bold; color: #000; padding-left: 10px;">{content}</p>
                        <p style="margin: -7px 10px 5px 10px; font-size: 12px; color: #777; padding-left: 10px;">{description}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            conn = create_connection()
            cursor = conn.cursor()

            total_query = f"""
                SELECT 
                    COUNT(o.order_number) AS total_orders, 
                    COALESCE(SUM(o.hoodies), 0) AS total_products,
                    COALESCE(SUM(o.order_price), 0) AS total_prices,
                    COALESCE(SUM(o.shipping_price), 0) AS total_shipping_prices
                FROM {orders} o
                """
            cursor.execute(total_query)
            total_orders, total_products, total_prices, total_shipping_prices = cursor.fetchone()

            total_profit = total_prices - total_shipping_prices
            query = f"""
                SELECT 
                    o.region, 
                    COUNT(o.order_number) AS total_orders 
                FROM {orders} o
                GROUP BY o.region
                ORDER BY total_orders DESC
                """
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=["Region", "Total Orders"])
            total_orders_region = df['Total Orders'].sum()
            df['Percentage'] = (df['Total Orders'] / total_orders_region) * 100
            metrics_query = f"""
                    SELECT 
                        COALESCE(AVG(o.shipping_price::NUMERIC), 0) AS avg_shipping_price,
                        COALESCE(AVG(o.days_to_receive::NUMERIC), 0) AS avg_days_to_receive
                    FROM {orders} o
                """
            cursor.execute(metrics_query)
            avg_shipping_price,avg_day_to_receive = cursor.fetchone()
            
            shipping_company_query = f"""
                SELECT 
                    o.ship_company AS Shipping_Company,
                    COUNT(o.order_number) AS Total_Orders
                FROM {orders} o
                GROUP BY o.ship_company
                ORDER BY Total_Orders DESC
                """
            cursor.execute(shipping_company_query)
            shipping_data = cursor.fetchall()
            df_shipping = pd.DataFrame(shipping_data, columns=["Shipping Company", "Total Orders"])
            total_orders_shipping = df_shipping['Total Orders'].sum()
            df_shipping['Percentage'] = (df_shipping['Total Orders'] / total_orders_shipping) * 100
            total_cancelled_query=f"""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM {cancelled_orders} o
            """
            cursor.execute(total_cancelled_query)
            total_cancelled=cursor.fetchone()[0]
            total_returned_query=f"""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM {returned_orders} o
            """
            cursor.execute(total_returned_query)
            total_returned=cursor.fetchone()[0]
            total_shipping_query=f"""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM {shipping} o
            """
            cursor.execute(total_shipping_query)
            total_shipping=cursor.fetchone()[0]
            
            date_query = f"""
                            SELECT 
                            o.order_date, 
                            COUNT(o.order_number) AS total_orders,
                            SUM(o.order_price) AS total_sales
                        FROM {orders} o
                        GROUP BY o.order_date
                        ORDER BY o.order_date
                      """
            cursor.execute(date_query)
            date_data = cursor.fetchall()
            df_date = pd.DataFrame(date_data, columns=["Date", "Total Orders", "Total Sales"])
            df_date["Date"] = pd.to_datetime(df_date["Date"])
            df_date.sort_values(by="Date", inplace=True) 
            def parse_products(products_str):
                product_items = re.findall(r'([a-zA-Z\s]+):(\d+)', products_str)
                products_dict = {item[0].strip(): int(item[1]) for item in product_items}
                return products_dict

            query = f"""
            SELECT 
                o.order_number,
                o.products,
                o.shipping_price
            FROM {orders} o
            """
            cursor.execute(query)
            data = cursor.fetchall()

            product_shipping = {}

            for order in data:
                order_number, products_str, total_shipping_price = order
                if not products_str:
                    continue
                products_dict = parse_products(products_str) 
                total_quantity = sum(products_dict.values()) 
                for product_type, quantity in products_dict.items():
                    shipping_price_for_product = (quantity / total_quantity) * total_shipping_price
                    if product_type in product_shipping:
                        product_shipping[product_type] += shipping_price_for_product
                    else:
                        product_shipping[product_type] = shipping_price_for_product

            df__shipping = pd.DataFrame(product_shipping.items(), columns=["Product Type", "Total Shipping Price"])
            df__shipping = df__shipping.sort_values(by="Total Shipping Price", ascending=False)
            total_orders_shipping = df__shipping['Total Shipping Price'].sum()
            df__shipping['Percentage'] = (df__shipping['Total Shipping Price'] / total_orders_shipping) * 100
            query = f"""
            SELECT 
                o.order_number,
                o.products,
                o.shipping_price,
                o.order_price,
                o.product_prices
            FROM {orders} o
            """
            cursor.execute(query)
            data = cursor.fetchall()

            def parse_products(products_str):
                return {item.split(":")[0].strip(): int(item.split(":")[1]) for item in products_str.split(",")}

            def parse_prices(prices_str):
                return {item.split(":")[0].strip(): float(item.split(":")[1]) for item in prices_str.split(",")}

            total_product_prices = {}
            total_product_counts = {}

            for order in data:
                order_number, products_str, total_shipping_price, total_order_price, product_prices_str = order
                if not products_str or not product_prices_str:
                    continue

                products_dict = parse_products(products_str)  # e.g. {"T-Shirt": 1, "Dxlr T-Shirt": 2}
                prices_dict = parse_prices(product_prices_str)  # e.g. {"T-Shirt": 750.00, "Dxlr T-Shirt": 780.00}

                for product_type, quantity in products_dict.items():
                    price_per_unit = prices_dict.get(product_type, 0)
                    total_price_for_product = price_per_unit * quantity

                    total_product_prices[product_type] = total_product_prices.get(product_type, 0) + total_price_for_product
                    total_product_counts[product_type] = total_product_counts.get(product_type, 0) + quantity

            df_total_prices = pd.DataFrame(list(total_product_prices.items()), columns=["Product Type", "Total Price"])
            df_total_prices["Total Quantity"] = df_total_prices["Product Type"].map(total_product_counts)
            df_total_prices["Avg Price"] = df_total_prices["Total Price"] / df_total_prices["Total Quantity"]
            df_total_prices = df_total_prices.sort_values(by="Total Price", ascending=False)

            total_prices_sum = df_total_prices["Total Price"].sum()
            df_total_prices["Percentage"] = (df_total_prices["Total Price"] / total_prices_sum) * 100

            query = f"""
            SELECT 
                o.products
            FROM {orders} o
            """

            cursor.execute(query)
            data = cursor.fetchall()

            total_counts = {}

            for row in data:
                products_str = row[0]
                if not products_str:
                    continue  

                products_list = products_str.split(',')

                for product_entry in products_list:
                    product_type, quantity = product_entry.split(':')
                    product_type = product_type.strip().lower()  
                    quantity = int(quantity.strip()) 
                    if product_type in total_counts:
                        total_counts[product_type] += quantity
                    else:
                        total_counts[product_type] = quantity

            df_total_counts = pd.DataFrame(total_counts.items(),columns=["Product Type", "Total Quantity"])
            df_total_counts = df_total_counts.sort_values(by="Total Quantity", ascending=False)
            total_countsss = df_total_counts['Total Quantity'].sum()
            df_total_counts['Percentage'] = (df_total_counts['Total Quantity'] / total_countsss) * 100
            query = f"""
                    WITH product_orders AS (
                        SELECT
                            o.order_number,
                            TRIM(SPLIT_PART(regexp_split_to_table(o.products, ','), ':', 1)) AS product_name
                        FROM {orders} o
                    ),
                    distinct_orders AS (
                        SELECT COUNT(DISTINCT order_number) AS total_orders FROM {orders}
                    )
                    SELECT 
                        product_name,
                        COUNT(DISTINCT order_number) AS order_count,
                        (COUNT(DISTINCT order_number) * 100.0) / (SELECT total_orders FROM distinct_orders) AS percentage
                    FROM product_orders
                    WHERE product_name IS NOT NULL
                    GROUP BY product_name
                    ORDER BY percentage DESC;

                    """
            df_products_percentage = pd.read_sql(query, conn)
            total_shipping_query = f"""
                SELECT ship_company, 
                    SUM(shipping_price) AS total_shipping_price
                FROM {orders}
                GROUP BY ship_company
                ORDER BY total_shipping_price DESC
            """
            df_shippingprice_byshippcompany_foreachproduct = pd.read_sql_query(total_shipping_query, conn)  
            shipping_company_query_products = f"""
                SELECT 
                    o.ship_company AS Shipping_Company,
                    SUM(o.hoodies) AS Total_Products
                FROM {orders} o
                GROUP BY o.ship_company
                ORDER BY Total_Products DESC
                """
            cursor.execute(shipping_company_query_products)
            shipping_data_products = cursor.fetchall()
            df_shipping_products = pd.DataFrame(shipping_data_products, columns=["Shipping Company", "Total Products"])
            conn.close()
            percentage_completed = total_orders / (total_orders + total_cancelled + total_returned)
            percentage_completed_1 = total_orders / (total_orders + total_cancelled + total_returned+total_shipping)
            avg_shipping_price_1=total_shipping_prices/total_products
            with col1:
                    metric_card_with_icon(
                        "Total Ordes", 
                        f"{total_orders:,}","", 
                        "The total number of orders."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                        "Total Products", 
                        f"{int(total_products):,}".replace(",", "."),"",
                        "The The total number of products sold."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                        "Avg Shipping Price(Products)", 
                        f"{avg_shipping_price_1:.2f}","",
                        """The average cost of shipping for all products. 
                        متوسط سعر الشحن للمنتج اللي هو عباره عن المجموع الكلي للشحن مقسوم على عدد المنتجات"""
                    )

            with col2:
                    metric_card_with_icon(
                        "Total Price", 
                        f"{int(total_prices):,}".replace(",", "."),"",
                        "The total revenue generated from all orders."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                        "Avg Shipping Price(order)", 
                        f"{avg_shipping_price:.2f}".replace(",", "."),"",
                        """The average cost of shipping for all orders.
                        متوسط سعر الشحن للاوردر اللي هو عباره عن المجموع الكلي للشحن مقسوم على عدد الاوردرات"""
                    )
                    st.markdown("")
                    metric_card_with_icon(
                        "Average Price per Product", 
                        f"{int(total_prices/total_products):,}".replace(",", "."),"",
                        "The average revenue generated per product across all orders."
                    )

            with col3:
                    metric_card_with_icon(
                        "Total Shipping Prices", 
                        f"{int(total_shipping_prices):,}".replace(",", "."),"", 
                        "The total shipping cost incurred for all orders."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                        "Avg Days to Receive", 
                        f"{avg_day_to_receive:.2f}","",
                        "The average number of days it takes for customers to receive their orders."
                    )

                    st.markdown("")
                    metric_card_with_icon(
                    "Percentage of Completed Orders(problems)", 
                    f"{percentage_completed_1 * 100:.2f}%", "", 
                    """The percentage of completed orders out of total orders with problems.
                    نسبة الاوردرات الكامله بالنسبه لكل الاوردرات"""
                    )
            with col4:
                    metric_card_with_icon(
                        "Total Profit", 
                        f"{int(total_profit):,}".replace(",", "."),"", 
                        """The total profit (total revenue minus total shipping cost).
                        السعر الكلي مطروح منه الشحن الكلي """
                    )
                    st.markdown("")
                    metric_card_with_icon(
                    "Percentage of Completed Orders", 
                    f"{percentage_completed * 100:.2f}%", "", 
                    """The percentage of completed orders out of total orders.
                    نسبة الاوردرات الكامله بالنسبه لكل الاوردرات"""
                    )

            fig = px.bar(
                df, 
                x="Region", 
                y="Total Orders", 
                title="Total Orders by Region",
                labels={"Region": "Region", "Total Orders": "Number of Orders"},
                text=df['Percentage'].apply(lambda x: f"{x:.2f}%"), 
                color="Region", 
                height=600
            )

            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(
                xaxis_title="Region",
                yaxis_title="Total Orders",
                uniformtext_minsize=8,
                uniformtext_mode='hide'
            )
            st.markdown("")
            st.plotly_chart(fig, use_container_width=True)
            df_merged = df_shipping.merge(
                df_shippingprice_byshippcompany_foreachproduct[["ship_company", "total_shipping_price"]],
                left_on="Shipping Company",
                right_on="ship_company",
                how="left"
            )

            df_merged = df_merged.merge(df_shipping_products, on="Shipping Company", how="left")

            df_merged["Avg Shipping Price Per Order"] = df_merged["total_shipping_price"] / df_merged["Total Orders"]

            df_merged["Avg Shipping Price Per Product"] = df_merged["total_shipping_price"] / df_merged["Total Products"]
            fig_shipping = px.bar(
                df_merged,
                x="Shipping Company",
                y="Total Orders",
                title="Total Orders by Shipping Company",
                labels={"Shipping Company": "Shipping Company", "Total Orders": "Number of Orders"},
                color="Shipping Company",
                height=600,
                text=df_shipping['Percentage'].apply(lambda x: f"{x:.2f}%"), 
                hover_data={
                    "Shipping Company": False,  
                    "Total Orders": True,
                    "Total Products": True, 
                    "Avg Shipping Price Per Order": ":.2f",  
                    "Avg Shipping Price Per Product": ":.2f" 
                }
            )

            fig_shipping.update_traces(
                texttemplate='%{text}', 
                textposition='outside' 
            )

            fig_shipping.update_layout(
                xaxis_title="Shipping Company",
                yaxis_title="Total Orders",
                uniformtext_minsize=8,
                uniformtext_mode='hide'
            )

            st.plotly_chart(fig_shipping, use_container_width=True)
            fig = px.line(
                df_date, 
                x="Date", 
                y="Total Orders", 
                title="Orders Over Time",
                labels={"Date": "Date", "Total Orders": "Number of Orders"}
            )
            st.plotly_chart(fig,use_container_width=True)
            fig = px.bar(
                df__shipping,
                x="Product Type",
                y="Total Shipping Price",
                title="Shipping Price Distribution by Product Type",
                labels={"Total Shipping Price": "Shipping Price (Currency)"},
                template="plotly_white",
                text=df__shipping['Percentage'].apply(lambda x: f"{x:.2f}%"),
                color="Product Type"
            )
            fig.update_traces(texttemplate="%{text}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
            fig = px.bar(
                df_total_prices,
                x="Product Type",
                y="Total Price",
                title="Price Distribution by Product Type",
                labels={"Total Price": "Price (Currency)"},
                template="plotly_white",
                text=df_total_prices["Percentage"].apply(lambda x: f"{x:.2f}%"),
                color="Product Type",
                custom_data=[df_total_prices["Avg Price"]]  # Explicitly map Avg Price
            )

            fig.update_traces(
                texttemplate="%{text}", 
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Total Price: %{y}<br>Avg Price: %{customdata[0]:.2f}"
            )
            st.plotly_chart(fig, use_container_width=True)

            fig = px.bar(
                df_total_counts,
                x="Product Type",
                y="Total Quantity",
                title="Quantity Distribution by Product Type",
                labels={"Total Quantity": "Quantity (Currency)"},
                template="plotly_white",
                text=df_total_counts['Percentage'].apply(lambda x: f"{x:.2f}%"),
                color="Product Type"
            )
            fig.update_traces(texttemplate="%{text}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
            fig = px.bar(df_products_percentage, x="product_name", y="percentage", 
             text="percentage", labels={"product_name": "Product Type", "percentage": "Percentage (%)"},
             title="Product Order Percentage", color="percentage",
             color_continuous_scale="blues")
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(yaxis_title="Percentage (%)", xaxis_title="Product Type")
            st.plotly_chart(fig,use_container_width=True)
    elif page == "Cancelled Orders":
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: -60px; '>📦Cancelled Orders</h1>", unsafe_allow_html=True)
        if st.session_state.username=="walid" or st.session_state.username=="ahmed":
            selected_2 = option_menu(
                menu_title=None,
                options=["Add Order", "Search Orders", "View All Orders", "Modify Orders","Delete Orders","Analysis"],
                icons=['cart', 'search', "list-task", 'gear','trash','graph-up'],
                menu_icon="cast",
                default_index=0,
                orientation="horizontal",
                styles={
                    'container': {
                        'width': '100%',
                        'margin': '30',
                        'padding': '0',
                    }
                }
            )
        else:
            selected_2 = option_menu(
                menu_title=None,
                options=["Add Order", "Search Orders", "View All Orders", "Modify Orders","Delete Orders"],
                icons=['cart', 'search', "list-task", 'gear','trash'],
                menu_icon="cast",
                default_index=0,
                orientation="horizontal",
                styles={
                    'container': {
                        'width': '100%',
                        'margin': '30',
                        'padding': '0',
                    }
                }
            )
        st.markdown("")
        st.markdown("")
        if selected_2=="Add Order":
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
                order_price=custom_number_input("Order Price",min_value=0,step=1)
                cancelled_reason=st.selectbox("Reason",reasons_1)
                if "order_products" not in st.session_state:
                    st.session_state.order_products = []
                if "product_count" not in st.session_state:
                    st.session_state.product_count = 1 
                col1, col2 = st.columns([1, 1])
                col_1, col_2,col_3= st.columns([1,1,25])
                with col_1:
                    if st.button("➕"):
                        st.session_state.product_count += 1
                with col_2:
                    if st.button("➖"):
                        st.session_state.product_count -= 1
                        st.session_state.order_products.pop()
                for i in range(st.session_state.product_count):
                    with col1:
                        type_of_product = st.selectbox(f"Type {i+1}", products, key=f"type_{i}")
                    with col2:
                        count_of_product = custom_number_input(
                            f"Count {i+1}", min_value=0, step=1, key=f"count_{i}"
                        )

                    if len(st.session_state.order_products) <= i:
                        st.session_state.order_products.append(
                            {"Type": type_of_product, "Count": count_of_product}
                        )
                    else:
                        st.session_state.order_products[i] = {"Type": type_of_product, "Count": count_of_product}
                order_date = st.date_input("Order Date")
                if st.button("Add Cancelled Order"):
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
                    elif order_price is None or order_price<0:
                        st.error("Order Price is required.")
                    else:
                        conn = create_connection()
                        cursor = conn.cursor()

                        cursor.execute(
                            f"SELECT 1 FROM {cancelled_orders} WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order = cursor.fetchone()
                        cursor.execute(
                            f"SELECT 1 FROM {orders} WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order_1 = cursor.fetchone()
                        cursor.execute(
                            f"SELECT 1 FROM {returned_orders} WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order_2 = cursor.fetchone()
                        if existing_order:
                            st.error("Order Number already exists in Cancelled Orders. Please enter a unique Order Number.")
                        elif existing_order_1:
                            st.error("Order Number already exists in Completed Orders. Please enter a unique Order Number.")
                        elif existing_order_2:
                            st.error("Order Number already exists in Returned Orders. Please enter a unique Order Number.")
                        else:
                            cursor.execute(
                                f"SELECT customer_id FROM {customers} WHERE customer_phone_1 = %s",
                                (corrected_phone_1,)
                            )
                            customer = cursor.fetchone()

                            if customer:
                                customer_id = customer[0]
                            else:
                                cursor.execute(
                                    f"INSERT INTO {customers} (customer_name, customer_phone_1, customer_phone_2, email) VALUES (%s, %s, %s, %s) RETURNING customer_id",
                                    (customer_name, corrected_phone_1, corrected_phone_2, corrected_email)
                                )
                                customer_id = cursor.fetchone()[0]
                            total_count = sum(item["Count"] for item in st.session_state.order_products)
                            products_string = ", ".join([f"{item['Type']}:{item['Count']}" for item in st.session_state.order_products])
                            cursor.execute( f"""
                                                INSERT INTO {cancelled_orders} 
                                                (customer_id, region, order_number,reason,hoodies,order_price,order_date,products) 
                                                VALUES (%s, %s, %s,%s,%s,%s,%s,%s)
                                                """,
                                                (customer_id, region, order_number,cancelled_reason,total_count,order_price,order_date,products_string),
                                            )
                            conn.commit()
                            st.success("Cancelled order added successfully!")
                            log_action(st.session_state.username, "Add Cancelled Order", f"Order ID: {order_number}, Customer: {customer_name}")

                        conn.close()
        elif selected_2=="Search Orders":
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
                        c.email,o.region,o.reason,o.products,o.hoodies,o.order_price,o.order_date
                    FROM {cancelled_orders} o
                    INNER JOIN {customers} c ON o.customer_id = c.customer_id
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
        elif selected_2=="View All Orders":            
            sort_by = st.selectbox("Sort by", ["Order Code"])
            sort_order = st.radio("Sort orders", ["Ascending", "Descending"])
            
            conn = create_connection()
            cursor = conn.cursor()
            sort_column = "CAST(o.order_number AS INTEGER)"
            sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
            
            query = f"""
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                c.email,o.region,o.reason,o.hoodies,o.order_price,o.order_date,o.products
            FROM {cancelled_orders} o
            INNER JOIN {customers} c ON o.customer_id = c.customer_id
            """
            query += f" ORDER BY {sort_column} {sort_direction}"
            
            cursor.execute(query)
            all_orders = cursor.fetchall()
            total_query = f"COALESCE(SUM(hoodies),0), COALESCE(SUM(order_price), 0) FROM {orders}"
            total_query = f"""
            SELECT COUNT(o.order_number), COALESCE(SUM(o.hoodies),0),COALESCE(SUM(o.order_price), 0)
            FROM {cancelled_orders} o
            """
            cursor.execute(total_query)
            total_orders,total_products, total_price = cursor.fetchone()
            conn.close()        
            if all_orders:
                data = []
                for order in all_orders:
                    data.append({
                        "Order Number": order[0],
                        "Date": order[9],
                        "Customer Name": order[1],
                        "Phone 1": order[2],
                        "Phone 2": order[3],
                        "Email": order[4],
                        "Region": order[5],
                        "Reason":order[6],
                        "Products Type":order[10],
                        "Number of Products":order[7],
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

        elif selected_2=="Modify Orders":            
                st.subheader("Select an Order")
                search_order_number = st.text_input("Enter Order Code")
                if search_order_number:
                    conn = create_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute(
                        f"""
                        SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2,
                            c.email, o.region,o.reason,o.hoodies,o.order_price,o.order_date,o.products
                        FROM {cancelled_orders} o
                        INNER JOIN {customers} c ON o.customer_id = c.customer_id
                        WHERE o.order_number = %s
                        """,
                        (search_order_number,)
                    )
                    order_details = cursor.fetchone()

                    if order_details:
                        st.write("Order Details:")
                        st.table([order_details])
                        if order_details[10]:  
                          products_list = [
                            {"Type": p.split(":")[0], "Count": int(p.split(":")[1])}
                            for p in order_details[10].split(", ") if ":" in p
                          ]
                        else:
                          products_list = []
                        st.subheader("Update Order")
                        new_name=st.text_input("Customer Name",value=order_details[1])
                        new_phone1=st.text_input("Customer Phone 1",value=order_details[2])
                        new_phone2=st.text_input("Customer Phone 1",value=order_details[3])
                        new_email=st.text_input("Email",value=order_details[4])
                        new_region = st.selectbox("Region",egypt_governorates,index=egypt_governorates.index(order_details[5]))
                        new_cancel_reason=st.selectbox("Reason",reasons_1,index=reasons_1.index(order_details[6]))
                        new_cancel_price=custom_number_input("Order Price",value=order_details[8])
                        new_date=st.date_input("Order Date",value=order_details[9])
                        if not products_list:
                           num_products = custom_number_input("Enter the number of products:", min_value=0,step=1)
                           fake_products = []
                           for i in range(num_products):
                             product_type = st.selectbox(f"Enter product type for item {i+1}:",products,key=f"type_{i}")
                             count = custom_number_input(f"Enter count for {product_type}:", min_value=0, step=1, key=f"count_{i}")
                             if product_type:  
                               fake_products.append({"Type": product_type, "Count": count})
                           products_list = fake_products
                        if "re_modified_products" not in st.session_state:
                            st.session_state.re_modified_products = products_list
                        for i, product in enumerate(st.session_state.re_modified_products):
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                st.session_state.re_modified_products[i]["Type"] = st.selectbox(
                                    f"Type {i+1}", products, key=f"product_type_{i}", index=products.index(product["Type"])
                                )
                            with col2:
                                st.session_state.re_modified_products[i]["Count"] = custom_number_input(
                                    f"Count {i+1}", min_value=0, step=1, key=f"product_count_{i}", value=product["Count"]
                                )
                            with col3:
                                if st.button(f"Remove Product {i+1}", key=f"remove_product_{i}"):
                                    st.session_state.re_modified_products.pop(i)
                                    st.rerun()
                        if "re_new_products" not in st.session_state:
                            st.session_state.re_new_products = []

                        if st.button("Add More Products"):
                            st.session_state.re_new_products.append({"Type": "", "Count": 1})

                        for i, product in enumerate(st.session_state.re_new_products):
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                st.session_state.re_new_products[i]["Type"] = st.selectbox(
                                    f"New Type {i+1}", products, key=f"new_product_type_{i}"
                                )
                            with col2:
                                st.session_state.re_new_products[i]["Count"] = custom_number_input(
                                    f"New Count {i+1}", min_value=0, step=1, key=f"new_product_count_{i}", value=product["Count"]
                                )
                            with col3:
                                if st.button(f"Remove New Product {i+1}", key=f"remove_new_product_{i}"):
                                    st.session_state.re_new_products.pop(i)
                                    st.rerun()

                        if st.button("Update Order"):
                                updated_products = ", ".join(
                                        [f"{item['Type']}:{item['Count']}" for item in (st.session_state.re_modified_products + st.session_state.re_new_products)]
                                    )
                                cursor.execute(
                                    f"""
                                    UPDATE {customers}
                                    SET customer_name = %s, customer_phone_1 = %s, customer_phone_2 = %s, email = %s
                                    WHERE customer_id = (
                                        SELECT customer_id 
                                        FROM {cancelled_orders} 
                                        WHERE order_number = %s
                                    )
                                    """,
                                    (new_name, new_phone1, new_phone2, new_email, search_order_number)
                                )
                                
                                cursor.execute(
                                    f"""
                                    UPDATE {cancelled_orders}
                                    SET region = %s,reason=%s,hoodies=%s,order_price=%s,order_date=%s,products=%s
                                    WHERE order_number = %s
                                    """,
                                    (new_region, new_cancel_reason,sum(item["Count"] for item in (st.session_state.re_modified_products + st.session_state.re_new_products)), new_cancel_price, new_date, updated_products, search_order_number)
                                )

                                conn.commit()
                                del st.session_state.re_modified_products
                                del st.session_state.re_new_products
                                st.success("Order updated successfully!")
                                log_action(st.session_state.username, "Update Cancelled Order", f"Order ID: {search_order_number}, Customer: {new_name}")

                        st.subheader("Remove Order")
                        with st.form("delete_order_form"):
                            delete_password = st.text_input("Enter Password to Confirm Deletion", type="password")
                            delete_submit = st.form_submit_button("Delete Order")

                            if delete_submit:
                                if delete_password == "admin":
                                    cursor.execute(
                                        f"DELETE FROM {cancelled_orders} WHERE order_number = %s", (search_order_number,)
                                    )
                                    conn.commit()
                                    st.success("Order deleted successfully!")
                                    log_action(st.session_state.username, "Delete Cancelled Order", f"Order ID: {search_order_number}, Customer: {new_name}")
                                else:
                                    st.error("Incorrect password. Order deletion canceled.")
                    else:
                            st.write("No order found with the given Order Number.")
                    conn.close()
        elif selected_2=="Delete Orders":
            query = f"""
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                c.email,o.region,o.reason,o.hoodies,o.order_price,o.order_date,o.products
            FROM {cancelled_orders} o
            INNER JOIN {customers} c ON o.customer_id = c.customer_id
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
                        "Order Number": order[0],
                        "Date": order[9],
                        "Customer Name": order[1],
                        "Phone 1": order[2],
                        "Phone 2": order[3],
                        "Email": order[4],
                        "Region": order[5],
                        "Reason":order[6],
                        "Number of Products":order[7],
                        "Order Price":order[8],
                    }
                    for order in all_orders
                ]
                df = pd.DataFrame(orders_data)
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_selection("multiple", use_checkbox=True, header_checkbox=True)
                gb.configure_column("Order Number", sort="asc")  
                grid_options = gb.build()
                grid_response = AgGrid(
                        df,
                        gridOptions=grid_options,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        height=400,
                        theme="streamlit",
                        fit_columns_on_grid_load=True,
                        key="grid",
                )
                selected_rows = grid_response["selected_rows"]

                if selected_rows is None or selected_rows.empty:
                    st.warning("No orders selected.")
                else:
                    st.write("Selected Rows:", selected_rows)  
                    if "Order Number" in selected_rows.columns:
                        selected_order_numbers = selected_rows["Order Number"].astype(str).tolist()
                        selected_customers = selected_rows["Customer Name"].astype(str).tolist()
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

                            delete_query = f"DELETE FROM {cancelled_orders} WHERE order_number IN %s"
                            try:
                                with create_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute(delete_query, (orders_tuple,))
                                    conn.commit()
                                    st.success(f"Successfully deleted {len(selected_order_numbers)} orders.")
                                    log_action(st.session_state.username, "Delete Completed Order", f"Order ID: {selected_order_numbers}, Customers: {selected_customers}")
                            except Exception as e:
                                st.error(f"Error deleting orders: {e}")
        elif selected_2=="Analysis":
            col1, col2, col3,col4= st.columns([1, 1, 1,1])
            def metric_card_with_icon(title, content, description,info):
                st.markdown(
                    f"""
                    <div style="background-color: #fff; border: 1px solid #ddd; border-radius: 15px; padding: 15px; 
                                text-align: left; box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.1); position: relative; color: #000; 
                                width: 100%; max-width: 300px;">
                        <div style="position: absolute; top: 8px; right: 8px;" title="{info}">
                            <div style="width: 20px; height: 20px; border: 2px solid #000; border-radius: 50%; display: flex; 
                                        align-items: center; justify-content: center; font-size: 12px; font-weight: bold; color: #000; 
                                        cursor: pointer;">
                                i
                            </div>
                        </div>
                        <h4 style="margin: 5px 10px 0 10px; font-size: 14px; color: #000; padding-left: 10px;">{title}</h4>
                        <p style="margin: -10px 10px 0 10px; font-size: 28px; font-weight: bold; color: #000; padding-left: 10px;">{content}</p>
                        <p style="margin: -7px 10px 5px 10px; font-size: 12px; color: #777; padding-left: 10px;">{description}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            conn = create_connection()
            cursor = conn.cursor()

            total_query = f"""
                SELECT 
                    COUNT(o.order_number) AS total_orders, 
                    COALESCE(SUM(o.hoodies), 0) AS total_products,
                    COALESCE(SUM(o.order_price), 0) AS total_prices
                FROM {cancelled_orders} o
                """
            cursor.execute(total_query)
            total_orders, total_products, total_prices= cursor.fetchone()

            query = f"""
                SELECT 
                    o.region, 
                    COUNT(o.order_number) AS total_orders 
                FROM {cancelled_orders} o
                GROUP BY o.region
                ORDER BY total_orders DESC
                """
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=["Region", "Total Orders"])
            total_completed_query=f"""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM {orders} o
            """
            cursor.execute(total_completed_query)
            total_completed=cursor.fetchone()[0]
            total_returned_query=f"""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM {returned_orders} o
            """
            cursor.execute(total_returned_query)
            total_returned=cursor.fetchone()[0]
            total_shipping_query=f"""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM {shipping} o
            """
            cursor.execute(total_shipping_query)
            total_shipping=cursor.fetchone()[0]
            reason_query = f"""
                SELECT 
                    o.reason AS reason,
                    COUNT(o.order_number) AS Total_Orders
                FROM {cancelled_orders} o
                GROUP BY o.reason
                ORDER BY Total_Orders DESC
                """
            cursor.execute(reason_query)
            reason_data = cursor.fetchall()
            df_reason = pd.DataFrame(reason_data, columns=["Reason", "Total Orders"])
            total_orders_all = df_reason['Total Orders'].sum()
            df_reason['Percentage'] = (df_reason['Total Orders'] / total_orders_all) * 100
            date_query = f"""
                        SELECT 
                            o.order_date, 
                            COUNT(o.order_number) AS total_orders,
                            SUM(o.order_price) AS total_sales
                        FROM {cancelled_orders} o
                        GROUP BY o.order_date
                        ORDER BY o.order_date
                    """
            cursor.execute(date_query)
            date_data = cursor.fetchall()
            df_date = pd.DataFrame(date_data, columns=["Date", "Total Orders", "Total Sales"])
            df_date["Date"] = pd.to_datetime(df_date["Date"])  
            df_date.sort_values(by="Date", inplace=True)  
            query = f"""
                    WITH product_orders AS (
                        SELECT
                            o.order_number,
                            TRIM(SPLIT_PART(regexp_split_to_table(o.products, ','), ':', 1)) AS product_name
                        FROM {cancelled_orders} o
                    ),
                    distinct_orders AS (
                        SELECT COUNT(DISTINCT order_number) AS total_orders FROM {cancelled_orders}
                    )
                    SELECT 
                        product_name,
                        COUNT(DISTINCT order_number) AS order_count,
                        (COUNT(DISTINCT order_number) * 100.0) / (SELECT total_orders FROM distinct_orders) AS percentage
                    FROM product_orders
                    WHERE product_name IS NOT NULL
                    GROUP BY product_name
                    ORDER BY percentage DESC;

                    """
            df_products_percentage = pd.read_sql(query, conn)
            conn.close()
            percentage_cancelled = total_orders / (total_orders + total_completed + total_returned)
            percentage_cancelled_1 = total_orders / (total_orders + total_completed + total_returned+total_shipping)
            percentage__cancelled = total_orders / (total_orders + total_returned)

            with col1:
                    metric_card_with_icon(
                        "Total Orders", 
                        f"{total_orders:,}","", 
                        "The total number of ordes."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                    "Percentage of Cancelled Orders(Cancelled & Returned only)", 
                    f"{percentage__cancelled * 100:.2f}%", "", 
                    """The percentage of cancelled orders out of cancelled and returned orders only.
                    نسبة الاوردرات اللي اتلغت بالنسبه للي اتلغت ورجعت بس"""
                    )
            with col2:
                    metric_card_with_icon(
                        "Total Products", 
                        f"{total_products:,}","", 
                        "The total number of products cancelled."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                    "Percentage of Cancelled Orders(problems)", 
                    f"{percentage_cancelled_1 * 100:.2f}%", "", 
                    """The percentage of cancelled orders out of total orders with problems.
                    نسبة الاوردرات اللي اتلغت بالنسبه لكل الاوردرات"""
                )
            with col3:
                    metric_card_with_icon(
                        "Total Price", 
                        f"{int(total_prices):,}".replace(",", "."),"",
                        "The total revenue generated from all orders."
                    )
            with col4:
                metric_card_with_icon(
                    "Percentage of Cancelled Orders", 
                    f"{percentage_cancelled * 100:.2f}%", "", 
                    """The percentage of cancelled orders out of total orders.
                    نسبة الاوردرات اللي اتلغت بالنسبه لكل الاوردرات"""
                )

            fig_cancelled = px.bar(
                df, 
                x="Region", 
                y="Total Orders", 
                title="Total Orders by Region",
                labels={"Region": "Region", "Total Orders": "Number of Orders"},
                text="Total Orders",
                color="Region", 
                height=600
            )

            fig_cancelled.update_traces(texttemplate='%{text}', textposition='outside')
            fig_cancelled.update_layout(
                xaxis_title="Region",
                yaxis_title="Total Orders",
                uniformtext_minsize=8,
                uniformtext_mode='hide'
            )
            st.markdown("")
            st.plotly_chart(fig_cancelled, use_container_width=True)
            fig_reason = px.bar(
            df_reason, 
            x="Reason", 
            y="Total Orders", 
            title="Total Orders by Reason",
            labels={"Reason": "Reason", "Total Orders": "Number of Orders"},
            text=df_reason['Percentage'].apply(lambda x: f"{x:.2f}%"), 
            color="Reason",  
            height=600
            )

            fig_reason.update_traces(texttemplate='%{text}', textposition='outside')
            fig_reason.update_layout(
            xaxis_title="Reason",
            yaxis_title="Total Orders",
            uniformtext_minsize=8,
            uniformtext_mode='hide'
            )
            st.plotly_chart(fig_reason, use_container_width=True)
            fig = px.line(
                df_date, 
                x="Date", 
                y="Total Orders", 
                title="Orders Over Time",
                labels={"Date": "Date", "Total Orders": "Number of Orders"}
            )
            st.plotly_chart(fig, use_container_width=True)
            fig = px.bar(df_products_percentage, x="product_name", y="percentage", 
             text="percentage", labels={"product_name": "Product Type", "percentage": "Percentage (%)"},
             title="Product Order Percentage", color="percentage",
             color_continuous_scale="blues")
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(yaxis_title="Percentage (%)", xaxis_title="Product Type")
            st.plotly_chart(fig,use_container_width=True)
    elif page == "Returned Orders":
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: -60px; '>📦Returned Orders</h1>", unsafe_allow_html=True)
        if st.session_state.username=="walid" or st.session_state.username=="ahmed":
            selected_1 = option_menu(
                menu_title=None,
                options=["Add Order", "Search Orders", "View All Orders", 'Modify Orders','Delete Orders','Analysis'],
                icons=['cart', 'search', "list-task", 'gear','trash','graph-up'],
                menu_icon="cast",
                default_index=0,
                orientation="horizontal",
                styles={
                    'container': {
                        'width': '100%',
                        'margin': '30',
                        'padding': '0',
                    }
                }
            )
        else:
            selected_1 = option_menu(
                menu_title=None,
                options=["Add Order", "Search Orders", "View All Orders", 'Modify Orders','Delete Orders'],
                icons=['cart', 'search', "list-task", 'gear','trash'],
                menu_icon="cast",
                default_index=0,
                orientation="horizontal",
                styles={
                    'container': {
                        'width': '100%',
                        'margin': '30',
                        'padding': '0',
                    }
                }
            )
        st.markdown("")
        st.markdown("")
        if selected_1=="Add Order":
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
            def reset_re_order_session_states():
                    st.session_state.re_order_products = []
                    st.session_state.re_product_count = 1

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
            ship_company = st.selectbox("Shipping Company",company)
            region = st.selectbox("Region", egypt_governorates)
            order_number = st.text_input("Order Code")
            status=st.selectbox("Status",["Go Only","Go And Back"])
            reason=st.selectbox("Reason",["Customer","Delivery Man","Quality","Size","Team"])
            if "re_order_products" not in st.session_state:
                    st.session_state.re_order_products = []
            if "re_product_count" not in st.session_state:
                    st.session_state.re_product_count = 1 
            col1, col2 = st.columns([1, 1])
            col_1, col_2,col_3= st.columns([1,1,25])
            with col_1:
                if st.button("➕"):
                    st.session_state.re_product_count += 1
            with col_2:
                if st.button("➖"):
                    st.session_state.re_product_count -= 1
                    st.session_state.re_order_products.pop()
            for i in range(st.session_state.re_product_count):
                with col1:
                    type_of_product = st.selectbox(f"Type {i+1}", products, key=f"type_{i}")
                with col2:
                    count_of_product = custom_number_input(
                        f"Count {i+1}", min_value=0, step=1, key=f"count_{i}"
                    )

                if len(st.session_state.re_order_products) <= i:
                    st.session_state.re_order_products.append(
                        {"Type": type_of_product, "Count": count_of_product}
                    )
                else:
                    st.session_state.re_order_products[i] = {"Type": type_of_product, "Count": count_of_product}
            order_price = custom_number_input("Order Price", min_value=0,step=1)
            order_date = st.date_input("Order Date")
            customer_shipping_price=custom_number_input("Shipping Price paid By customer", min_value=0,step=1)
            shipping_price = custom_number_input("Shipping Price Paid To Company", min_value=0,step=1)
            if st.button("Add Returned Order"):
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
                    elif order_price is None or order_price<0:
                        st.error("Order Price is required.")
                    elif shipping_price is None or shipping_price<0:
                        st.error("Shipping Price is required.")
                    elif customer_shipping_price is None or customer_shipping_price<0:
                        st.error("Shipping price paid by customer is required.")
                    
                    else:
                        conn = create_connection()
                        cursor = conn.cursor()

                        cursor.execute(
                            f"SELECT 1 FROM {returned_orders} WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order = cursor.fetchone()
                        cursor.execute(
                            f"SELECT 1 FROM {cancelled_orders} WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order_1 = cursor.fetchone()
                        cursor.execute(
                            f"SELECT 1 FROM {orders} WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order_2 = cursor.fetchone()
                        if existing_order:
                            st.error("Order Number already exists in Returned Orders. Please enter a unique Order Number.")
                        elif existing_order_1:
                            st.error("Order Number already exists in Cancelled Orders. Please enter a unique Order Number.")
                        elif existing_order_2:
                            st.error("Order Number already exists in Completed Orders. Please enter a unique Order Number.")
                        else:
                            cursor.execute(
                                f"SELECT customer_id FROM {customers} WHERE customer_phone_1 = %s",
                                (corrected_phone_1,)
                            )
                            customer = cursor.fetchone()

                            if customer:
                                customer_id = customer[0]
                            else:
                                cursor.execute(
                                    f"INSERT INTO {customers} (customer_name, customer_phone_1, customer_phone_2, email) VALUES (%s, %s, %s, %s) RETURNING customer_id",
                                    (customer_name, corrected_phone_1, corrected_phone_2, corrected_email)
                                )
                                customer_id = cursor.fetchone()[0]
                            total_count = sum(item["Count"] for item in st.session_state.re_order_products)
                            products_string = ", ".join([f"{item['Type']}:{item['Count']}" for item in st.session_state.re_order_products])
                            cursor.execute(
                                f"INSERT INTO {returned_orders} (customer_id, ship_company, region, order_number,reason,hoodies,order_price,shipping_price,status,products,order_date,customer_shipping_price) VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                (customer_id, ship_company, region, order_number,reason,total_count,order_price,shipping_price,status,products_string,order_date,customer_shipping_price)
                            )

                            conn.commit()
                            st.success("Returned order added successfully!")
                            log_action(st.session_state.username, "Add Returned Order", f"Order ID: {order_number}, Customer: {customer_name}")
                            reset_re_order_session_states()  
                        conn.close()
        elif selected_1=="Search Orders":
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
                        c.email, o.ship_company, o.region,o.reason,o.hoodies,o.order_price,o.shipping_price,o.products,o.order_date,o.customer_shipping_price
                    FROM {returned_orders} o
                    INNER JOIN {customers} c ON o.customer_id = c.customer_id
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
        elif selected_1=="View All Orders":            
            sort_by = st.selectbox("Sort by", ["Order Code"])
            sort_order = st.radio("Sort orders", ["Ascending", "Descending"])
            
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT DISTINCT ship_company FROM {returned_orders}")
            ship_companies = [row[0] for row in cursor.fetchall()]
            selected_ship_company = st.selectbox("Filter by Shipping Company", ["All"] + ship_companies)
            sort_column = "CAST(o.order_number AS INTEGER)"
            sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
            
            query = f"""
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                c.email, o.ship_company, o.region, o.reason,o.hoodies,o.order_price,o.shipping_price,o.products,o.order_date,o.customer_shipping_price
            FROM {returned_orders} o
            INNER JOIN {customers} c ON o.customer_id = c.customer_id
            """
            if selected_ship_company != "All":
                query += f" WHERE o.ship_company = '{selected_ship_company}'"
            
            query += f" ORDER BY {sort_column} {sort_direction}"
                
            cursor.execute(query)
            all_orders = cursor.fetchall()
            total_query = f"""
            SELECT COUNT(o.order_number), COALESCE(SUM(o.hoodies),0),COALESCE(SUM(o.order_price), 0),COALESCE(SUM(o.shipping_price), 0)
            FROM {returned_orders} o
            """
            if selected_ship_company != "All":
                total_query += f" WHERE ship_company = '{selected_ship_company}'"
            cursor.execute(total_query)
            total_orders,total_products, total_price,total_shipping_price = cursor.fetchone()
            conn.close()
            
            if all_orders:
                data = []
                for order in all_orders:
                    data.append({
                        "Order Number": order[0],
                        "Date": order[12],
                        "Customer Name": order[1],
                        "Phone 1": order[2],
                        "Phone 2": order[3],
                        "Email": order[4],
                        "Shipping Company": order[5],
                        "Region": order[6],
                        "Reason": order[7],
                        "Number Of Products":order[8],
                        "Order Price":order[9],
                        "Shipping Price Paid To Company":order[10],
                        "Order Profit": (order[9] or 0) - (order[10] or 0),
                        "Type of Products": order[11],
                        "Actual Shipping Cost": (order[10] or 0) - (order[13] or 0),
                    })
                df = pd.DataFrame(data)
                st.write("All Orders:")
                st.dataframe(df)
                st.write(f"**Total Orders:** {total_orders}")
                st.write(f"**Total Price:** {int(total_price):,}".replace(",", "."))
                st.write(f"**Total Shipping Price:** {int(total_shipping_price):,}".replace(",", "."))
                st.write(f"**Total Actual Shipping Cost:** {int(df['Actual Shipping Cost'].sum()):,}".replace(',', '.'))
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

        elif selected_1=="Modify Orders":   
                Status=["Go Only","Go And Back"]   
                Reasons=["Customer","Delvirey Man","Quality","Size","Team"]     
                st.subheader("Select an Order")
                search_order_number = st.text_input("Enter Order Code")

                if search_order_number:
                    conn = create_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute(
                        f"""
                        SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2,
                            c.email, o.ship_company, o.region,o.reason,o.hoodies,o.order_price,o.shipping_price,o.order_date,o.status,o.products,o.customer_shipping_price
                        FROM {returned_orders} o
                        INNER JOIN {customers} c ON o.customer_id = c.customer_id
                        WHERE o.order_number = %s
                        """,
                        (search_order_number,)
                    )
                    order_details = cursor.fetchone()

                    if order_details:
                        st.write("Order Details:")
                        st.table([order_details])
                        if order_details[13]:
                          products_list = [
                            {"Type": p.split(":")[0], "Count": int(p.split(":")[1])}
                            for p in order_details[13].split(", ") if ":" in p
                          ]
                        else:
                          products_list = []
                        st.subheader("Update Order")
                        new_name=st.text_input("Customer Name",value=order_details[1])
                        new_phone1=st.text_input("Customer Phone 1",value=order_details[2])
                        new_phone2=st.text_input("Customer Phone 2",value=order_details[3])
                        new_email=st.text_input("Email",value=order_details[4])
                        new_ship_company = st.selectbox("Shipping Company",company,index=company.index(order_details[5]))
                        new_region = st.selectbox("Region",egypt_governorates,index=egypt_governorates.index(order_details[6]))
                        new_status=st.selectbox("Status",Status,Status.index(order_details[12]))
                        new_reason = st.selectbox("Reason",Reasons,Reasons.index(order_details[7]))
                        new_price=custom_number_input("Order Price",value=order_details[9])
                        new_customer_shipping_price=custom_number_input("Shipping price paid By customer",value=order_details[14])
                        new_shipping_price=custom_number_input("Shipping Price Paid To Company",value=order_details[10])
                        new_date=st.date_input("Order Date",value=order_details[11])
                        if not products_list:
                           num_products = custom_number_input("Enter the number of products:", min_value=0,step=1)
                           fake_products = []
                           for i in range(num_products):
                             product_type = st.selectbox(f"Enter product type for item {i+1}:",products,key=f"type_{i}")
                             count = custom_number_input(f"Enter count for {product_type}:", min_value=0, step=1, key=f"count_{i}")
                             if product_type:  
                               fake_products.append({"Type": product_type, "Count": count})
                           products_list = fake_products
                        if "ca_modified_products" not in st.session_state:
                            st.session_state.ca_modified_products = products_list
                        for i, product in enumerate(st.session_state.ca_modified_products):
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                st.session_state.ca_modified_products[i]["Type"] = st.selectbox(
                                    f"Type {i+1}", products, key=f"product_type_{i}", index=products.index(product["Type"])
                                )
                            with col2:
                                st.session_state.ca_modified_products[i]["Count"] = custom_number_input(
                                    f"Count {i+1}", min_value=0, step=1, key=f"product_count_{i}", value=product["Count"]
                                )
                            with col3:
                                if st.button(f"Remove Product {i+1}", key=f"remove_product_{i}"):
                                    st.session_state.ca_modified_products.pop(i)
                                    st.rerun()
                        if "ca_new_products" not in st.session_state:
                            st.session_state.ca_new_products = []

                        if st.button("Add More Products"):
                            st.session_state.ca_new_products.append({"Type": "", "Count": 1})

                        for i, product in enumerate(st.session_state.ca_new_products):
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                st.session_state.ca_new_products[i]["Type"] = st.selectbox(
                                    f"New Type {i+1}", products, key=f"new_product_type_{i}"
                                )
                            with col2:
                                st.session_state.ca_new_products[i]["Count"] = custom_number_input(
                                    f"New Count {i+1}", min_value=0, step=1, key=f"new_product_count_{i}", value=product["Count"]
                                )
                            with col3:
                                if st.button(f"Remove New Product {i+1}", key=f"remove_new_product_{i}"):
                                    st.session_state.ca_new_products.pop(i)
                                    st.rerun()
                        if st.button("Update Order"):
                                updated_products = ", ".join(
                                    [f"{item['Type']}:{item['Count']}" for item in (st.session_state.ca_modified_products + st.session_state.ca_new_products)]
                                )
                                cursor.execute(
                                    f"""
                                    UPDATE {customers}
                                    SET customer_name = %s, customer_phone_1 = %s, customer_phone_2 = %s, email = %s
                                    WHERE customer_id = (
                                        SELECT customer_id 
                                        FROM {returned_orders} 
                                        WHERE order_number = %s
                                    )
                                    """,
                                    (new_name, new_phone1, new_phone2, new_email, search_order_number)
                                )
                                
                                cursor.execute(
                                    f"""
                                    UPDATE {returned_orders}
                                    SET ship_company = %s, region = %s,reason=%s,hoodies=%s,order_price=%s,shipping_price=%s,order_date=%s,status=%s,products=%s,customer_shipping_price=%s
                                    WHERE order_number = %s
                                    """,
                                    (new_ship_company, new_region, new_reason,sum(item["Count"] for item in (st.session_state.ca_modified_products + st.session_state.ca_new_products)), new_price, new_shipping_price, new_date, new_status,updated_products, new_customer_shipping_price, search_order_number)
                                )
                                conn.commit()
                                del st.session_state.ca_modified_products
                                del st.session_state.ca_new_products
                                st.success("Order updated successfully!")
                                log_action(st.session_state.username, "Update Returned Order", f"Order ID: {search_order_number}, Customer: {new_name}")

                        st.subheader("Remove Order")
                        with st.form("delete_order_form"):
                            delete_password = st.text_input("Enter Password to Confirm Deletion", type="password")
                            delete_submit = st.form_submit_button("Delete Order")

                            if delete_submit:
                                if delete_password == "admin":
                                    cursor.execute(
                                        f"DELETE FROM {returned_orders} WHERE order_number = %s", (search_order_number,)
                                    )
                                    conn.commit()
                                    st.success("Order deleted successfully!")
                                    log_action(st.session_state.username, "Delete Returned Order", f"Order ID: {search_order_number}, Customer: {new_name}")
                                else:
                                    st.error("Incorrect password. Order deletion canceled.")
                    else:
                        st.write("No order found with the given Order Number.")
                    
                    conn.close()
        elif selected_1=="Delete Orders":
            query = f"""
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                c.email, o.ship_company, o.region, o.reason,o.hoodies,o.order_price,o.shipping_price,o.order_date,o.customer_shipping_price
            FROM {returned_orders} o
            INNER JOIN {customers} c ON o.customer_id = c.customer_id
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
                        "Order Number": order[0],
                        "Date": order[11],
                        "Customer Name": order[1],
                        "Phone 1": order[2],
                        "Phone 2": order[3],
                        "Email": order[4],
                        "Shipping Company": order[5],
                        "Region": order[6],
                        "Reason": order[7],
                        "Number Of Products":order[8],
                        "Order Price":order[9],
                        "Shipping Price in Shipping Company":order[10],
                        "Order Profit": (order[9] or 0) - (order[10] or 0),
                        "Actual Shipping Cost": (order[10] or 0) - (order[12] or 0),
                    }
                    for order in all_orders
                ]
                df = pd.DataFrame(orders_data)
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_selection("multiple", use_checkbox=True, header_checkbox=True)
                gb.configure_column("Order Number", sort="asc")  
                grid_options = gb.build()
                grid_response = AgGrid(
                        df,
                        gridOptions=grid_options,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        height=400,
                        theme="streamlit",
                        fit_columns_on_grid_load=True,
                        key="grid",
                )
                selected_rows = grid_response["selected_rows"]

                if selected_rows is None or selected_rows.empty:
                    st.warning("No orders selected.")
                else:
                    st.write("Selected Rows:", selected_rows)  
                    if "Order Number" in selected_rows.columns:
                        selected_order_numbers = selected_rows["Order Number"].astype(str).tolist()
                        selected_customers = selected_rows["Customer Name"].astype(str).tolist()
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

                            delete_query = f"DELETE FROM {returned_orders} WHERE order_number IN %s"
                            try:
                                with create_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute(delete_query, (orders_tuple,))
                                    conn.commit()
                                    st.success(f"Successfully deleted {len(selected_order_numbers)} orders.")
                                    log_action(st.session_state.username, "Delete Completed Order", f"Order ID: {selected_order_numbers}, Customers: {selected_customers}")
                            except Exception as e:
                                st.error(f"Error deleting orders: {e}")
        elif selected_1=="Analysis":
            col1, col2, col3,col4= st.columns([1, 1, 1,1])
            def metric_card_with_icon(title, content, description,info):
                st.markdown(
                    f"""
                    <div style="background-color: #fff; border: 1px solid #ddd; border-radius: 15px; padding: 15px; 
                                text-align: left; box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.1); position: relative; color: #000; 
                                width: 100%; max-width: 300px;">
                        <div style="position: absolute; top: 8px; right: 8px;" title="{info}">
                            <div style="width: 20px; height: 20px; border: 2px solid #000; border-radius: 50%; display: flex; 
                                        align-items: center; justify-content: center; font-size: 12px; font-weight: bold; color: #000; 
                                        cursor: pointer;">
                                i
                            </div>
                        </div>
                        <h4 style="margin: 5px 10px 0 10px; font-size: 14px; color: #000; padding-left: 10px;">{title}</h4>
                        <p style="margin: -10px 10px 0 10px; font-size: 28px; font-weight: bold; color: #000; padding-left: 10px;">{content}</p>
                        <p style="margin: -7px 10px 5px 10px; font-size: 12px; color: #777; padding-left: 10px;">{description}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            conn = create_connection()
            cursor = conn.cursor()

            total_query = f"""
                SELECT 
                    COUNT(o.order_number) AS total_orders, 
                    COALESCE(SUM(o.hoodies), 0) AS total_products,
                    COALESCE(SUM(o.order_price), 0) AS total_prices,
                    COALESCE(SUM(o.shipping_price), 0) AS total_shipping_prices,
                    COALESCE(SUM(o.customer_shipping_price), 0) AS total_shipping_cutomer_prices,
                    COALESCE(SUM(CASE WHEN o.status = 'Go Only' THEN o.shipping_price ELSE 0 END), 0)-COALESCE(SUM(CASE WHEN o.status = 'Go Only' THEN o.customer_shipping_price ELSE 0 END), 0) AS total_shipping_prices_go,
                    COALESCE(SUM(CASE WHEN o.status = 'Go And Back' THEN o.shipping_price ELSE 0 END), 0)-COALESCE(SUM(CASE WHEN o.status = 'Go And Back' THEN o.customer_shipping_price ELSE 0 END), 0) AS total_shipping_prices_back
                FROM {returned_orders} o
                """
            cursor.execute(total_query)
            total_orders, total_products, total_prices, total_shipping_prices,total_shipping_cutomer_prices,total_shipping_prices_go,total_shipping_prices_back = cursor.fetchone()
            total_shipping_cost=total_shipping_prices
            total_shipping_prices=total_shipping_prices-total_shipping_cutomer_prices
            total_profit = total_prices - total_shipping_cost
            query = f"""
                SELECT 
                    o.region, 
                    COUNT(o.order_number) AS total_orders 
                FROM {returned_orders} o
                GROUP BY o.region
                ORDER BY total_orders DESC
                """
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=["Region", "Total Orders"])
            total_orders_region = df['Total Orders'].sum()
            df['Percentage'] = (df['Total Orders'] / total_orders_region) * 100
            shipping_company_query = f"""
                SELECT 
                    o.ship_company AS Shipping_Company,
                    COUNT(o.order_number) AS Total_Orders
                FROM {returned_orders} o
                GROUP BY o.ship_company
                ORDER BY Total_Orders DESC
                """
            cursor.execute(shipping_company_query)
            shipping_data = cursor.fetchall()
            df_shipping = pd.DataFrame(shipping_data, columns=["Shipping Company", "Total Orders"])
            total_orders_shipping = df_shipping['Total Orders'].sum()
            df_shipping['Percentage'] = (df_shipping['Total Orders'] / total_orders_shipping) * 100
            total_cancelled_query=f"""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM {cancelled_orders} o
            """
            cursor.execute(total_cancelled_query)
            total_cancelled=cursor.fetchone()[0]
            total_completeed_query=f"""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM {orders} o
            """
            cursor.execute(total_completeed_query)
            total_comp=cursor.fetchone()[0]
            total_shipping_query=f"""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM {shipping} o
            """
            cursor.execute(total_shipping_query)
            total_shipping=cursor.fetchone()[0]
            reason_query = f"""
                SELECT 
                    o.reason AS reason,
                    COUNT(o.order_number) AS Total_Orders
                FROM {returned_orders} o
                GROUP BY o.reason
                ORDER BY Total_Orders DESC
                """
            cursor.execute(reason_query)
            reason_data = cursor.fetchall()
            df_reason = pd.DataFrame(reason_data, columns=["Reason", "Total Orders"])
            total_orders_all = df_reason['Total Orders'].sum()
            df_reason['Percentage'] = (df_reason['Total Orders'] / total_orders_all) * 100
            status_query = f"""
                SELECT 
                    o.status AS status,
                    COUNT(o.order_number) AS Total_Orders
                FROM {returned_orders} o
                GROUP BY o.status
                ORDER BY Total_Orders DESC
                """
            cursor.execute(status_query)
            status_data = cursor.fetchall()
            df_status = pd.DataFrame(status_data, columns=["Status", "Total Orders"])
            total_orders_all = df_reason['Total Orders'].sum()
            df_status['Percentage'] = (df_status['Total Orders'] / total_orders_all) * 100
            date_query = f"""
                        SELECT 
                            o.order_date, 
                            COUNT(o.order_number) AS total_orders,
                            SUM(o.order_price) AS total_sales
                        FROM {returned_orders} o
                        GROUP BY o.order_date
                        ORDER BY o.order_date
                    """
            cursor.execute(date_query)
            date_data = cursor.fetchall()
            df_date = pd.DataFrame(date_data, columns=["Date", "Total Orders", "Total Sales"])
            df_date["Date"] = pd.to_datetime(df_date["Date"]) 
            df_date.sort_values(by="Date", inplace=True) 

            def parse_products(products_str):
                product_items = re.findall(r'([a-zA-Z\s]+):(\d+)', products_str)
                products_dict = {item[0].strip(): int(item[1]) for item in product_items}
                return products_dict

            query = f"""
            SELECT 
                o.order_number,
                o.products,
                o.shipping_price-o.customer_shipping_price
            FROM {returned_orders} o
            """
            cursor.execute(query)
            data = cursor.fetchall()

            product_shipping = {}

            for order in data:
                order_number, products_str, total_shipping_price = order
                if not products_str:
                    continue
                products_dict = parse_products(products_str) 
                total_quantity = sum(products_dict.values()) 

                for product_type, quantity in products_dict.items():
                    shipping_price_for_product = (quantity / total_quantity)

                    if product_type in product_shipping:
                        product_shipping[product_type] += shipping_price_for_product
                    else:
                        product_shipping[product_type] = shipping_price_for_product

            df__shipping = pd.DataFrame(product_shipping.items(), columns=["Product Type", "Total Shipping Price"])
            df__shipping = df__shipping.sort_values(by="Total Shipping Price", ascending=False)
            total_shipping_cost = df__shipping["Total Shipping Price"].sum()
            df__shipping["Percentage"] = (df__shipping["Total Shipping Price"] / total_shipping_cost) * 100
            shipping_company_query = f"""
                SELECT 
                    o.status AS Status,
                    SUM(o.shipping_price)-SUM(o.customer_shipping_price) AS Total_Shipping_Cost
                FROM {returned_orders} o
                GROUP BY o.status
                ORDER BY Total_Shipping_Cost DESC
            """
            cursor.execute(shipping_company_query)
            shipping_data = cursor.fetchall()

            df___shipping = pd.DataFrame(shipping_data, columns=["Status", "Total Shipping Cost"])
            total_shipping_cost = df___shipping["Total Shipping Cost"].sum()
            df___shipping["Percentage"] = (df___shipping["Total Shipping Cost"] / total_shipping_cost) * 100
            shipping_company_query = f"""
                SELECT 
                    o.reason AS Reason,
                    SUM(o.shipping_price) - SUM(o.customer_shipping_price) AS Total_Shipping_Cost
                FROM {returned_orders} o
                GROUP BY o.reason
                ORDER BY Total_Shipping_Cost DESC
            """
            cursor.execute(shipping_company_query)
            shipping_data = cursor.fetchall()

            df____shipping = pd.DataFrame(shipping_data, columns=["Reason", "Total Shipping Cost"])
            total_shipping_cost = df____shipping["Total Shipping Cost"].sum()
            df____shipping["Percentage"] = (df____shipping["Total Shipping Cost"] / total_shipping_cost) * 100
            query = f"""
                    WITH product_orders AS (
                        SELECT
                            o.order_number,
                            TRIM(SPLIT_PART(regexp_split_to_table(o.products, ','), ':', 1)) AS product_name
                        FROM {returned_orders} o
                    ),
                    distinct_orders AS (
                        SELECT COUNT(DISTINCT order_number) AS total_orders FROM {returned_orders}
                    )
                    SELECT 
                        product_name,
                        COUNT(DISTINCT order_number) AS order_count,
                        (COUNT(DISTINCT order_number) * 100.0) / (SELECT total_orders FROM distinct_orders) AS percentage
                    FROM product_orders
                    WHERE product_name IS NOT NULL
                    GROUP BY product_name
                    ORDER BY percentage DESC;

                    """
            df_products_percentage = pd.read_sql(query, conn)
            conn.close()
            percentage_returned = total_orders / (total_orders + total_cancelled + total_comp)
            percentage_returned_1 = total_orders / (total_orders + total_cancelled + total_comp+total_shipping)
            percentage__returned = total_orders / (total_orders + total_cancelled)
            avg_shipping_price=total_shipping_prices/total_orders
            avg_shipping_price_1=total_shipping_prices/total_products
            with col1:
                    metric_card_with_icon(
                        "Total Ordes", 
                        f"{total_orders:,}","", 
                        "The total number of orders."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                        "Total Products", 
                        f"{int(total_products):,}".replace(",", "."),"",
                        "The The total number of products returned."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                        "Percentage of Shipping Price (Go Only)", 
                        f"{(total_shipping_prices_go / total_shipping_prices):,.2f}","", 
                        """perctange of total shipping cost for orders which go only.  
                        النسبه اللي بتمثلها فلوس شحن الاوردرات اللي اتشحنت مره الفعليه بالنسبه للشحن الكلي الفعلي"""
                    )

            with col2:
                    metric_card_with_icon(
                        "Total Price", 
                        f"{int(total_prices):,}".replace(",", "."),"",
                        "The total revenue generated from all orders."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                        "Avg Shipping Price", 
                        f"{int(avg_shipping_price):,}".replace(",", "."),"",
                        "The average cost of shipping for all orders."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                        "Percentage of Shipping Price (Go And Back)", 
                        f"{(total_shipping_prices_back / total_shipping_prices):,.2f}","", 
                        """perctange of total shipping cost for orders which go and back.
                        النسبه اللي بتمثلها فلوس شحن الاوردرات اللي اتشحنت مرتين الفعليه بالنسبه للشحن الكلي الفعلي"""
                    )
            with col3:
                    metric_card_with_icon(
                        "Total Shipping Price(Actual)", 
                        f"{int(total_shipping_prices):,}".replace(",", "."),"", 
                        "The total shipping cost incurred for all orders."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                    "Percentage of Returned Orders", 
                    f"{percentage_returned * 100:.2f}%", "", 
                    "The percentage of returned orders out of total orders."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                        "Avg Shipping Price(Products)", 
                        f"{avg_shipping_price_1:.2f}","",
                        "The average cost of shipping for all products."
                    )
            with col4:
                    metric_card_with_icon(
                        "Total Profit", 
                        f"{int(total_profit):,}".replace(",", "."),"", 
                        """The total profit (total revenue minus total shipping cost).
                        االمبلغ الكلي مطروح منه الشحن الكلي مش الفعلي بس"""
                    )
                    st.markdown("")
                    metric_card_with_icon(
                    "Percentage of Returned Orders(Cancelled & Returned Only)", 
                    f"{percentage__returned * 100:.2f}%", "", 
                    "The percentage of returned orders out of cancelled and returned orders only."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                    "Percentage of Returned Orders(problems)", 
                    f"{percentage_returned_1 * 100:.2f}%", "", 
                    "The percentage of returned orders out of total orders with problems."
                    )

            fig = px.bar(
                df, 
                x="Region", 
                y="Total Orders", 
                title="Total Orders Distribution by Region",
                labels={"Region": "Region", "Total Orders": "Number of Orders"},
                text=df['Percentage'].apply(lambda x: f"{x:.2f}%"),
                color="Region",  
                height=600
            )

            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(
                xaxis_title="Region",
                yaxis_title="Total Orders",
                uniformtext_minsize=8,
                uniformtext_mode='hide'
            )
            st.markdown("")
            st.plotly_chart(fig, use_container_width=True)

            fig_shipping = px.bar(
            df_shipping, 
            x="Shipping Company", 
            y="Total Orders", 
            title="Total Orders Distribution by Shipping Company",
            labels={"Shipping Company": "Shipping Company", "Total Orders": "Number of Orders"},
            text=df_shipping['Percentage'].apply(lambda x: f"{x:.2f}%"), 
            color="Shipping Company",
            height=600
            )

            fig_shipping.update_traces(texttemplate='%{text}', textposition='outside')
            fig_shipping.update_layout(
            xaxis_title="Shipping Company",
            yaxis_title="Total Orders",
            uniformtext_minsize=8,
            uniformtext_mode='hide'
            )
            st.plotly_chart(fig_shipping, use_container_width=True)
            fig_reason = px.bar(
            df_reason, 
            x="Reason", 
            y="Total Orders", 
            title="Total Orders Distribution by Reason",
            labels={"Reason": "Reason", "Total Orders": "Number of Orders"},
            text=df_reason['Percentage'].apply(lambda x: f"{x:.2f}%"),
            color="Reason",
            height=600
            )

            fig_reason.update_traces(texttemplate='%{text}', textposition='outside')
            fig_reason.update_layout(
            xaxis_title="Reason",
            yaxis_title="Total Orders",
            uniformtext_minsize=8,
            uniformtext_mode='hide'
            )
            st.plotly_chart(fig_reason, use_container_width=True)
            fig_status = px.bar(
            df_status, 
            x="Status", 
            y="Total Orders", 
            title="Total Orders Distribution by Status",
            labels={"Status": "Status", "Total Orders": "Number of Orders"},
            text=df_status['Percentage'].apply(lambda x: f"{x:.2f}%"),
            color="Status",
            height=600
            )

            fig_status.update_traces(texttemplate='%{text}', textposition='outside')
            fig_status.update_layout(
            xaxis_title="Status",
            yaxis_title="Total Orders",
            uniformtext_minsize=8,
            uniformtext_mode='hide'
            )
            st.plotly_chart(fig_status, use_container_width=True)
            fig = px.line(
                df_date, 
                x="Date", 
                y="Total Orders", 
                title="Orders Over Time",
                labels={"Date": "Date", "Total Orders": "Number of Orders"}
            )
            st.plotly_chart(fig,use_container_width=True)
            fig = px.bar(
                df__shipping,
                x="Product Type",
                y="Total Shipping Price",
                title="Shipping Price Distribution by Product Type",
                labels={"Total Shipping Price": "Shipping Price (Currency)"},
                template="plotly_white",
                 text=df__shipping['Percentage'].apply(lambda x: f"{x:.2f}%"),
                color="Product Type"
            )
            fig.update_traces(texttemplate="%{text}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
                        
            fig = px.bar(
                df___shipping,
                x="Status",
                y="Total Shipping Cost",
                title="Shipping Price Distribution by Status",
                labels={"Total Shipping Cost": "Shipping Cost (Currency)"},
                template="plotly_white",
                text=df___shipping['Percentage'].apply(lambda x: f"{x:.2f}%"),
                color="Status"
            )
            fig.update_traces(texttemplate="%{text}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
            fig = px.bar(
                df____shipping,
                x="Reason",
                y="Total Shipping Cost",
                title="Shipping Price Distribution by Reason",
                labels={"Total Shipping Cost": "Shipping Cost (Currency)"},
                template="plotly_white",
                text=df____shipping['Percentage'].apply(lambda x: f"{x:.2f}%"),
                color="Reason"
            )
            fig.update_traces(texttemplate="%{text}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
            fig = px.bar(df_products_percentage, x="product_name", y="percentage", 
             text="percentage", labels={"product_name": "Product Type", "percentage": "Percentage (%)"},
             title="Product Order Percentage", color="percentage",
             color_continuous_scale="blues")
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(yaxis_title="Percentage (%)", xaxis_title="Product Type")
            st.plotly_chart(fig,use_container_width=True)
    elif page == "Problems":
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: -60px; '>🚨Problems</h1>", unsafe_allow_html=True)
        if st.session_state.username=="walid" or st.session_state.username=="ahmed":
            selected = option_menu(
                menu_title=None,
                options=["Add Order", "Search Orders", "View All Orders", 'Modify Orders','Delete Orders','Analysis'],
                icons=['cart', 'search', "list-task", 'gear','trash','graph-up'],
                menu_icon="cast",
                default_index=0,
                orientation="horizontal",
                styles={
                    'container': {
                        'width': '100%',
                        'margin': '30',
                        'padding': '0',
                    }
                }
            )
        else:
            selected = option_menu(
                menu_title=None,
                options=["Add Order", "Search Orders", "View All Orders", 'Modify Orders','Delete Orders'],
                icons=['cart', 'search', "list-task", 'gear','trash'],
                menu_icon="cast",
                default_index=0,
                orientation="horizontal",
                styles={
                    'container': {
                        'width': '100%',
                        'margin': '30',
                        'padding': '0',
                    }
                }
            )

        st.markdown("")
        st.markdown("")
        if selected== 'Add Order':
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
            def reset_sh_order_session_states():
                    st.session_state.sh_order_products = []
                    st.session_state.sh_product_count = 1
            # customer_name = st.text_input("Customer Name")
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

            # customer_phone_2 = st.text_input("Customer Phone 2 (Optional)", value="")
            # corrected_phone_2, is_valid_2, is_valid_22 = correct_phone_number(customer_phone_2)
            # if customer_phone_2:
            #     if not is_valid_22:
            #         st.markdown(
            #             f"<div style='color: red;'>(Invalid Length): {corrected_phone_2}</div>",
            #             unsafe_allow_html=True,
            #         )
            #     elif not is_valid_2:
            #         st.markdown(
            #             f"<div style='color: orange;'>Corrected Phone 2 (Invalid Format): {corrected_phone_2}</div>",
            #             unsafe_allow_html=True,
            #         )

            # email = st.text_input("Email (Optional)", value="")
            # corrected_email, is_valid_email = correct_email(email)
            # if email:
            #     if not is_valid_email:
            #         st.markdown(
            #             f"<div style='color: orange;'>Corrected email (Invalid Format): {corrected_email}</div>",
            #             unsafe_allow_html=True,
            #         )

            ship_company = st.selectbox("Shipping Company",company)
            region = st.selectbox("Region", egypt_governorates)
            order_number = st.text_input("Order Code")
            status = st.selectbox("Status", ["Exchanged", "Delivery Man", "Team","Customer"])

            if status == "Delivery Man":
                reason = "Delivery Man"
            elif status == "Team":
                reason="Team"
            elif status=="Customer":
                reason="Customer"
            elif status =="Exchanged":
                reason=st.selectbox("Reason",["Size","Quality"])

            if "sh_order_products" not in st.session_state:
                    st.session_state.sh_order_products = []
            if "sh_product_count" not in st.session_state:
                    st.session_state.sh_product_count = 1 
            col1, col2 = st.columns([1, 1])
            col_1, col_2,col_3= st.columns([1,1,25])
            with col_1:
                if st.button("➕"):
                    st.session_state.sh_product_count += 1
            with col_2:
                if st.button("➖"):
                    st.session_state.sh_product_count -= 1
                    st.session_state.sh_order_products.pop()
            for i in range(st.session_state.sh_product_count):
                with col1:
                    type_of_product = st.selectbox(f"Type {i+1}", products, key=f"type_{i}")
                with col2:
                    count_of_product = custom_number_input(
                        f"Count {i+1}", min_value=0, step=1, key=f"count_{i}"
                    )

                if len(st.session_state.sh_order_products) <= i:
                    st.session_state.sh_order_products.append(
                        {"Type": type_of_product, "Count": count_of_product}
                    )
                else:
                    st.session_state.sh_order_products[i] = {"Type": type_of_product, "Count": count_of_product}     
            customer_shipping_price = custom_number_input("Shipping price paid By customer", min_value=0, step=1)     
            shipping_price = custom_number_input("Shipping Price Paid To Company", min_value=0, step=1)
            if st.button("Add Order"):
                # if not customer_name.strip():
                #     st.error("Customer Name is required.")
                # elif contains_arabic(customer_name):
                #     st.error("Customer Name cannot contain Arabic characters.")
                if not customer_phone_1.strip():
                    st.error("Customer Phone 1 is required.")
                elif not is_valid_1:
                    st.error("Customer Phone 1 is invalid. Please correct the number.")
                # elif customer_phone_2 and not is_valid_2:
                #     st.error("Customer Phone 2 is invalid. Please correct the number.")
                # elif email and not is_valid_email:
                #     st.error("Email is invalid. Please correct the email.")
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
                elif shipping_price is None or shipping_price < 0:
                    st.error("Order Price is required.")
                elif customer_shipping_price is None or customer_shipping_price < 0:
                    st.error("Shipping price paid by customer is required.")
                else:
                    conn = create_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute(
                            f"SELECT customer_id FROM {customers} WHERE customer_phone_1 = %s",
                            (corrected_phone_1,)
                        )
                    customer = cursor.fetchone()
                    customer_id = customer[0]
                    # if customer:                
                    # else:
                    #         cursor.execute(
                    #             f"INSERT INTO {customers} (customer_name, customer_phone_1, customer_phone_2, email) VALUES (%s, %s, %s, %s) RETURNING customer_id",
                    #             (customer_name, corrected_phone_1, corrected_phone_2, corrected_email)
                    #         )
                    #         customer_id = cursor.fetchone()[0]
                    total_count = sum(item["Count"] for item in st.session_state.sh_order_products)
                    products_string = ", ".join([f"{item['Type']}:{item['Count']}" for item in st.session_state.sh_order_products])
                    cursor.execute(
                            f"INSERT INTO {shipping} (customer_id, ship_company, region, order_number, status, shipping_price, hoodies,products,reason,customer_shipping_price) VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s,%s)",
                            (customer_id, ship_company, region, order_number, status, shipping_price, total_count,products_string,reason,customer_shipping_price)
                        )

                    conn.commit()
                    st.success("Order added successfully!")
                    log_action(st.session_state.username, "Add Shipping Problem", f"Order ID: {order_number}, Customer: {customer_name}")
                    reset_sh_order_session_states()
                    conn.close()
        elif selected=="Search Orders":
            st.markdown("")
            st.markdown("")
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
                        c.email, o.ship_company, o.region,o.status,o.shipping_price,o.hoodies,o.reason,o.products,o.customer_shipping_price
                    FROM {shipping} o
                    INNER JOIN {customers} c ON o.customer_id = c.customer_id
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
        elif selected=="View All Orders":
            st.markdown("")
            st.markdown("")
            sort_by = st.selectbox("Sort by", ["Order Code"])
            sort_order = st.radio("Sort orders", ["Ascending", "Descending"])
            
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT DISTINCT ship_company FROM {shipping}")
            ship_companies = [row[0] for row in cursor.fetchall()]
            selected_ship_company = st.selectbox("Filter by Shipping Company", ["All"] + ship_companies)
            sort_column = "CAST(o.order_number AS INTEGER)"
            sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
            
            query = f"""
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                c.email, o.ship_company, o.region, o.status,o.shipping_price,o.hoodies,o.reason,o.products,o.customer_shipping_price
            FROM {shipping} o
            INNER JOIN {customers} c ON o.customer_id = c.customer_id
            """
            if selected_ship_company != "All":
                query += f" WHERE o.ship_company = '{selected_ship_company}'"
            
            query += f" ORDER BY {sort_column} {sort_direction}"
                
            cursor.execute(query)
            all_orders = cursor.fetchall()
            total_query = f"""
            SELECT COUNT(o.order_number), COALESCE(SUM(o.hoodies),0),COALESCE(SUM(o.shipping_price), 0)
            FROM {shipping} o
            """
            if selected_ship_company != "All":
                total_query += f" WHERE ship_company = '{selected_ship_company}'"
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
                        "Shipping Price Paid To Company":order[8],
                        "Actual Shipping Cost": (order[8] or 0) - (order[12] or 0),
                        "Type of Products":order[11],
                        "Number of Products":order[9]
                    })
                df = pd.DataFrame(data)
                st.write("All Orders:")
                st.dataframe(df)
                st.write(f"**Total Orders:** {total_orders}")
                st.write(f"**Total Shipping Price:** {int(total_price):,}".replace(",", "."))
                st.write(f"**Total Actual Shipping Cost:** {int(df['Actual Shipping Cost'].sum()):,}".replace(',', '.'))
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

        elif selected=="Modify Orders":
            st.markdown("")
            st.markdown("")
            st.subheader("Select an Order")
            search_order_number = st.text_input("Enter Order Code")

            if search_order_number:
                conn = create_connection()
                cursor = conn.cursor()
                
                cursor.execute(
                    f"""
                    SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2,
                        c.email, o.ship_company, o.region,o.status,o.shipping_price,o.hoodies,o.reason,o.products,o.customer_shipping_price
                    FROM {shipping} o
                    INNER JOIN {customers} c ON o.customer_id = c.customer_id
                    WHERE o.order_number = %s
                    """,
                    (search_order_number,)
                )
                order_details = cursor.fetchone()

                if order_details:
                    st.write("Order Details:")
                    st.table([order_details])
                    products_list = [
                            {"Type": p.split(":")[0], "Count": int(p.split(":")[1])}
                            for p in order_details[11].split(", ")]
                    st.subheader("Update Order")
                    new_name=st.text_input("Customer Name",value=order_details[1])
                    new_phone1=st.text_input("Customer Phone 1",value=order_details[2])
                    new_phone2=st.text_input("Customer Phone 2",value=order_details[3])
                    new_email=st.text_input("Email",value=order_details[4])
                    new_ship_company = st.selectbox("Shipping Company",company,index=company.index(order_details[5]))
                    new_region = st.selectbox("Region",egypt_governorates,index=egypt_governorates.index(order_details[6]))
                    new_status = st.selectbox("Status",["Delivery Man","Exchanged","Team","Customer"])
                    if new_status == "Delivery Man":
                        new_problem_reason = "Delivery Man"
                    elif new_status == "Team":
                        new_problem_reason="Team"
                    elif new_status == "Customer":
                        new_problem_reason="Customer"
                    elif new_status =="Exchanged":
                        new_problem_reason=st.selectbox("Reason",["Size","Quality"])
                    new_customer_shipping_price=custom_number_input("Shipping price paid By customer",value=order_details[12])
                    new_price=custom_number_input("Shipping Price Paid To Company",value=order_details[8])
                    if "sh_modified_products" not in st.session_state:
                            st.session_state.sh_modified_products = products_list
                    for i, product in enumerate(st.session_state.sh_modified_products):
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                st.session_state.sh_modified_products[i]["Type"] = st.selectbox(
                                    f"Type {i+1}", products, key=f"product_type_{i}", index=products.index(product["Type"])
                                )
                            with col2:
                                st.session_state.sh_modified_products[i]["Count"] = custom_number_input(
                                    f"Count {i+1}", min_value=0, step=1, key=f"product_count_{i}", value=product["Count"]
                                )
                            with col3:
                                if st.button(f"Remove Product {i+1}", key=f"remove_product_{i}"):
                                    st.session_state.sh_modified_products.pop(i)
                                    st.rerun()
                    if "sh_new_products" not in st.session_state:
                        st.session_state.sh_new_products = []

                    if st.button("Add More Products"):
                        st.session_state.sh_new_products.append({"Type": "", "Count": 1})

                    for i, product in enumerate(st.session_state.sh_new_products):
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col1:
                            st.session_state.sh_new_products[i]["Type"] = st.selectbox(
                                f"New Type {i+1}", products, key=f"new_product_type_{i}"
                            )
                        with col2:
                            st.session_state.sh_new_products[i]["Count"] = custom_number_input(
                                f"New Count {i+1}", min_value=0, step=1, key=f"new_product_count_{i}", value=product["Count"]
                            )
                        with col3:
                            if st.button(f"Remove New Product {i+1}", key=f"remove_new_product_{i}"):
                                st.session_state.sh_new_products.pop(i)
                                st.rerun()

                    if st.button("Update Order"):
                                updated_products = ", ".join(
                                    [f"{item['Type']}:{item['Count']}" for item in (st.session_state.sh_modified_products + st.session_state.sh_new_products)]
                                )
                                cursor.execute(
                                    f"""
                                    UPDATE {customers}
                                    SET customer_name = %s, customer_phone_1 = %s, customer_phone_2 = %s, email = %s
                                    WHERE customer_id = (
                                        SELECT customer_id 
                                        FROM {shipping}
                                        WHERE order_number = %s
                                    )
                                    """,
                                    (new_name, new_phone1, new_phone2, new_email, search_order_number)
                                )
                                
                                cursor.execute(
                                    f"""
                                    UPDATE {shipping}
                                    SET ship_company = %s, region = %s,status=%s,shipping_price=%s,hoodies=%s,reason=%s,products=%s,customer_shipping_price=%s
                                    WHERE order_number = %s
                                    """,
                                    (new_ship_company, new_region, new_status,new_price,sum(item["Count"] for item in (st.session_state.sh_modified_products + st.session_state.sh_new_products)), new_problem_reason,updated_products, new_customer_shipping_price, search_order_number)
                                )


                                conn.commit()
                                del st.session_state.sh_modified_products
                                del st.session_state.sh_new_products
                                st.success("Order updated successfully!")
                                log_action(st.session_state.username, "Update Shipping Problem", f"Order ID: {search_order_number}, Customer: {new_name}")

                    st.subheader("Remove Order")
                    with st.form("delete_order_form"):
                        delete_password = st.text_input("Enter Password to Confirm Deletion", type="password")
                        delete_submit = st.form_submit_button("Delete Order")

                        if delete_submit:
                            if delete_password == "admin":
                                cursor.execute(
                                    f"DELETE FROM {shipping} WHERE order_number = %s", (search_order_number,)
                                )
                                conn.commit()
                                st.success("Order deleted successfully!")
                                log_action(st.session_state.username, "Delete Shipping Problem", f"Order ID: {search_order_number}, Customer: {new_name}")
                            else:
                                st.error("Incorrect password. Order deletion canceled.")
                else:
                    st.write("No order found with the given Order Number.")
                
                conn.close()
        elif selected=='Delete Orders':
            query = f"""
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                c.email, o.ship_company, o.region, o.status,o.shipping_price,o.hoodies,o.reason,o.customer_shipping_price,o.order_id
            FROM {shipping} o
            INNER JOIN {customers} c ON o.customer_id = c.customer_id
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
                        "Order Id":order[12],
                        "Order Number": order[0],
                        "Customer Name": order[1],
                        "Phone 1": order[2],
                        "Phone 2": order[3],
                        "Email": order[4],
                        "Shipping Company": order[5],
                        "Region": order[6],
                        "Status": order[7],
                        "Reason":order[10],
                        "Shipping Price In Shipping Company":order[8],
                        "Actual Shipping Cost": (order[8] or 0) -(order[11] or 0),
                        "Number of Products":order[9]
                    }
                    for order in all_orders
                ]
                df = pd.DataFrame(orders_data)
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_selection("multiple", use_checkbox=True, header_checkbox=True)
                gb.configure_column("Order Number", sort="asc")  
                grid_options = gb.build()
                grid_response = AgGrid(
                        df,
                        gridOptions=grid_options,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        height=400,
                        theme="streamlit",
                        fit_columns_on_grid_load=True,
                        key="grid",
                )
                selected_rows = grid_response["selected_rows"]

                if selected_rows is None or selected_rows.empty:
                    st.warning("No orders selected.")
                else:
                    st.write("Selected Rows:", selected_rows)  
                    if "Order Number" in selected_rows.columns:
                        selected_order_numbers = selected_rows["Order Id"].astype(str).tolist()
                        selected_customers = selected_rows["Customer Name"].astype(str).tolist()
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

                            delete_query = f"DELETE FROM {shipping} WHERE order_id IN %s"
                            try:
                                with create_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute(delete_query, (orders_tuple,))
                                    conn.commit()
                                    st.success(f"Successfully deleted {len(selected_order_numbers)} orders.")
                                    log_action(st.session_state.username, "Delete Completed Order", f"Order ID: {selected_order_numbers}, Customers: {selected_customers}")
                            except Exception as e:
                                st.error(f"Error deleting orders: {e}")
        elif selected=="Analysis":
            col1, col2, col3,col4= st.columns([1, 1, 1,1])
            def metric_card_with_icon(title, content, description,info):
                st.markdown(
                    f"""
                    <div style="background-color: #fff; border: 1px solid #ddd; border-radius: 15px; padding: 15px; 
                                text-align: left; box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.1); position: relative; color: #000; 
                                width: 100%; max-width: 300px;">
                        <div style="position: absolute; top: 8px; right: 8px;" title="{info}">
                            <div style="width: 20px; height: 20px; border: 2px solid #000; border-radius: 50%; display: flex; 
                                        align-items: center; justify-content: center; font-size: 12px; font-weight: bold; color: #000; 
                                        cursor: pointer;">
                                i
                            </div>
                        </div>
                        <h4 style="margin: 5px 10px 0 10px; font-size: 14px; color: #000; padding-left: 10px;">{title}</h4>
                        <p style="margin: -10px 10px 0 10px; font-size: 28px; font-weight: bold; color: #000; padding-left: 10px;">{content}</p>
                        <p style="margin: -7px 10px 5px 10px; font-size: 12px; color: #777; padding-left: 10px;">{description}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            conn = create_connection()
            cursor = conn.cursor()

            total_query = f"""
                SELECT 
                    COUNT(o.order_number) AS total_orders, 
                    COALESCE(SUM(o.hoodies), 0) AS total_products,
                    COALESCE(SUM(o.shipping_price), 0)-COALESCE(SUM(o.customer_shipping_price), 0) AS total_shipping_prices
                FROM {shipping} o
                """
            cursor.execute(total_query)
            total_orders, total_products, total_shipping_prices = cursor.fetchone()
            query = f"""
                SELECT 
                    o.region, 
                    COUNT(o.order_number) AS total_orders 
                FROM {shipping} o
                GROUP BY o.region
                ORDER BY total_orders DESC
                """
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=["Region", "Total Orders"])
            total_orders_region = df['Total Orders'].sum()
            df['Percentage'] = (df['Total Orders'] / total_orders_region) * 100
            shipping_company_query = f"""
                SELECT 
                    o.ship_company AS Shipping_Company,
                    COUNT(o.order_number) AS Total_Orders
                FROM {shipping} o
                GROUP BY o.ship_company
                ORDER BY Total_Orders DESC
                """
            cursor.execute(shipping_company_query)
            shipping_data = cursor.fetchall()
            df_shipping = pd.DataFrame(shipping_data, columns=["Shipping Company", "Total Orders"])
            total_orders_shipping = df_shipping['Total Orders'].sum()
            df_shipping['Percentage'] = (df_shipping['Total Orders'] / total_orders_shipping) * 100
            reason_query = f"""
                SELECT 
                    o.reason AS reason,
                    COUNT(o.order_number) AS Total_Orders
                FROM {shipping} o
                GROUP BY o.reason
                ORDER BY Total_Orders DESC
                """
            cursor.execute(reason_query)
            reason_data = cursor.fetchall()
            df_reason = pd.DataFrame(reason_data, columns=["Reason", "Total Orders"])
            total_orders_all = df_reason['Total Orders'].sum()
            df_reason['Percentage'] = (df_reason['Total Orders'] / total_orders_all) * 100
            status_query = f"""
                SELECT 
                    o.status AS status,
                    COUNT(o.order_number) AS Total_Orders
                FROM {shipping} o
                GROUP BY o.status
                ORDER BY Total_Orders DESC
                """
            cursor.execute(status_query)
            status_data = cursor.fetchall()
            df_status = pd.DataFrame(status_data, columns=["Status", "Total Orders"])
            total_orders_all = df_reason['Total Orders'].sum()
            df_status['Percentage'] = (df_status['Total Orders'] / total_orders_all) * 100
            def parse_products(products_str):
                product_items = re.findall(r'([a-zA-Z\s]+):(\d+)', products_str)
                products_dict = {item[0].strip(): int(item[1]) for item in product_items}
                return products_dict

            query = f"""
            SELECT 
                o.order_number,
                o.products,
                o.shipping_price-o.customer_shipping_price
            FROM {shipping} o
            """
            cursor.execute(query)
            data = cursor.fetchall()

            product_shipping = {}

            for order in data:
                order_number, products_str, total_shipping_price = order
                if not products_str:
                    continue
                products_dict = parse_products(products_str) 
                total_quantity = sum(products_dict.values()) 
                if total_quantity==0:
                    continue
                for product_type, quantity in products_dict.items():
                    shipping_price_for_product = (quantity / total_quantity)

                    if product_type in product_shipping:
                        product_shipping[product_type] += shipping_price_for_product
                    else:
                        product_shipping[product_type] = shipping_price_for_product

            df__shipping = pd.DataFrame(product_shipping.items(), columns=["Product Type", "Total Shipping Price"])
            df__shipping = df__shipping.sort_values(by="Total Shipping Price", ascending=False)
            total_shipping_cost = df__shipping["Total Shipping Price"].sum()
            df__shipping["Percentage"] = (df__shipping["Total Shipping Price"] / total_shipping_cost) * 100
            shipping_company_query = f"""
                SELECT 
                    o.status AS Status,
                    SUM(o.shipping_price - o.customer_shipping_price) AS Total_Shipping_Cost
                FROM {shipping} o
                GROUP BY o.status
                ORDER BY Total_Shipping_Cost DESC
            """
            cursor.execute(shipping_company_query)
            shipping_data = cursor.fetchall()

            df_shipping_status = pd.DataFrame(shipping_data, columns=["Status", "Total Shipping Cost"])
            total_shipping_cost = df_shipping_status["Total Shipping Cost"].sum()
            df_shipping_status["Percentage"] = (df_shipping_status["Total Shipping Cost"] / total_shipping_cost) * 100
            shipping_company_query = f"""
                SELECT 
                    o.reason AS Reason,
                    SUM(o.shipping_price - o.customer_shipping_price) AS Total_Shipping_Cost
                FROM {shipping} o
                GROUP BY o.reason
                ORDER BY Total_Shipping_Cost DESC
            """
            cursor.execute(shipping_company_query)
            shipping_data = cursor.fetchall()

            df_shipping_reason = pd.DataFrame(shipping_data, columns=["Reason", "Total Shipping Cost"])
            total_shipping_cost = df_shipping_reason["Total Shipping Cost"].sum()
            df_shipping_reason["Percentage"] = (df_shipping_reason["Total Shipping Cost"] / total_shipping_cost) * 100
            query = f"""
                    WITH product_orders AS (
                        SELECT
                            o.order_number,
                            TRIM(SPLIT_PART(regexp_split_to_table(o.products, ','), ':', 1)) AS product_name
                        FROM {shipping} o
                    ),
                    distinct_orders AS (
                        SELECT COUNT(DISTINCT order_number) AS total_orders FROM {shipping}
                    )
                    SELECT 
                        product_name,
                        COUNT(DISTINCT order_number) AS order_count,
                        (COUNT(DISTINCT order_number) * 100.0) / (SELECT total_orders FROM distinct_orders) AS percentage
                    FROM product_orders
                    WHERE product_name IS NOT NULL
                    GROUP BY product_name
                    ORDER BY percentage DESC;

                    """
            df_products_percentage = pd.read_sql(query, conn)
            total_completed_query=f"""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM {orders} o
            """
            cursor.execute(total_completed_query)
            total_completed=cursor.fetchone()[0]
            total_returned_query=f"""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM {returned_orders} o
            """
            cursor.execute(total_returned_query)
            total_returned=cursor.fetchone()[0]
            total_cancelled_query=f"""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM {shipping} o
            """
            cursor.execute(total_cancelled_query)
            total_cancelled=cursor.fetchone()[0]
            conn.close()
            avg_shipping_price= total_shipping_prices/total_orders
            avg_shipping_price_1=total_shipping_prices/total_products
            problems_pre=total_orders/(total_orders+total_cancelled+total_returned+total_completed)
            with col1:
                    metric_card_with_icon(
                        "Total Ordes", 
                        f"{total_orders:,}","", 
                        "The total number of orders."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                        "Avg Shipping Price(Products)", 
                        f"{avg_shipping_price_1:.2f}","",
                        "The average cost of shipping for all products."
                    )

            with col2:
                    metric_card_with_icon(
                        "Avg Shipping Price", 
                        f"{int(avg_shipping_price):,}".replace(",", "."),"",
                        "The average cost of shipping for all orders."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                    "Percentage of problems", 
                    f"{problems_pre * 100:.2f}%", "", 
                    "The percentage of  problems out of total orders."
                    )
            with col3:
                    metric_card_with_icon(
                        "Total Shipping Prices", 
                        f"{int(total_shipping_prices):,}".replace(",", "."),"", 
                         "The total shipping cost incurred for all orders."
                    )
            with col4:
                    metric_card_with_icon(
                        "Total Products", 
                        f"{int(total_products):,}".replace(",", "."),"",
                        "The The total number of products returned."
                    )

            fig = px.bar(
                df, 
                x="Region", 
                y="Total Orders", 
                title="Total Orders by Region",
                labels={"Region": "Region", "Total Orders": "Number of Orders"},
                text=df['Percentage'].apply(lambda x: f"{x:.2f}%"),
                color="Region",  
                height=600
            )

            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(
                xaxis_title="Region",
                yaxis_title="Total Orders",
                uniformtext_minsize=8,
                uniformtext_mode='hide'
            )
            st.markdown("")
            st.plotly_chart(fig, use_container_width=True)

            fig_shipping = px.bar(
            df_shipping, 
            x="Shipping Company", 
            y="Total Orders", 
            title="Total Orders by Shipping Company",
            labels={"Shipping Company": "Shipping Company", "Total Orders": "Number of Orders"},
            text=df_shipping['Percentage'].apply(lambda x: f"{x:.2f}%"), 
            color="Shipping Company",
            height=600
            )

            fig_shipping.update_traces(texttemplate='%{text}', textposition='outside')
            fig_shipping.update_layout(
            xaxis_title="Shipping Company",
            yaxis_title="Total Orders",
            uniformtext_minsize=8,
            uniformtext_mode='hide'
            )
            st.plotly_chart(fig_shipping, use_container_width=True)
            fig_reason = px.bar(
            df_reason, 
            x="Reason", 
            y="Total Orders", 
            title="Total Orders by Reason",
            labels={"Reason": "Reason", "Total Orders": "Number of Orders"},
            text=df_reason['Percentage'].apply(lambda x: f"{x:.2f}%"),
            color="Reason",
            height=600
            )

            fig_reason.update_traces(texttemplate='%{text}', textposition='outside')
            fig_reason.update_layout(
            xaxis_title="Reason",
            yaxis_title="Total Orders",
            uniformtext_minsize=8,
            uniformtext_mode='hide'
            )
            st.plotly_chart(fig_reason, use_container_width=True)
            fig_status = px.bar(
            df_status, 
            x="Status", 
            y="Total Orders", 
            title="Total Orders by Status",
            labels={"Status": "Status", "Total Orders": "Number of Orders"},
            text=df_status['Percentage'].apply(lambda x: f"{x:.2f}%"),
            color="Status",
            height=600
            )

            fig_status.update_traces(texttemplate='%{text}', textposition='outside')
            fig_status.update_layout(
            xaxis_title="Status",
            yaxis_title="Total Orders",
            uniformtext_minsize=8,
            uniformtext_mode='hide'
            )
            st.plotly_chart(fig_status, use_container_width=True)
            fig = px.bar(
                df__shipping,
                x="Product Type",
                y="Total Shipping Price",
                title="Shipping Price Distribution by Product Type",
                labels={"Total Shipping Price": "Shipping Price (Currency)"},
                template="plotly_white",
                text=df__shipping['Percentage'].apply(lambda x: f"{x:.2f}%"),
                color="Product Type"
            )
            fig.update_traces(texttemplate="%{text}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
            fig = px.bar(
                df_shipping_status,
                x="Status",
                y="Total Shipping Cost",
                title="Shipping Price Distribution by Status",
                labels={"Total Shipping Cost": "Shipping Cost (Currency)"},
                template="plotly_white",
                 text=df_shipping_status['Percentage'].apply(lambda x: f"{x:.2f}%"),
                color="Status"
            )
            fig.update_traces(texttemplate="%{text}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
            fig = px.bar(
                df_shipping_reason,
                x="Reason",
                y="Total Shipping Cost",
                title="Shipping Price Distribution by Reason",
                labels={"Total Shipping Cost": "Shipping Cost (Currency)"},
                template="plotly_white",
                 text=df_shipping_reason['Percentage'].apply(lambda x: f"{x:.2f}%"),
                color="Reason"
            )
            fig.update_traces(texttemplate="%{text}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
            fig = px.bar(df_products_percentage, x="product_name", y="percentage", 
             text="percentage", labels={"product_name": "Product Type", "percentage": "Percentage (%)"},
             title="Product Order Percentage", color="percentage",
             color_continuous_scale="blues")
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(yaxis_title="Percentage (%)", xaxis_title="Product Type")
            st.plotly_chart(fig,use_container_width=True)
    elif page == "Information":
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: -60px; '>📝Information</h1>", unsafe_allow_html=True)
        order_statuses = {
            "Cancelled": {
                "en": "The order was not shipped.",
                "ar": "لم يتم شحن الاوردر"
            },
            "Cancelled (Out of Stock)": {
                "en": "The order was cancelled due to product unavailability.",
                "ar": "الاوردر تم الغاءه بسبب عدم توفر المنتج"
            },
            "Cancelled (Team)": {
                "en": "The order was not confirmed due to the team (order was forgotten).",
                "ar": "لم يتم تأكيد الاوردر بسبب التيم ( الاوردر اتنسى)"
            },
            "Cancelled (Customer)": {
                "en": "The customer cancelled the order.",
                "ar": "العميل قام بإلغاء الأوردر"
            },
            "Cancelled (Not Confirmed)": {
                "en": "The customer did not confirm the order.",
                "ar": "العميل لم يقم بتأكيد الاوردر"
            },
            "Returned (Go Only)": {
                "en": "The order was shipped but returned in the same order, and the customer refused to receive it.",
                "ar": "الاوردر تم شحنه ورجع في نفس الاوردر و العميل رفض استلامه(مرتجع)"
            },
            "Returned (Go and Back)": {
                "en": "The order was shipped, and another order was created for its return.",
                "ar": "الاوردر تم شحنه و تم عمل اوردر اخر لاسترجاعه"
            },
            "Returned (Customer)": {
                "en": "The customer returned the order, and it was not shipped again.",
                "ar": "العميل رجع الاوردر ولم يتم شحنه مره اخرى"
            },
            "Returned (Quality)": {
                "en": "The customer returned the order due to quality issues, and it was not shipped again.",
                "ar": "العميل رجع الاوردر بسبب الخامه ولم يتم شحنه مره اخرى"
            },
            "Returned (Size)": {
                "en": "The customer returned the order due to size issues, and it was not shipped again.",
                "ar": "العميل رجع الاوردر بسبب المقاس و لم يتم شحنه مره اخرى"
            },
            "Returned (Team)": {
                "en": "The customer received the order with an issue caused by the team and refused to reorder.",
                "ar": "العميل وصله الاوردر فيه حاجه غلط بسبب خطأ من التييم ورفض يطلب تاني."
            },
            "Returned (Delivery Man)": {
                "en": "The order was returned due to the delivery man.",
                "ar": "الاوردر رجع بسبب مندوب الشحن"
            },
            "Problems (Exchanged)": {
                "en": "The order was exchanged.",
                "ar": "الاوردر تم استبداله"
            },
            "Problems (Exchanged - Size)": {
                "en": "The order was exchanged due to size issues.",
                "ar": "الاوردر تم استبداله بسبب المقاس"
            },
            "Problems (Exchanged - Quality)": {
                "en": "The order was exchanged due to quality issues.",
                "ar": "الاوردر تم استبداله بسبب الخامه"
            },
            "Problems (Team)": {
                "en": "There was an issue with the order due to the team.",
                "ar": "الاوردر فيه مشكله بسبب التييم"
            },
            "Problems (Delivery Man)": {
                "en": "There was an issue with the order due to the delivery man.",
                "ar": "الاوردر فيه مشكله بسبب مندوب الشحن"
            },
            "Problems (Customer)": {
                "en": "The order is complete, but there is a problem that happened because of the customer.",
                "ar": "الاوردر اكتمل بس فيه مشكله حصلت بسبب العميل"
            }
        }
        
        for status, descriptions in order_statuses.items():
            with st.expander(status):
                st.write(f"{descriptions['en']}")
                st.write(f"{descriptions['ar']}")
SEASON_PARAMS = {
    "Winter": ("orders", "returned_orders", "cancelled_orders", "shipping", "on_hole", "customers"),
    "Summer": ("summer_completed", "summer_returned", "summer_cancelled", "summer_shipping", "summer_on_hold", "summer_customers"),
    # Add more seasons as needed
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    if "selected_season" not in st.session_state or st.session_state.selected_season is None:
        # Show the appropriate season selection page
        if st.session_state.username in ["walid", "ahmed"]:
            season_selection_page()
        else:
            season_selection_page_1()
    else:
        # Get the parameters for the selected season and call the orders page
        season = st.session_state.selected_season
        params = SEASON_PARAMS.get(season)
        if params:
            orders_management_page(*params)
        else:
            st.error(f"No parameters defined for season: {season}")
else:
    login_page()
