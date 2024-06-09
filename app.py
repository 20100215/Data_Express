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

# Page title and headline
st.sidebar.title('📊🚀 Data Express')
st.sidebar.subheader('Unleash your data\'s potential in minutes!')

# User prompt to select file type
ft = st.sidebar.selectbox("*Select file type*",["CSV", "Excel"])

# Caching function to load data
@st.cache_data(experimental_allow_widgets=True)
def load_data(file_path,ft,sh,h):
    
    if ft == 'Excel':
        try:
            #Reading the excel file
            data = pd.read_excel(file_path,header=h,sheet_name=sh,engine='openpyxl')
        except:
            st.info("File is not recognised as an Excel file.")
            sys.exit()

    elif ft == 'CSV':
        try:
            #Reading the csv file
            data = pd.read_csv(file_path)
        except:
            st.info("File is not recognised as a csv file.")
            sys.exit()
    
    return data

# Dialog for SQL filter help
@st.experimental_dialog("Filter help", width="large")
def open_help_dialog():
    st.markdown('''
        The filtering utilizes syntax from SQLite's `WHERE` clause to filter your data for display and subsequent profiling actions.
        Begin by typing conditions involving column names. If there are multiple conditions, you may chain them with `AND` or `OR`.
        Negate conditions using `NOT`. If the column name has two or more words, enclose in `` ` ``. [SQLite WHERE Documentation](https://www.sqlitetutorial.net/sqlite-where/)

        Helpful syntax:
        - `>`, `>=`, `<`, `<=`, `=`, `<>`: Comparison operators between numeric values, dates, or strings 
            (in alphabetical manner). Operators can be column names or custom values. Enclose strings with a `'` character.
        - `column BETWEEN value1 AND value2`: Filters numeric values, dates, or strings (in alphabetical manner) 
            between `value1` and `value2` inclusive in a `column`.
        - `LIKE '%text%'`: Searches string values containg the text. Surround the text with `%` characters then with `'` characters.
        - `IN (value1, value2, value3)`: 
            Dates are in the form `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS` to match the ISO 8601 Standard.
        - `strftime('%Y', datetime)` extracts and returns the year of the date. Replacing `%Y` with `%m`, `%d`, `%w` extracts 
            the month, day, and day of week (0-Sunday to 6-Saturday) part of the date.
                
        Example: `` score BETWEEN 50 AND 100 AND name = 'Wayne' AND strftime('%Y', `start date`) = 2024 ``: Filters for records 
            with `score` between 50 and 100 inclusive, `name` of 'Wayne' and `start date` with the year 2024.
    ''')


# Creating dynamic file upload option in sidebar
uploaded_file = st.sidebar.file_uploader("*Upload file*")

# Creating option to use sample dataset
sample_checked = st.sidebar.checkbox("Load sample dataset")


if uploaded_file is not None or sample_checked:

    if sample_checked:
        file_path = 'adult.csv'
        ft = 'CSV'
        sh = None
        h = None

    elif ft == 'Excel':
        try:
            file_path = uploaded_file
            # User prompt to select sheet name in uploaded Excel
            sh = st.sidebar.selectbox("*Select sheet name:*",pd.ExcelFile(file_path).sheet_names)
            # User prompt to define row with column names if they aren't in the header row in the uploaded Excel
            h = st.sidebar.number_input("*Select row number for header names:*",0,10)
        except:
            st.info("File is not recognised as an Excel file")
            sys.exit()
    
    elif ft == 'CSV':
        try:
            file_path = uploaded_file
            sh = None
            h = None
        except:
            st.info("File is not recognised as a csv file.")
            sys.exit()

    data = load_data(file_path,ft,sh,h)

    # Select which section to show
    selected = st.sidebar.radio( "****MENU****", 
                                    ["Dataset overview",
                                    "Data summarization and profiling",
                                    "Interactive visual exploration", 
                                    "Statistical experimentation"])

    ## 1. Overview of the data
    if selected == 'Dataset overview':
        st.write( '### 1. Dataset Preview ')

        st.write("Enter a custom filter for your dataset (Use SQLite syntax)...")

        col1, col2 = st.columns([4,1])

        with col1:
            filter_text = st.text_input("filter_input", label_visibility='collapsed')

            # Logic for filter text
            if filter_text != '':
                try:
                    new_data = sqldf('SELECT * FROM data WHERE ' + filter_text)

                except:
                    st.write("There is an error in your query. Click the help button for guide.")
            else:
                new_data = data

        with col2:
            # Button for help dialog
            if st.button("Help", type='secondary'):
                open_help_dialog()

        # Check if there is data
        if len(new_data) > 0:
            try:
                # View the dataframe in streamlit
                st.markdown(f'Total rows in display: **{len(new_data)}** of **{len(data)}** ({round(len(new_data)/len(data)*100,2)}%)')
                st.dataframe(new_data, use_container_width=True)
            except:
                st.info("Error reading file. Please ensure that the input parameters are correctly defined.")
                sys.exit()
        else:
            st.write("Error: No record found!")

    ## 2. Data summarization and profiling
    if selected == 'Data summarization and profiling':

        st.write( '### 2. Data summarization and profiling')

        st.write("Enter a custom filter for your dataset (Use SQLite syntax)...")

        col1, col2 = st.columns([4,1])

        with col1:
            filter_text = st.text_input("filter_input", label_visibility='collapsed')

            # Logic for filter text
            if filter_text != '':
                try:
                    new_data = sqldf('SELECT * FROM data WHERE ' + filter_text)

                except:
                    st.write("There is an error in your query. Click the help button for guide.")
            else:
                new_data = data

        with col2:
            # Button for help dialog
            if st.button("Help", type='secondary'):
                open_help_dialog()

        # Check if there is data
        if len(new_data) > 0:
            try:
                # View the profiling
                profile = ProfileReport(new_data, orange_mode=True)
                st.markdown(f'Total rows in analysis: **{len(new_data)}** of **{len(data)}** ({round(len(new_data)/len(data)*100,2)}%)')
                st_profile_report(profile, height=999999, navbar=True)  
            except:
                st.info("Error reading file. Please ensure that the input parameters are correctly defined.")
                sys.exit()
        else:
            st.write("Error: No record found!")



else:
    st.title("Welcome to Data Express!")
    st.subheader("Import a dataset (CSV/Excel) or use a sample dataset to begin exploring.")
    st.write("")
    st.write("By Wayne Dayata | June 9, 2024")