import sys
import streamlit as st
import pandas as pd
from pandasql import sqldf
import numpy as np
import ydata_profiling
from streamlit_ydata_profiling import st_profile_report
from ydata_profiling import ProfileReport
import openpyxl
import pygwalker as pyg
import pandas as pd

# Setting up web app page
st.set_page_config(page_title='Exploratory Data Analysis App', page_icon=None, layout="wide")

# Creating section in sidebar
st.sidebar.write("****FILE UPLOAD****")

# User prompt to select file type
ft = st.sidebar.selectbox("*Select file type*",["Excel", "csv"])

# Creating dynamic file upload option in sidebar
uploaded_file = st.sidebar.file_uploader("*Upload file*")

if uploaded_file is not None:
    file_path = uploaded_file

    if ft == 'Excel':
        try:
            # User prompt to select sheet name in uploaded Excel
            sh = st.sidebar.selectbox("*Select sheet name:*",pd.ExcelFile(file_path).sheet_names)
            # User prompt to define row with column names if they aren't in the header row in the uploaded Excel
            h = st.sidebar.number_input("*Select row number for header names:*",0,10)
        except:
            st.info("File is not recognised as an Excel file")
            sys.exit()
    
    elif ft == 'csv':
        try:
            #No need for sh and h for csv, set them to None
            sh = None
            h = None
        except:
            st.info("File is not recognised as a csv file.")
            sys.exit()

    #Caching function to load data
    @st.cache_data(experimental_allow_widgets=True)
    def load_data(file_path,ft,sh,h):
        
        if ft == 'Excel':
            try:
                #Reading the excel file
                data = pd.read_excel(file_path,header=h,sheet_name=sh,engine='openpyxl')
            except:
                st.info("File is not recognised as an Excel file.")
                sys.exit()
    
        elif ft == 'csv':
            try:
                #Reading the csv file
                data = pd.read_csv(file_path)
            except:
                st.info("File is not recognised as a csv file.")
                sys.exit()
        
        return data

    data = load_data(file_path,ft,sh,h)

    # Select which section to show
    selected = st.sidebar.radio( "****MENU****", 
                                    ["Dataset overview",
                                    "Data Summarization and Profiling",
                                    "Interactive Visual Exploration", 
                                    "Statistical Experimentation"])

## 1. Overview of the data
    st.write( '### 1. Dataset Preview ')

    try:
      #View the dataframe in streamlit
      st.dataframe(data, use_container_width=True)

    except:
      st.info("Error reading file. Please ensure that the input parameters are correctly defined.")
      sys.exit()