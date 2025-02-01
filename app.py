import streamlit as st
import psycopg2
import re
import pandas as pd
import io
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from streamlit_option_menu import option_menu
import streamlit_shadcn_ui as ui
import plotly.express as px
import plotly.graph_objects as go
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
    "metoo": "14151617",
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

    with col2:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: 50px; '>☀️ Summer Season</h1>", unsafe_allow_html=True)
        st.markdown("")
        if st.button("Select Summer", key="summer", use_container_width=True):
            st.session_state.selected_season = "Summer"
            st.rerun()

def orders_management_page():
    if st.session_state.selected_season is None:
        season_selection_page()
        return
    if st.session_state.selected_season == "Summer":
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: 200px;'>Coming Soon...</h1>", unsafe_allow_html=True)
        st.markdown("")
        st.markdown("")
        st.markdown("")
        col1,col2,col3=st.columns([1.75,1,1])
        with col2:
            if st.button("Back"):
                st.session_state.selected_season = None 
                season_selection_page()
                st.rerun()
            return 
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
        
    if st.session_state.username=="walid" and  st.session_state.selected_season== "Winter":
        with st.sidebar:
            page=option_menu("Orders Management", ["Completed Orders", 'Cancelled Orders','Returned Orders','Problems','Customers','Analysis','Activity Logs'],icons=['check-circle', 'ban','arrow-left','exclamation-circle','people','graph-up','clock'], menu_icon="list", default_index=0)
            if st.button("Logout"):
                st.session_state.logged_in = False
                log_action(st.session_state.username, "Logout", "Successful logout")
                st.rerun()
    elif st.session_state.selected_season== "Winter":
        with st.sidebar:
            page=option_menu("Orders Management", ["Completed Orders", 'Cancelled Orders','Returned Orders','Problems','Customers','Analysis'],icons=['check-circle', 'ban','arrow-left','exclamation-circle','people','graph-up'], menu_icon="list", default_index=0)
            if st.button("Logout"):
                st.session_state.logged_in = False
                log_action(st.session_state.username, "Logout", "Successful logout")
                st.rerun()
 
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
    products=['Hoodie','Quarter Zipper','Acid Washed Hoodie']
    Options= ["No", "Yes"]
    if page=='Analysis':
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
        total_query = """
                SELECT 
                    COALESCE(SUM(o.order_price), 0) AS total_prices
                FROM orders o
                """
        cursor.execute(total_query)
        total_prices = cursor.fetchone()[0]

        total_cancelled_query = """
                SELECT 
                    COALESCE(SUM(o.order_price), 0) AS total_prices
                FROM cancelled_orders o
                """
        cursor.execute(total_cancelled_query)
        total_cancelled=cursor.fetchone()[0]


        total_returned_query = """
                SELECT 
                    COALESCE(SUM(o.order_price), 0) AS total_prices
                FROM returned_orders o
                """
        cursor.execute(total_returned_query)
        total_returned=cursor.fetchone()[0]
        total_shipping_returned_query = """
            SELECT 
                COUNT(o.order_number) AS total_orders, 
                COALESCE(SUM(o.shipping_price), 0) AS total_shipping_price
            FROM returned_orders o;
          """
        cursor.execute(total_shipping_returned_query)
        total_returned_orders,total_shipping_returned_price = cursor.fetchone()
        total_shipping_returned_price=total_shipping_returned_price-(60*total_returned_orders)
        total_shipping_problems_query = """
            SELECT 
                COUNT(o.order_number) AS total_orders, 
                COALESCE(SUM(o.shipping_price), 0) AS total_shipping_price
            FROM shipping o;
          """
        cursor.execute(total_shipping_problems_query)
        total_problem_orders,total_shipping_problem_price = cursor.fetchone()
        total_shipping_problem_price=total_shipping_problem_price-(60*total_problem_orders)
        total_shipping_completed_query = """
            SELECT 
                COALESCE(SUM(o.shipping_price), 0) AS total_shipping_price
            FROM orders o;
          """
        cursor.execute(total_shipping_completed_query)
        total_shipping_completed_price = cursor.fetchone()[0]
        total__profit = total_returned - total_shipping_returned_price
        total_can_be_gained=total_cancelled+total__profit
        total_profit=total_prices-(total_shipping_problem_price+total_shipping_returned_price+total_shipping_completed_price)
        total_shipping_price=total_shipping_problem_price+total_shipping_returned_price+total_shipping_completed_price
        completed_query = """
            SELECT 
                region, 
                COUNT(order_number) AS total_orders
            FROM orders
            GROUP BY region;
        """
        cursor.execute(completed_query)
        completed_data = cursor.fetchall()

        cancelled_query = """
            SELECT 
                region, 
                COUNT(order_number) AS total_orders
            FROM cancelled_orders
            GROUP BY region;
        """
        cursor.execute(cancelled_query)
        cancelled_data = cursor.fetchall()

        returned_query = """
            SELECT 
                region, 
                COUNT(order_number) AS total_orders
            FROM returned_orders
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
        completed__query = """
            SELECT 
                ship_company, 
                COUNT(order_number) AS total_orders
            FROM orders
            GROUP BY ship_company;
        """
        cursor.execute(completed__query)
        completed__data = cursor.fetchall()

        problem__query = """
            SELECT 
                ship_company, 
                COUNT(order_number) AS total_orders
            FROM shipping
            GROUP BY ship_company;
        """
        cursor.execute(problem__query)
        problem__data = cursor.fetchall()

        returned__query = """
            SELECT 
                ship_company, 
                COUNT(order_number) AS total_orders
            FROM returned_orders
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


        completed_date_query = """
            SELECT 
                order_date, 
                COUNT(order_number) AS total_orders
            FROM orders
            GROUP BY order_date
            ORDER BY order_date;
        """
        cursor.execute(completed_date_query)
        completed_date_data = cursor.fetchall()

        cancelled_date_query = """
            SELECT 
                order_date, 
                COUNT(order_number) AS total_orders
            FROM cancelled_orders
            GROUP BY order_date
            ORDER BY order_date;
        """
        cursor.execute(cancelled_date_query)
        cancelled_date_data = cursor.fetchall()

        returned_date_query = """
            SELECT 
                order_date, 
                COUNT(order_number) AS total_orders
            FROM returned_orders
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

        query="""SELECT COUNT(*) AS total_orders
                    FROM (
                        SELECT order_number FROM orders
                        UNION ALL
                        SELECT order_number FROM returned_orders
                        UNION ALL
                        SELECT order_number FROM shipping
                    ) AS all_orders;
                    """
        cursor.execute(query)
        total_orders=cursor.fetchone()[0]
        query = """SELECT SUM(hoodies) AS total_products
                FROM (
                    SELECT hoodies FROM orders
                    UNION ALL
                    SELECT hoodies FROM returned_orders
                    UNION ALL
                    SELECT hoodies FROM shipping
                ) AS all_orders;
                """
        cursor.execute(query)
        total_products = cursor.fetchone()[0]

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
                            f"{int(total_shipping_price/total_orders):,}".replace(",", "."),"",
                            "Total Shipping Price divide by total orders"
                        )
        with col2:
            metric_card_with_icon(
                            "Total Profit", 
                            f"{int(total_profit):,}".replace(",", "."),"",
                            "The total money gained from completed orders - total shipping coast."
                        )
        with col3:
             metric_card_with_icon(
                            "Total Profit could have been achieved", 
                            f"{int(total_can_be_gained):,}".replace(",", "."),"",
                            "The total money could have been achieved which is total profit from cancelled and returned orders"
                        )
        with col4:
             metric_card_with_icon(
                            " AVG Shipping Price per Product", 
                            f"{int(total_shipping_price/total_products):,}".replace(",", "."),"",
                            "Total Shipping Price divide by total products"
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
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_date["Date"],
            y=df_date["Completed"],
            mode="lines",
            name="Completed",
            line=dict(color="green", width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df_date["Date"],
            y=df_date["Cancelled"],
            mode="lines",
            name="Cancelled",
            line=dict(color="red", width=2, dash="dash")
        ))
        fig.add_trace(go.Scatter(
            x=df_date["Date"],
            y=df_date["Returned"],
            mode="lines",
            name="Returned",
            line=dict(color="orange", width=2, dash="dot")
        ))

        fig.update_layout(
            title="Number of Orders Over Time by Status",
            xaxis_title="Date",
            yaxis_title="Number of Orders",
            template="plotly_white",
            legend_title="Order Status"
        )

        st.plotly_chart(fig,use_container_width=True)
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
        cursor.execute("SELECT * FROM customers")
        cutomers = cursor.fetchall()
        conn.close()
        
        columns = ["Customer Name", "Customer Phone 1", "Customer Phone 2", "Email","Order Id"] 
        cutomers_df = pd.DataFrame(cutomers, columns=columns)
        cutomers_df.drop("Order Id",axis=1,inplace=True)
        st.dataframe(cutomers_df) 

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
        cursor.execute("SELECT * FROM activity_log ORDER BY timestamp DESC")
        logs = cursor.fetchall()
        conn.close()
        
        columns = ["Order iD", "Employee", "Action", "Timestamp", "Details"]
        logs_df = pd.DataFrame(logs, columns=columns)
        logs_df.drop("Order iD",axis=1,inplace=True)
        
        st.dataframe(logs_df) 
        
    elif page == "Completed Orders":
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: -60px; '>📦Completed Orders</h1>", unsafe_allow_html=True)
        selected_3 = option_menu(
            menu_title=None,
            options=["Add Order", "Search Orders", "View All Orders", 'Modify Orders',"Multiple Orders","Orders View","Delete Orders","Analysis"],
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
                ship_company = st.text_input("Shipping Company")
                region = st.selectbox("Region",egypt_governorates)
                order_number = st.text_input("Order Code")
                shipping_price = custom_number_input("Shipping Price", min_value=0, step=1)
                days_to_receive = custom_number_input("Days to Receive Order",min_value=0,step=1)
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
                            "SELECT 1 FROM orders WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order = cursor.fetchone()
                        cursor.execute(
                            "SELECT 1 FROM cancelled_orders WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order_1 = cursor.fetchone()
                        cursor.execute(
                            "SELECT 1 FROM returned_orders WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order_2 = cursor.fetchone()
                        if existing_order or existing_order_1 or existing_order_2:
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
                            total_count = sum(item["Count"] for item in st.session_state.order_products)
                            products_string = ", ".join([f"{item['Type']}:{item['Count']}" for item in st.session_state.order_products])
                            cursor.execute(
                                "INSERT INTO orders (customer_id, ship_company, region, order_price, order_number,days_to_receive,hoodies,shipping_price,products,order_date) VALUES (%s, %s, %s, %s, %s,%s,%s,%s,%s,%s)",
                                (customer_id, ship_company, region, order_price, order_number,days_to_receive,total_count,shipping_price,products_string,order_date)
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
            cursor.execute("SELECT DISTINCT ship_company FROM orders")
            ship_companies = [row[0] for row in cursor.fetchall()]
            selected_ship_company = st.selectbox("Filter by Shipping Company", ["All"] + ship_companies)
            sort_column = "CAST(o.order_number AS INTEGER)" if sort_by == "Order Code" else "o.order_price"
            sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
            
            query = f"""
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                c.email, o.ship_company, o.region, o.order_price,o.days_to_receive,o.hoodies,o.shipping_price,o.products,o.order_date
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
                        "Date":order[12],
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
                        "Type of products":order[11],
                        "Total number of Products":order[9],
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

        elif selected_3=="Modify Orders":
                st.header("Update or Remove Orders")
                
                st.subheader("Select an Order")
                search_order_number = st.text_input("Enter Order Code")

                if search_order_number:
                    conn = create_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute(
                        """
                        SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2,
                            c.email, o.ship_company, o.region, o.order_price,o.days_to_receive,o.hoodies,o.shipping_price,o.order_date,o.products
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
                        products_list = [
                            {"Type": p.split(":")[0], "Count": int(p.split(":")[1])}
                            for p in order_details[12].split(", ")
                        ]
                        st.subheader("Update Order")
                        new_name=st.text_input("Customer Name",value=order_details[1])
                        new_phone1=st.text_input("Customer Phone 1",value=order_details[2])
                        new_phone2=st.text_input("Customer Phone 1",value=order_details[3])
                        new_email=st.text_input("Email",value=order_details[4])
                        new_ship_company = st.text_input("Shipping Company", value=order_details[5])
                        new_region = st.selectbox("Region",egypt_governorates,index=egypt_governorates.index(order_details[6]))
                        new_order_price = custom_number_input("Order Price",value=order_details[7],min_value=0,step=1)
                        new_shipping_price = custom_number_input("Shipping Price",value=order_details[10],min_value=0,step=1)
                        new_days_to_receive=st.text_input("Days_to_receive",value=order_details[8])
                        new_date=st.date_input("Order Date",value=order_details[11])
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
                        if st.button("Update Order"):
                            updated_products = ", ".join(
                                [f"{item['Type']}:{item['Count']}" for item in st.session_state.modified_products]
                            )
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
                                SET ship_company = %s, region = %s, order_price = %s, days_to_receive = %s,
                                    hoodies = %s, shipping_price = %s, products = %s, order_date = %s
                                WHERE order_number = %s
                                """,
                                (
                                    new_ship_company, new_region, new_order_price, new_days_to_receive,
                                    sum(item["Count"] for item in st.session_state.modified_products),
                                    new_shipping_price, updated_products, new_date, search_order_number
                                )
                            )

                            conn.commit()
                            del st.session_state.modified_products
                            st.success("Order updated successfully!")
                            log_action(st.session_state.username,"Update Completed Order",f"Order ID: {search_order_number}, Customer: {new_name}")
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
                FROM customers c
                INNER JOIN orders o ON c.customer_id = o.customer_id
                GROUP BY c.customer_name, c.customer_phone_1, c.email
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
                total_product_count = 0
                product_summary = {}

                for row in consolidated_orders:
                    customer_name, customer_phone_1, email, order_numbers,date, order_count, total_price, total_shipping, product_details = row
                    customer_products = {}

                    if product_details:  
                        for product in product_details.split(', '): 
                            product_type, count = product.rsplit(':', 1) 
                            count = int(count)
                            customer_products[product_type] = customer_products.get(product_type, 0) + count
                            product_summary[product_type] = product_summary.get(product_type, 0) + count
                            total_product_count += count

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


        elif selected_3=="Delete Orders":
            query = """
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                c.email, o.ship_company, o.region, o.order_price, o.days_to_receive, 
                o.hoodies, o.shipping_price,o.order_date
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
                        "Date": order[11], 
                        "Customer Name": order[1],
                        "Phone 1": order[2],
                        "Phone 2": order[3],
                        "Email": order[4],
                        "Ship Company": order[5],
                        "Region": order[6],
                        "Order Price": order[7],
                        "Days to Receive": order[8],
                        "Total Number Of Produts": order[9],
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

                            delete_query = "DELETE FROM orders WHERE order_number IN %s"
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

            total_query = """
                SELECT 
                    COUNT(o.order_number) AS total_orders, 
                    COALESCE(SUM(o.hoodies), 0) AS total_products,
                    COALESCE(SUM(o.order_price), 0) AS total_prices,
                    COALESCE(SUM(o.shipping_price), 0) AS total_shipping_prices
                FROM orders o
                """
            cursor.execute(total_query)
            total_orders, total_products, total_prices, total_shipping_prices = cursor.fetchone()

            total_profit = total_prices - total_shipping_prices
            query = """
                SELECT 
                    o.region, 
                    COUNT(o.order_number) AS total_orders 
                FROM orders o
                GROUP BY o.region
                ORDER BY total_orders DESC
                """
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=["Region", "Total Orders"])
            total_orders_region = df['Total Orders'].sum()
            df['Percentage'] = (df['Total Orders'] / total_orders_region) * 100
            metrics_query = """
                    SELECT 
                        COALESCE(AVG(o.shipping_price::NUMERIC), 0) AS avg_shipping_price,
                        COALESCE(AVG(o.days_to_receive::NUMERIC), 0) AS avg_days_to_receive
                    FROM orders o
                """
            cursor.execute(metrics_query)
            avg_shipping_price,avg_day_to_receive = cursor.fetchone()
            
            shipping_company_query = """
                SELECT 
                    o.ship_company AS Shipping_Company,
                    COUNT(o.order_number) AS Total_Orders
                FROM orders o
                GROUP BY o.ship_company
                ORDER BY Total_Orders DESC
                """
            cursor.execute(shipping_company_query)
            shipping_data = cursor.fetchall()
            df_shipping = pd.DataFrame(shipping_data, columns=["Shipping Company", "Total Orders"])
            total_orders_shipping = df_shipping['Total Orders'].sum()
            df_shipping['Percentage'] = (df_shipping['Total Orders'] / total_orders_shipping) * 100
            total_cancelled_query="""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM cancelled_orders o
            """
            cursor.execute(total_cancelled_query)
            total_cancelled=cursor.fetchone()[0]
            total_returned_query="""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM returned_orders o
            """
            cursor.execute(total_returned_query)
            total_returned=cursor.fetchone()[0]
            date_query = """
                            SELECT 
                            o.order_date, 
                            COUNT(o.order_number) AS total_orders,
                            SUM(o.order_price) AS total_sales
                        FROM orders o
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

            query = """
            SELECT 
                o.order_number,
                o.products,
                o.shipping_price
            FROM orders o
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
            query = """
            SELECT 
                o.order_number,
                o.products,
                o.shipping_price,
                o.order_price
            FROM orders o
            """
            cursor.execute(query)
            data = cursor.fetchall()

            product_prices = {
                "hoodie": 850,
                "quarter zipper": 800,
                "default": 750  
            }

            total_product_prices = {}

            for order in data:
                order_number, products_str, total_shipping_price, total_order_price = order
                if not products_str:
                    continue  
                
                products_dict = parse_products(products_str)
                total_quantity = sum(products_dict.values())

                if len(products_dict) == 1: 
                    product_type = list(products_dict.keys())[0]
                    if product_type in total_product_prices:
                        total_product_prices[product_type] += total_order_price
                    else:
                        total_product_prices[product_type] = total_order_price
                else:
                    for product_type, quantity in products_dict.items():
                        unit_price = product_prices.get(product_type.lower(), product_prices["default"])
                        total_price_for_product = unit_price * quantity
                        if product_type in total_product_prices:
                            total_product_prices[product_type] += total_price_for_product
                        else:
                            total_product_prices[product_type] = total_price_for_product

            df_total_prices = pd.DataFrame(total_product_prices.items(),columns=["Product Type", "Total Price"])

            df_total_prices = df_total_prices.sort_values(by="Total Price", ascending=False)


            query = """
            SELECT 
                o.products
            FROM orders o
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
            conn.close()
            percentage_completed = total_orders / (total_orders + total_cancelled + total_returned)
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
                        "The average cost of shipping for all products."
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
                        f"{avg_shipping_price:.2f}".replace(",", "."),"",
                        "The average cost of shipping for all orders."
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

            with col4:
                    metric_card_with_icon(
                        "Total Profit", 
                        f"{int(total_profit):,}".replace(",", "."),"", 
                        "The total profit (total revenue minus total shipping cost)."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                    "Percentage of Completed Orders", 
                    f"{percentage_completed * 100:.2f}%", "", 
                    "The percentage of completed orders out of total orders."
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
                text="Total Shipping Price",
                color="Product Type"
            )
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
            fig = px.bar(
                df_total_prices,
                x="Product Type",
                y="Total Price",
                title="Price Distribution by Product Type",
                labels={"Total Price": "Price (Currency)"},
                template="plotly_white",
                text="Total Price",
                color="Product Type"
            )
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
            fig = px.bar(
                df_total_counts,
                x="Product Type",
                y="Total Quantity",
                title="Quantity Distribution by Product Type",
                labels={"Total Quantity": "Quantity (Currency)"},
                template="plotly_white",
                text="Total Quantity",
                color="Product Type"
            )
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
    elif page == "Cancelled Orders":
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: -60px; '>📦Cancelled Orders</h1>", unsafe_allow_html=True)
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
                order_date = st.date_input("Order Date")
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
                        cursor.execute(
                            "SELECT 1 FROM orders WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order_1 = cursor.fetchone()
                        cursor.execute(
                            "SELECT 1 FROM returned_orders WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order_2 = cursor.fetchone()
                        if existing_order or existing_order_1 or existing_order_2:
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
                                                (customer_id, region, order_number,reason,hoodies,order_price,order_date) 
                                                VALUES (%s, %s, %s,%s,%s,%s,%s)
                                                """,
                                                (customer_id, region, order_number,cancelled_reason,hoodies,order_price,order_date),
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
                        c.email,o.region,o.reason,o.hoodies,o.order_price,o.order_date
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
        elif selected_2=="View All Orders":            
            sort_by = st.selectbox("Sort by", ["Order Code"])
            sort_order = st.radio("Sort orders", ["Ascending", "Descending"])
            
            conn = create_connection()
            cursor = conn.cursor()
            sort_column = "CAST(o.order_number AS INTEGER)"
            sort_direction = "ASC" if sort_order == "Ascending" else "DESC"
            
            query = f"""
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                c.email,o.region,o.reason,o.hoodies,o.order_price,o.order_date
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
                        "Date": order[9],
                        "Customer Name": order[1],
                        "Phone 1": order[2],
                        "Phone 2": order[3],
                        "Email": order[4],
                        "Region": order[5],
                        "Reason":order[6],
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
                    """
                    SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2,
                        c.email, o.region,o.reason,o.hoodies,o.order_price,o.order_date
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
                        new_date=st.date_input("Order Date",value=order_details[9])
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
                                    SET region = %s,reason=%s,hoodies=%s,order_price=%s,order_date=%s
                                    WHERE order_number = %s
                                    """,
                                    (new_region, new_cancel_reason, new_cancel_hoodies, new_cancel_price, new_date, search_order_number)
                                )

                                conn.commit()
                                st.success("Order updated successfully!")
                                log_action(st.session_state.username, "Update Cancelled Order", f"Order ID: {search_order_number}, Customer: {new_name}")

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
                                log_action(st.session_state.username, "Delete Cancelled Order", f"Order ID: {search_order_number}, Customer: {new_name}")
                            else:
                                st.error("Incorrect password. Order deletion canceled.")
                else:
                    st.write("No order found with the given Order Number.")
                
                conn.close()
        elif selected_2=="Delete Orders":
            query = """
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                c.email,o.region,o.reason,o.hoodies,o.order_price,o.order_date
            FROM cancelled_orders o
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

                            delete_query = "DELETE FROM cancelled_orders WHERE order_number IN %s"
                            try:
                                with create_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute(delete_query, (orders_tuple,))
                                    conn.commit()
                                    st.success(f"Successfully deleted {len(selected_order_numbers)} orders.")
                                    log_action(st.session_state.username, "Delete Cancelled Order", f"Order ID: {selected_order_numbers}, Customers: {selected_customers}")
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

            total_query = """
                SELECT 
                    COUNT(o.order_number) AS total_orders, 
                    COALESCE(SUM(o.hoodies), 0) AS total_products,
                    COALESCE(SUM(o.order_price), 0) AS total_prices
                FROM cancelled_orders o
                """
            cursor.execute(total_query)
            total_orders, total_products, total_prices= cursor.fetchone()

            query = """
                SELECT 
                    o.region, 
                    COUNT(o.order_number) AS total_orders 
                FROM cancelled_orders o
                GROUP BY o.region
                ORDER BY total_orders DESC
                """
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=["Region", "Total Orders"])
            total_completed_query="""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM orders o
            """
            cursor.execute(total_completed_query)
            total_completed=cursor.fetchone()[0]
            total_returned_query="""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM returned_orders o
            """
            cursor.execute(total_returned_query)
            total_returned=cursor.fetchone()[0]

            reason_query = """
                SELECT 
                    o.reason AS reason,
                    COUNT(o.order_number) AS Total_Orders
                FROM cancelled_orders o
                GROUP BY o.reason
                ORDER BY Total_Orders DESC
                """
            cursor.execute(reason_query)
            reason_data = cursor.fetchall()
            df_reason = pd.DataFrame(reason_data, columns=["Reason", "Total Orders"])
            total_orders_all = df_reason['Total Orders'].sum()
            df_reason['Percentage'] = (df_reason['Total Orders'] / total_orders_all) * 100
            date_query = """
                        SELECT 
                            o.order_date, 
                            COUNT(o.order_number) AS total_orders,
                            SUM(o.order_price) AS total_sales
                        FROM cancelled_orders o
                        GROUP BY o.order_date
                        ORDER BY o.order_date
                    """
            cursor.execute(date_query)
            date_data = cursor.fetchall()
            df_date = pd.DataFrame(date_data, columns=["Date", "Total Orders", "Total Sales"])
            df_date["Date"] = pd.to_datetime(df_date["Date"])  
            df_date.sort_values(by="Date", inplace=True)  

            conn.close()
            percentage_cancelled = total_orders / (total_orders + total_completed + total_returned)
            percentage__cancelled = total_orders / (total_orders + total_returned)

            with col1:
                    metric_card_with_icon(
                        "Total Orders", 
                        f"{total_orders:,}","", 
                        "The total number of ordes."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                    "Percentage of Cancelled Orders", 
                    f"{percentage__cancelled * 100:.2f}%", "", 
                    "The percentage of cancelled orders out of cancelled and returned orders only."
                    )
            with col2:
                    metric_card_with_icon(
                        "Total Products", 
                        f"{total_products:,}","", 
                        "The total number of products cancelled."
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
                    "The percentage of cancelled orders out of total orders."
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
            st.plotly_chart(fig)

    elif page == "Returned Orders":
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: -60px; '>📦Returned Orders</h1>", unsafe_allow_html=True)
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
            ship_company = st.text_input("Shipping Company")
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
            if status=="Go Only":
                shipping_price = custom_number_input("Shipping Price", min_value=0,step=1)
            elif status=="Go And Back":
                go_shipping_price=custom_number_input("Go Shipping Price", min_value=0,step=1)
                back_shipping_price=custom_number_input("Bacck Shipping Price", min_value=0,step=1)
                shipping_price=go_shipping_price+back_shipping_price

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
                    else:
                        conn = create_connection()
                        cursor = conn.cursor()

                        cursor.execute(
                            "SELECT 1 FROM returned_orders WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order = cursor.fetchone()
                        cursor.execute(
                            "SELECT 1 FROM cancelled_orders WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order_1 = cursor.fetchone()
                        cursor.execute(
                            "SELECT 1 FROM orders WHERE order_number = %s",
                            (order_number,)
                        )
                        existing_order_2 = cursor.fetchone()
                        if existing_order or existing_order_1 or existing_order_2:
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
                            total_count = sum(item["Count"] for item in st.session_state.re_order_products)
                            products_string = ", ".join([f"{item['Type']}:{item['Count']}" for item in st.session_state.re_order_products])
                            cursor.execute(
                                "INSERT INTO returned_orders (customer_id, ship_company, region, order_number,reason,hoodies,order_price,shipping_price,status,products,order_date) VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s)",
                                (customer_id, ship_company, region, order_number,reason,total_count,order_price,shipping_price,status,products_string,order_date)
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
                        c.email, o.ship_company, o.region,o.reason,o.hoodies,o.order_price,o.shipping_price,o.products,o.order_date
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
        elif selected_1=="View All Orders":            
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
                c.email, o.ship_company, o.region, o.reason,o.hoodies,o.order_price,o.shipping_price,o.products,o.order_date
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
                        "Shipping Price in Shipping Company":order[10],
                        "Order Profit": (order[9] or 0) - (order[10] or 0),
                        "Type of Products": order[11],
                        "Actual Shipping Cost": (order[10] or 0) - 60,
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
                st.subheader("Select an Order")
                search_order_number = st.text_input("Enter Order Code")

                if search_order_number:
                    conn = create_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute(
                        """
                        SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2,
                            c.email, o.ship_company, o.region,o.reason,o.hoodies,o.order_price,o.shipping_price,o.order_date,o.status,o.products
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
                        products_list = [
                                {"Type": p.split(":")[0], "Count": int(p.split(":")[1])}
                                for p in order_details[13].split(", ")]
                        st.subheader("Update Order")
                        new_name=st.text_input("Customer Name",value=order_details[1])
                        new_phone1=st.text_input("Customer Phone 1",value=order_details[2])
                        new_phone2=st.text_input("Customer Phone 2",value=order_details[3])
                        new_email=st.text_input("Email",value=order_details[4])
                        new_ship_company = st.text_input("Shipping Company", value=order_details[5])
                        new_region = st.selectbox("Region",egypt_governorates,index=egypt_governorates.index(order_details[6]))
                        new_status=st.selectbox("Status",["Go Only","Go And Back"])
                        new_reason = st.selectbox("Reason",["Customer","Delvirey Man","Quality","Size","Team"])
                        new_price=custom_number_input("Order Price",value=order_details[9])
                        new_shipping_price=custom_number_input("Shipping Price",value=order_details[10])
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
                        new_date=st.date_input("Order Date",value=order_details[11])
                        if st.button("Update Order"):
                                updated_products = ", ".join(
                                    [f"{item['Type']}:{item['Count']}" for item in st.session_state.re_modified_products]
                                )
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
                                    SET ship_company = %s, region = %s,reason=%s,hoodies=%s,order_price=%s,shipping_price=%s,order_date=%s,status=%s,products=%s
                                    WHERE order_number = %s
                                    """,
                                    (new_ship_company, new_region, new_reason, sum(item["Count"] for item in st.session_state.re_modified_products), new_price, new_shipping_price, new_date, new_status,updated_products, search_order_number)
                                )
                                conn.commit()
                                del st.session_state.re_modified_products
                                st.success("Order updated successfully!")
                                log_action(st.session_state.username, "Update Returned Order", f"Order ID: {search_order_number}, Customer: {new_name}")

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
                                    log_action(st.session_state.username, "Delete Returned Order", f"Order ID: {search_order_number}, Customer: {new_name}")
                                else:
                                    st.error("Incorrect password. Order deletion canceled.")
                    else:
                        st.write("No order found with the given Order Number.")
                    
                    conn.close()
        elif selected_1=="Delete Orders":
            query = """
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                c.email, o.ship_company, o.region, o.reason,o.hoodies,o.order_price,o.shipping_price,o.order_date
            FROM returned_orders o
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
                        "Actual Shipping Cost": (order[10] or 0) - 60,
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

                            delete_query = "DELETE FROM returned_orders WHERE order_number IN %s"
                            try:
                                with create_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute(delete_query, (orders_tuple,))
                                    conn.commit()
                                    st.success(f"Successfully deleted {len(selected_order_numbers)} orders.")
                                    log_action(st.session_state.username, "Delete Returned Order", f"Order ID: {selected_order_numbers}, Customers: {selected_customers}")
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

            total_query = """
                SELECT 
                    COUNT(o.order_number) AS total_orders, 
                    COALESCE(SUM(o.hoodies), 0) AS total_products,
                    COALESCE(SUM(o.order_price), 0) AS total_prices,
                    COALESCE(SUM(o.shipping_price), 0) AS total_shipping_prices,
                    COALESCE(SUM(CASE WHEN o.status = 'Go Only' THEN o.shipping_price ELSE 0 END), 0) AS total_shipping_prices_go,
                    COALESCE(SUM(CASE WHEN o.status = 'Go And Back' THEN o.shipping_price ELSE 0 END), 0) AS total_shipping_prices_back
                FROM returned_orders o
                """
            cursor.execute(total_query)
            total_orders, total_products, total_prices, total_shipping_prices,total_shipping_prices_go,total_shipping_prices_back = cursor.fetchone()
            total_shipping_prices=(total_shipping_prices-(60*total_orders))
            total_profit = total_prices - total_shipping_prices
            query = """
                SELECT 
                    o.region, 
                    COUNT(o.order_number) AS total_orders 
                FROM returned_orders o
                GROUP BY o.region
                ORDER BY total_orders DESC
                """
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=["Region", "Total Orders"])
            total_orders_region = df['Total Orders'].sum()
            df['Percentage'] = (df['Total Orders'] / total_orders_region) * 100
            shipping_company_query = """
                SELECT 
                    o.ship_company AS Shipping_Company,
                    COUNT(o.order_number) AS Total_Orders
                FROM returned_orders o
                GROUP BY o.ship_company
                ORDER BY Total_Orders DESC
                """
            cursor.execute(shipping_company_query)
            shipping_data = cursor.fetchall()
            df_shipping = pd.DataFrame(shipping_data, columns=["Shipping Company", "Total Orders"])
            total_orders_shipping = df_shipping['Total Orders'].sum()
            df_shipping['Percentage'] = (df_shipping['Total Orders'] / total_orders_shipping) * 100
            total_cancelled_query="""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM cancelled_orders o
            """
            cursor.execute(total_cancelled_query)
            total_cancelled=cursor.fetchone()[0]
            total_completeed_query="""
            SELECT
                COUNT(o.order_number) AS total_orders
            FROM orders o
            """
            cursor.execute(total_completeed_query)
            total_comp=cursor.fetchone()[0]
            reason_query = """
                SELECT 
                    o.reason AS reason,
                    COUNT(o.order_number) AS Total_Orders
                FROM returned_orders o
                GROUP BY o.reason
                ORDER BY Total_Orders DESC
                """
            cursor.execute(reason_query)
            reason_data = cursor.fetchall()
            df_reason = pd.DataFrame(reason_data, columns=["Reason", "Total Orders"])
            total_orders_all = df_reason['Total Orders'].sum()
            df_reason['Percentage'] = (df_reason['Total Orders'] / total_orders_all) * 100
            status_query = """
                SELECT 
                    o.status AS status,
                    COUNT(o.order_number) AS Total_Orders
                FROM returned_orders o
                GROUP BY o.status
                ORDER BY Total_Orders DESC
                """
            cursor.execute(status_query)
            status_data = cursor.fetchall()
            df_status = pd.DataFrame(status_data, columns=["Status", "Total Orders"])
            total_orders_all = df_reason['Total Orders'].sum()
            df_status['Percentage'] = (df_status['Total Orders'] / total_orders_all) * 100
            date_query = """
                        SELECT 
                            o.order_date, 
                            COUNT(o.order_number) AS total_orders,
                            SUM(o.order_price) AS total_sales
                        FROM returned_orders o
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

            query = """
            SELECT 
                o.order_number,
                o.products,
                o.shipping_price
            FROM returned_orders o
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
                    shipping_price_for_product = (quantity / total_quantity) * (total_shipping_price-60)

                    if product_type in product_shipping:
                        product_shipping[product_type] += shipping_price_for_product
                    else:
                        product_shipping[product_type] = shipping_price_for_product

            df__shipping = pd.DataFrame(product_shipping.items(), columns=["Product Type", "Total Shipping Price"])
            df__shipping = df__shipping.sort_values(by="Total Shipping Price", ascending=False)
            shipping_company_query = """
                SELECT 
                    o.status AS Status,
                    SUM(o.shipping_price - 60) AS Total_Shipping_Cost
                FROM returned_orders o
                GROUP BY o.status
                ORDER BY Total_Shipping_Cost DESC
            """
            cursor.execute(shipping_company_query)
            shipping_data = cursor.fetchall()

            df___shipping = pd.DataFrame(shipping_data, columns=["Status", "Total Shipping Cost"])
            total_shipping_cost = df___shipping["Total Shipping Cost"].sum()
            df___shipping["Percentage"] = (df___shipping["Total Shipping Cost"] / total_shipping_cost) * 100
            shipping_company_query = """
                SELECT 
                    o.reason AS Reason,
                    SUM(o.shipping_price - 60) AS Total_Shipping_Cost
                FROM returned_orders o
                GROUP BY o.reason
                ORDER BY Total_Shipping_Cost DESC
            """
            cursor.execute(shipping_company_query)
            shipping_data = cursor.fetchall()

            df____shipping = pd.DataFrame(shipping_data, columns=["Reason", "Total Shipping Cost"])
            total_shipping_cost = df____shipping["Total Shipping Cost"].sum()
            df___shipping["Percentage"] = (df____shipping["Total Shipping Cost"] / total_shipping_cost) * 100

            conn.close()
            percentage_returned = total_orders / (total_orders + total_cancelled + total_comp)
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
                        "perctange of total shipping cost for orders which go only."
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
                        "perctange of total shipping cost for orders which go and back."
                    )

            with col3:
                    metric_card_with_icon(
                        "Total Shipping Price", 
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
                        "The total profit (total revenue minus total shipping cost)."
                    )
                    st.markdown("")
                    metric_card_with_icon(
                    "Percentage of Returned Orders", 
                    f"{percentage__returned * 100:.2f}%", "", 
                    "The percentage of returned orders out of cancelled and returned orders only."
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
                text="Total Shipping Price",
                color="Product Type"
            )
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
                        
            fig = px.bar(
                df___shipping,
                x="Status",
                y="Total Shipping Cost",
                title="Shipping Price Distribution by Status",
                labels={"Total Shipping Cost": "Shipping Cost (Currency)"},
                template="plotly_white",
                text="Total Shipping Cost",
                color="Status"
            )
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
            fig = px.bar(
                df____shipping,
                x="Reason",
                y="Total Shipping Cost",
                title="Shipping Price Distribution by Reason",
                labels={"Total Shipping Cost": "Shipping Cost (Currency)"},
                template="plotly_white",
                text="Total Shipping Cost",
                color="Reason"
            )
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
    elif page == "Problems":
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: -60px; '>🚨Problems</h1>", unsafe_allow_html=True)
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
            status = st.selectbox("Status", ["Exchanged", "Delivery Man", "Team"])

            if status == "Delivery Man":
                reason = "Delivery Man"
            elif status == "Team":
                reason="Team"
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
            shipping_price = custom_number_input("Shipping Price", min_value=0, step=1)
            if st.button("Add Order"):
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
                elif shipping_price is None or shipping_price < 0:
                    st.error("Order Price is required.")
                else:
                    conn = create_connection()
                    cursor = conn.cursor()
                    
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
                    total_count = sum(item["Count"] for item in st.session_state.sh_order_products)
                    products_string = ", ".join([f"{item['Type']}:{item['Count']}" for item in st.session_state.sh_order_products])
                    cursor.execute(
                            "INSERT INTO shipping (customer_id, ship_company, region, order_number, status, shipping_price, hoodies,products,reason) VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s)",
                            (customer_id, ship_company, region, order_number, status, shipping_price, total_count,products_string,reason)
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
                        c.email, o.ship_company, o.region,o.status,o.shipping_price,o.hoodies,o.reason,o.products
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
        elif selected=="View All Orders":
            st.markdown("")
            st.markdown("")
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
                c.email, o.ship_company, o.region, o.status,o.shipping_price,o.hoodies,o.reason,o.products
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
                        "Shipping Price In Shipping Company":order[8],
                        "Actual Shipping Cost": (order[8] or 0) - 60,
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
                    """
                    SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2,
                        c.email, o.ship_company, o.region,o.status,o.shipping_price,o.hoodies,o.reason,o.products
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
                    products_list = [
                            {"Type": p.split(":")[0], "Count": int(p.split(":")[1])}
                            for p in order_details[11].split(", ")]
                    st.subheader("Update Order")
                    new_name=st.text_input("Customer Name",value=order_details[1])
                    new_phone1=st.text_input("Customer Phone 1",value=order_details[2])
                    new_phone2=st.text_input("Customer Phone 2",value=order_details[3])
                    new_email=st.text_input("Email",value=order_details[4])
                    new_ship_company = st.text_input("Shipping Company", value=order_details[5])
                    new_region = st.selectbox("Region",egypt_governorates,index=egypt_governorates.index(order_details[6]))
                    new_status = st.selectbox("Status",["Delivery Man","Exchanged","Team"])
                    new_price=custom_number_input("Shipping Price",value=order_details[8])
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

                    if new_status == "Delivery Man":
                        new_problem_reason = "Delivery Man"
                    elif new_status == "Team":
                        new_problem_reason="Team"
                    elif new_status =="Exchanged":
                        new_problem_reason=st.selectbox("Reason",["Size","Quality"])
                    if st.button("Update Order"):
                                updated_products = ", ".join(
                                [f"{item['Type']}:{item['Count']}" for item in st.session_state.sh_modified_products]
                                  )
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
                                    SET ship_company = %s, region = %s,status=%s,shipping_price=%s,hoodies=%s,reason=%s,products=%s
                                    WHERE order_number = %s
                                    """,
                                    (new_ship_company, new_region, new_status,new_price,sum(item["Count"] for item in st.session_state.sh_modified_products), new_problem_reason,updated_products, search_order_number)
                                )


                                conn.commit()
                                del st.session_state.sh_modified_products
                                st.success("Order updated successfully!")
                                log_action(st.session_state.username, "Update Shipping Problem", f"Order ID: {search_order_number}, Customer: {new_name}")

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
                                log_action(st.session_state.username, "Delete Shipping Problem", f"Order ID: {search_order_number}, Customer: {new_name}")
                            else:
                                st.error("Incorrect password. Order deletion canceled.")
                else:
                    st.write("No order found with the given Order Number.")
                
                conn.close()
        elif selected=='Delete Orders':
            query = """
            SELECT o.order_number, c.customer_name, c.customer_phone_1, c.customer_phone_2, 
                c.email, o.ship_company, o.region, o.status,o.shipping_price,o.hoodies,o.reason
            FROM shipping o
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
                        "Actual Shipping Cost": (order[8] or 0) - 60,
                        "Number of Products":order[9]
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

                            delete_query = "DELETE FROM shipping WHERE order_number IN %s"
                            try:
                                with create_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute(delete_query, (orders_tuple,))
                                    conn.commit()
                                    st.success(f"Successfully deleted {len(selected_order_numbers)} orders.")
                                    log_action(st.session_state.username, "Delete Problem", f"Order ID: {selected_order_numbers}, Customers: {selected_customers}")
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

            total_query = """
                SELECT 
                    COUNT(o.order_number) AS total_orders, 
                    COALESCE(SUM(o.hoodies), 0) AS total_products,
                    COALESCE(SUM(o.shipping_price), 0) AS total_shipping_prices
                FROM shipping o
                """
            cursor.execute(total_query)
            total_orders, total_products, total_shipping_prices = cursor.fetchone()
            total_shipping_prices=total_shipping_prices-(60*total_orders)
            query = """
                SELECT 
                    o.region, 
                    COUNT(o.order_number) AS total_orders 
                FROM shipping o
                GROUP BY o.region
                ORDER BY total_orders DESC
                """
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=["Region", "Total Orders"])
            total_orders_region = df['Total Orders'].sum()
            df['Percentage'] = (df['Total Orders'] / total_orders_region) * 100
            shipping_company_query = """
                SELECT 
                    o.ship_company AS Shipping_Company,
                    COUNT(o.order_number) AS Total_Orders
                FROM shipping o
                GROUP BY o.ship_company
                ORDER BY Total_Orders DESC
                """
            cursor.execute(shipping_company_query)
            shipping_data = cursor.fetchall()
            df_shipping = pd.DataFrame(shipping_data, columns=["Shipping Company", "Total Orders"])
            total_orders_shipping = df_shipping['Total Orders'].sum()
            df_shipping['Percentage'] = (df_shipping['Total Orders'] / total_orders_shipping) * 100
            reason_query = """
                SELECT 
                    o.reason AS reason,
                    COUNT(o.order_number) AS Total_Orders
                FROM shipping o
                GROUP BY o.reason
                ORDER BY Total_Orders DESC
                """
            cursor.execute(reason_query)
            reason_data = cursor.fetchall()
            df_reason = pd.DataFrame(reason_data, columns=["Reason", "Total Orders"])
            total_orders_all = df_reason['Total Orders'].sum()
            df_reason['Percentage'] = (df_reason['Total Orders'] / total_orders_all) * 100
            status_query = """
                SELECT 
                    o.status AS status,
                    COUNT(o.order_number) AS Total_Orders
                FROM shipping o
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

            query = """
            SELECT 
                o.order_number,
                o.products,
                o.shipping_price
            FROM shipping o
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
                    shipping_price_for_product = (quantity / total_quantity) * (total_shipping_price-60)

                    if product_type in product_shipping:
                        product_shipping[product_type] += shipping_price_for_product
                    else:
                        product_shipping[product_type] = shipping_price_for_product

            df__shipping = pd.DataFrame(product_shipping.items(), columns=["Product Type", "Total Shipping Price"])
            df__shipping = df__shipping.sort_values(by="Total Shipping Price", ascending=False)
            shipping_company_query = """
                SELECT 
                    o.status AS Status,
                    SUM(o.shipping_price - 60) AS Total_Shipping_Cost
                FROM shipping o
                GROUP BY o.status
                ORDER BY Total_Shipping_Cost DESC
            """
            cursor.execute(shipping_company_query)
            shipping_data = cursor.fetchall()

            df_shipping_status = pd.DataFrame(shipping_data, columns=["Status", "Total Shipping Cost"])
            total_shipping_cost = df_shipping_status["Total Shipping Cost"].sum()
            df_shipping_status["Percentage"] = (df_shipping_status["Total Shipping Cost"] / total_shipping_cost) * 100
            shipping_company_query = """
                SELECT 
                    o.reason AS Reason,
                    SUM(o.shipping_price - 60) AS Total_Shipping_Cost
                FROM shipping o
                GROUP BY o.reason
                ORDER BY Total_Shipping_Cost DESC
            """
            cursor.execute(shipping_company_query)
            shipping_data = cursor.fetchall()

            df_shipping_reason = pd.DataFrame(shipping_data, columns=["Reason", "Total Shipping Cost"])
            total_shipping_cost = df_shipping_reason["Total Shipping Cost"].sum()
            df_shipping_reason["Percentage"] = (df_shipping_reason["Total Shipping Cost"] / total_shipping_cost) * 100
            conn.close()
            avg_shipping_price= total_shipping_prices/total_orders
            avg_shipping_price_1=total_shipping_prices/total_products
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
                text="Total Shipping Price",
                color="Product Type"
            )
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
            fig = px.bar(
                df_shipping_status,
                x="Status",
                y="Total Shipping Cost",
                title="Shipping Price Distribution by Status",
                labels={"Total Shipping Cost": "Shipping Cost (Currency)"},
                template="plotly_white",
                text="Total Shipping Cost",
                color="Status"
            )
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
            fig = px.bar(
                df_shipping_reason,
                x="Reason",
                y="Total Shipping Cost",
                title="Shipping Price Distribution by Reason",
                labels={"Total Shipping Cost": "Shipping Cost (Currency)"},
                template="plotly_white",
                text="Total Shipping Cost",
                color="Reason"
            )
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            st.plotly_chart(fig,use_container_width=True)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    orders_management_page()
else:
    login_page()
