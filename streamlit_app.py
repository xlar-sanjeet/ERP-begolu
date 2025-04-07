import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import math




# Display title and description

st.title("Begolu Mal Check by xlar")

# Establishing a google sheets connection
# Clear Streamlit's cache for the connection
# st.cache_data.clear()
# @st.cache_data(ttl=0, show_spinner=False)
def fetch_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    inv_ws = conn.read(worksheet="products", ttl=5)
    real_time = conn.read(worksheet="real_time_inventory",ttl=5)
    sell_ws = conn.read(worksheet="sell",ttl=5)
    return conn, inv_ws.dropna(how="all"), real_time.dropna(how="all"), sell_ws.dropna(how="all")

# Fetch latest data
conn, inv_ws, real_time, sell_ws = fetch_data()


try:
    num_kurtis = inv_ws["Category"].value_counts().get("Kurti", 0)
    num_sarees = inv_ws["Category"].value_counts().get("Saree", 0)
    num_jewels = inv_ws["Category"].value_counts().get("Jewellery", 0)
    num_shoes = inv_ws["Category"].value_counts().get("Shoes", 0)
except KeyError:
    print("error")
    num_kurtis,num_sarees,num_jewels,num_shoes = 0,0,0,0
# NUM = 0


def gen_code(ptype,color, id_num = 1, BorS = "Buy"):
    global NUM 
    NUM = id_num
    # print(NUM)
    if BorS == "Buy":
        if ptype == "Kurti":
            t = "KU"
            NUM += num_kurtis
        elif ptype == "Saree":
            t = "SR"
            NUM += num_sarees
        elif ptype == "Jewellery":
            t = "JR"
            NUM += num_jewels
        elif ptype == "Shoes":
            t = "SH"
            NUM += num_shoes

        return t +"-"+color+"-"+str(NUM).zfill(6)
    
    else:
        if ptype == "Kurti":
            t = "KU"
            # NUM += num_kurtis
        elif ptype == "Saree":
            t = "SR"
            # NUM += num_sarees
        elif ptype == "Jewellery":
            t = "JR"
            # NUM += num_jewels
        elif ptype == "Shoes":
            t = "SH"
            # NUM += num_shoes

        return t +"-"+color+"-"+str(NUM).zfill(6)
    
    


# existing_data = existing_data.dropna(how="all")

# st.dataframe(inv_ws)

# Predefined Options
PRODUCTS = ["Kurti", "Saree", "Jewellery", "Shoes"]

KURTI_SIZES = ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL","36","38","40","42","44","46"]
SAREE_COLORS = ["1", "2", "3", "4", "5", "6", "7", "8"]
JEWELS = ["1", "2", "3", "4", "5", "6"]
SHOES = ["5", "6", "7", "8", "9","10", "11", "12", "13", "14","37","38", "39", "40", "41", "42",]
COLORS = ["ORANGE","WHITE","RED","DARK_BLUE","SKY_BLUE","YELLOW","GREEN","GREY","PURPLE","PEA_GREEN","BLACK","MAROON","PINK"]

# Sidebar menu
tab = st.sidebar.radio("Menu", ["Inventory", "Sell", "Sales History", "product info", "del_entry"], key="menu_radio")

if tab == "Inventory":
    # st.subheader("Add New Item")
    st.markdown("Enter the details of the new product below")

    # item = st.text_input("Item name")
    category = st.selectbox("Select Product Category", PRODUCTS)

    # Dynamically show size options
    size = None
    if category == "Kurti":
        size = st.multiselect("Select kurti Sizes", options=KURTI_SIZES, key="kurti")
        quantity = len(size)
    elif category == "Saree":
        size = st.selectbox("Select num-Colors", options=SAREE_COLORS, key="saree")
        quantity = int(size)
    elif category == "Jewellery":
        size = st.selectbox("Select num-Jewellery", options=JEWELS, key="jewels")
        quantity = int(size)
    elif category == "Shoes":
        size = st.multiselect("Select Shoe Size", options=SHOES, key="shoes")
        quantity = len(size)

    color = st.selectbox("Select color", options = COLORS)

    cost_price = st.text_input("Enter price")

    try:
        total_price = float(cost_price) * quantity
    except ValueError:
        total_price = 0

    code = gen_code(category, color)

    if st.button("Submit"):
        if category and size:
            st.success(f"✅ Added:{category}, {size}, {quantity}")

            new_row = pd.DataFrame([{
                        "Category":category,
                        "Code": code,
                        "Size": size if isinstance(size, str) else ",".join(size),
                        "Color": color,
                        "Quantity": quantity,
                        "Cost Price": cost_price,
                        "Total Price": total_price,
                        "Date Added" : pd.Timestamp.now().strftime("%Y-%m-%d"),
                                        }])    

            # 🔄 RE-fetch directly before writing
            # conn = st.connection("gsheets", type=GSheetsConnection)
            # latest_inv = conn.read(worksheet="products").dropna(how="all")
            # latest_rt = conn.read(worksheet="real_time_inventory").dropna(how="all")
            # conn, latest_inv, latest_rt = fetch_data()

            # ✅ Append the row
            updated_inv = pd.concat([inv_ws, new_row], ignore_index=True)
            # updated_rt = pd.concat([real_time, new_row], ignore_index=True)

            # ✅ Write back
            conn.update(worksheet="products", data=updated_inv)
            conn.update(worksheet="real_time_inventory", data=updated_inv)
                
            st.success("✅ Added to inventory and saved to Google Sheet!")
        else:
            st.error("❌ Please fill in all fields before submitting.")


elif tab == "Sell":
    st.markdown("Enter the details of the sold product below")
    # item = st.text_input("Item name")
    category = st.selectbox("Select Product Category", PRODUCTS)

    # Dynamically show size options
    size = None
    if category == "Kurti":
        size = st.multiselect("Select kurti Sizes", options=KURTI_SIZES, key="kurti")
        quantity = len(size)
    elif category == "Saree":
        size = st.selectbox("Select num-Colors", options=SAREE_COLORS, key="saree")
        quantity = int(size)
    elif category == "Jewellery":
        size = st.selectbox("Select num-Jewellery", options=JEWELS, key="jewels")
        quantity = int(size)
    elif category == "Shoes":
        size = st.multiselect("Select Shoe Size", options=SHOES, key="shoes")
        quantity = len(size)

    color = st.selectbox("Select color", options = COLORS)

    num = st.text_input("Add the identity number")

    sell_price = st.text_input("Enter price")

    try:
        total_sell_price = float(sell_price) * quantity
    except ValueError:
        total_sell_price = 0

    code = gen_code(category, color, id_num = num, BorS = "Sell")

    if st.button("Submit"):
        if category and size:
            st.success(f"✅ Added:{category}, {size}, {quantity}")

            real_time_updated = real_time.copy()

            if code in real_time_updated["Code"].values:
                idx = real_time_updated[real_time_updated["Code"] == code].index[0]

                # Original Data
                old_qty = real_time_updated.at[idx, "Quantity"]
                old_size = real_time_updated.at[idx, "Size"]
                cost_price = real_time_updated.at[idx, "Cost Price"]
                profit = math.ceil(((int(sell_price) - int(cost_price)) * quantity))
                profit_cent = math.ceil((profit/cost_price * 100))

                # Convert old sizes to a list
                if category == "Kurti" or category == "Shoes":
                    old_sizes_list = [s.strip() for s in old_size.split(",")]
                    sold_sizes = size if isinstance(size, list) else [size]
                    # New sizes = remove sold ones
                    new_sizes_list = [s for s in old_sizes_list if s not in sold_sizes]

                    # Update the values
                    new_qty = max(0, int(old_qty) - quantity)
                    new_size_str = ", ".join(new_sizes_list)
                else:
                    new_qty = max(0, int(old_qty) - quantity)
                    new_size_str = str(new_qty)

                if new_qty == 0:
                    real_time_updated = real_time_updated.drop(index=idx)
                else:
                    real_time_updated.at[idx, "Quantity"] = new_qty
                    real_time_updated.at[idx, "Size"] = new_size_str

            new_row = pd.DataFrame([{
                        "Category":category,
                        "Code": code,
                        "Size": size if isinstance(size, str) else ", ".join(size),
                        "Color": color,
                        "Quantity": quantity,
                        "Sell Price": sell_price,
                        "Cost Price": cost_price,
                        "Profit": profit,
                        "Profit Cent": str(profit_cent) + " %" ,
                        "Revenue": total_sell_price,
                        "Date Added" : pd.Timestamp.now().strftime("%Y-%m-%d"),
                                        }])    

            # Combine with existing data and remove empty rows
            updated_sell = pd.concat([sell_ws.dropna(how='all'), new_row], ignore_index=True)
            
            
            # Push to google sheet
            conn.update(worksheet="sell", data=updated_sell)
            conn.update(worksheet="real_time_inventory", data=real_time_updated)
            
            
            st.success("✅ Added to inventory and saved to Google Sheet!")
        else:
            st.error("❌ Please fill in all fields before submitting.")

elif tab == "product info":
    st.markdown("Enter the details of the product below")
    # item = st.text_input("Item name")
    category = st.selectbox("Select Product Category", PRODUCTS)

    color = st.selectbox("Select color", options = COLORS)

    num = st.text_input("Add the identity number")

    code = gen_code(category, color, id_num = num, BorS = "Sell")

    real_time_updated = real_time.copy()
    if code in real_time_updated["Code"].values:
                idx = real_time_updated[real_time_updated["Code"] == code].index[0]

                # Original Data
                old_qty = real_time_updated.at[idx, "Quantity"]
                old_size = real_time_updated.at[idx, "Size"]

    if st.button("check"):
        if old_qty and old_size:
            st.success(f"✅ Quantiy:{old_qty}, Size: {old_size}")
        else:
            st.error("Not available") 

elif tab == "del_entry":
    st.markdown("Enter the details of the product to be deleted below")

    category = st.selectbox("Select Product Category", PRODUCTS)

    # Dynamically show size options
    size = None
    if category == "Kurti":
        size = st.multiselect("Select kurti Sizes", options=KURTI_SIZES, key="kurti")
        quantity = len(size)
    elif category == "Saree":
        size = st.selectbox("Select num-Colors", options=SAREE_COLORS, key="saree")
        quantity = int(size)
    elif category == "Jewellery":
        size = st.selectbox("Select num-Jewellery", options=JEWELS, key="jewels")
        quantity = int(size)
    elif category == "Shoes":
        size = st.multiselect("Select Shoe Size", options=SHOES, key="shoes")
        quantity = len(size)

    color = st.selectbox("Select color", options = COLORS)

    num = st.text_input("Add the identity number")

    code = gen_code(category, color, id_num = num, BorS = "Sell")

    real_time_updated = real_time.copy()

    if code in real_time_updated["Code"].values:
                idx = real_time_updated[real_time_updated["Code"] == code].index[0]

                # Original Data
                old_qty = real_time_updated.at[idx, "Quantity"]
                old_size = real_time_updated.at[idx, "Size"]

                # Convert old sizes to a list
                if category == "Kurti" or category == "Shoes":
                    old_sizes_list = [s.strip() for s in old_size.split(",")]
                    sold_sizes = size if isinstance(size, list) else [size]
                    # New sizes = remove sold ones
                    new_sizes_list = [s for s in old_sizes_list if s not in sold_sizes]

                    # Update the values
                    new_qty = max(0, int(old_qty) - quantity)
                    new_size_str = ", ".join(new_sizes_list)
                else:
                    new_qty = max(0, int(old_qty) - quantity)
                    new_size_str = str(new_qty)

                if new_qty == 0:
                    real_time_updated = real_time_updated.drop(index=idx)
                else:
                    real_time_updated.at[idx, "Quantity"] = new_qty
                    real_time_updated.at[idx, "Size"] = new_size_str

    if st.button("check"):
            conn.update(worksheet="real_time_inventory", data=real_time_updated)
            st.success(f"✅ Deleted:{category}, {size}, {quantity}")
            
    else:
        st.error("Not available")                             

else:
    st.markdown("Enter the details of date range to access sales history")

    start = st.date_input("Enter start date", datetime.date(2025, 4, 6), min_value = datetime.date(2025, 4, 6))
    end = st.date_input("Enter End date", "today", max_value = "today")

    # Convert the column to datetime if not already
    sell_ws["Date Added"] = pd.to_datetime(sell_ws["Date Added"])

    # Filter by date range
    mask = (sell_ws["Date Added"].dt.date >= start) & (sell_ws["Date Added"].dt.date <= end)
    date_range = sell_ws.loc[mask]

    inv_ws["Date Added"] = pd.to_datetime(inv_ws["Date Added"])
     # Filter by date range
    mask_inv = (inv_ws["Date Added"].dt.date >= start) & (inv_ws["Date Added"].dt.date <= end)
    inv_date_range = inv_ws.loc[mask_inv]


    # Calculate metrics
    if not date_range.empty:
        try:
            date_range["Profit"] = pd.to_numeric(date_range["Profit"], errors="coerce")
            date_range["Revenue"] = pd.to_numeric(date_range["Sell Price"], errors="coerce")
            total_profit = date_range["Profit"].sum()
            total_revenue = date_range["Revenue"].sum()

            inv_date_range["Total Price"] = pd.to_numeric(inv_date_range["Total Price"], errors="coerce")
            total_investment = inv_date_range["Total Price"].sum()

        except KeyError:
            total_profit = total_revenue = 0
    else:
        total_profit = total_revenue = 0

    # Show results
    if st.button("Calculate"):
        if total_profit or total_revenue:
            st.success(f"📅 Start: `{start}` → End: `{end}` \n\n💰 Total Investment: **₹{total_investment:.2f}**  \n💰 Total Profit: **₹{total_profit:.2f}**  \n📈 Total Revenue: **₹{total_revenue:.2f}**")
        else:
            st.error("No data available for the selected range.")

