import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# def load_data():
#      spark = SparkSession.builder.appName("IFCOVisualization").getOrCreate()
#      df = spark.read.table("crate_order_distribution.csv").toPandas()
#      return df

# Load the DataFrame saved from Jupyter
# df_order_dist = pd.read_csv("/home/mooney/de_projects/ifco_project/crate_order_distribution.csv") 
df_order_dist = pd.read_csv("/app/data/crate_order_distribution.csv") 

# Streamlit UI
st.title("IFCO Data Analytics Dashboard")
st.write("This dashboard displays analytics data from Jupyter.")

########### Order & Crate Data ##############

st.header("1. Distribution of orders by crate type:")
# Show DataFrame
st.caption("Data Preview:")
st.dataframe(df_order_dist)

# Create a simple bar chart
st.subheader("Distribution of orders by crate type:")
st.bar_chart(df_order_dist.set_index("crate_type"))

########### Sales Owner list ##############
st.header("2. Sales owners list for training:")
st.write("To improve selling on plastic crate based on the last 12 months orders")

## Load the DataFrame saved from Jupyter 
# df_training_list = pd.read_csv("/home/mooney/de_projects/ifco_project/crate_sale_distribution.csv") 
df_training_list = pd.read_csv("/app/data/crate_sale_distribution.csv") 
# Filter where crate_type is 'Plastic'
filtered_df = df_training_list[df_training_list['crate_type'] == 'Plastic'].drop(columns=['crate_type'])
# Show DataFrame
st.caption("Data Preview:")
st.dataframe(filtered_df)

# Create a simple bar chart
st.bar_chart(filtered_df.set_index("salesowner"))

########### Sales Owner list ##############
st.header("3. Top 5 performers selling plastic crates")

## Load the DataFrame saved from Jupyter 
# df_top_5 = pd.read_csv("/home/mooney/de_projects/ifco_project/sales_top_5.csv") 
df_top_5 = pd.read_csv("/app/data/sales_top_5.csv") 

# Show DataFrame
st.caption("Data Preview:")
st.dataframe(df_top_5)

st.bar_chart(df_top_5.set_index("salesowner"))

# import pandas as pd
# df = pd.read_csv("/home/mooney/de_projects/ifco_project/crate_order_distribution.csv") 
# print(df.head())
