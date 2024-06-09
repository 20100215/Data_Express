import sys
import streamlit as st
import pandas as pd
from pandasql import sqldf
import numpy as np
from streamlit_ydata_profiling import st_profile_report
from ydata_profiling import ProfileReport
import openpyxl
from pygwalker.api.streamlit import StreamlitRenderer
from scipy import stats
import scikit_posthocs as sp
import statsmodels.api as sm
from statsmodels.formula.api import ols
import math

# Setting up web app page
st.set_page_config(page_title='Exploratory Data Analysis App', page_icon=None, layout="wide")

# Page title and headline
st.sidebar.title('📊🚀 Data Express')
st.sidebar.subheader('Unleash your data\'s potential in minutes!')

# Caching function to load data
@st.cache_data(experimental_allow_widgets=True)
def load_data(file_path,sh,h):
    
    if file_path and file_path.name.endswith('.xlsx'):
        try:
            #Reading the excel file
            data = pd.read_excel(file_path,header=h,sheet_name=sh,engine='openpyxl')
        except:
            st.info("File is not recognised as an Excel file.")
            sys.exit()

    elif file_path and file_path.name.endswith('.csv'):
        try:
            #Reading the csv file
            data = pd.read_csv(file_path)
        except:
            st.info("File is not recognised as a csv file.")
            sys.exit()
    else:
        data = pd.read_csv('students.csv')
    
    return data

# Dialog for SQL filter help
@st.experimental_dialog("Filter help", width="large")
def open_help_dialog():
    st.markdown('''
        The filtering utilizes syntax from SQLite's `WHERE` clause to filter your data for display and subsequent profiling actions.
        Begin by typing conditions involving column names. If there are multiple conditions, you may chain them with `AND` or `OR`.
        Negate conditions using `NOT`. [SQLite WHERE Documentation](https://www.sqlitetutorial.net/sqlite-where/)

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
            with `score` from 50 to 100, `name` of 'Wayne' and `start date` with the year 2024.
    ''')


# Creating dynamic file upload option in sidebar
uploaded_file = st.sidebar.file_uploader("*Upload file*", type=['csv', 'xlsx'])

# Creating option to use sample dataset
sample_checked = st.sidebar.checkbox("Load sample dataset")


if uploaded_file is not None or sample_checked:

    if sample_checked:
        uploaded_file = None
        file_path = None
        sh = None
        h = None

    elif uploaded_file.name.endswith('.xlsx'):
        try:
            file_path = uploaded_file
            sample_checked = False
            # User prompt to select sheet name in uploaded Excel
            sh = st.sidebar.selectbox("*Select sheet name:*",pd.ExcelFile(file_path).sheet_names)
            # User prompt to define row with column names if they aren't in the header row in the uploaded Excel
            h = st.sidebar.number_input("*Select row number for header names:*",0,10)
        except:
            st.info("File is not recognised as an Excel file")
            sys.exit()
    
    elif uploaded_file.name.endswith('.csv'):
        try:
            file_path = uploaded_file
            sample_checked = False
            sh = None
            h = None
        except:
            st.info("File is not recognised as a csv file.")
            sys.exit()

    data = load_data(file_path,sh,h)

    # Select which section to show
    selected = st.sidebar.radio( "****MENU****", 
                                    ["Dataset preview",
                                    "Data summarization and profiling",
                                    "Interactive visual exploration", 
                                    "Statistical experimentation"])

    ## ===============================================
    ## 1. Preview of the data
    ## ===============================================
    if selected == 'Dataset preview':
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
                    new_data = data
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
                st.write('Tip: Drag the edges of the columns to increase its size. Click on a column to sort the table by its values.')
                if sample_checked:
                    st.markdown('See details about the dataset in [this paper](https://www.mdpi.com/2306-5729/4/3/124).')
                st.dataframe(new_data, use_container_width=True)
            except:
                st.info("Error reading file. Please ensure that the input parameters are correctly defined.")
                sys.exit()
        else:
            st.write("Error: No record found!")

    ## ===============================================
    ## 2. Data summarization and profiling
    ## ===============================================
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
                    new_data = data
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
                profile = ProfileReport(new_data, orange_mode=True, explorative=True, sample=None)
                st.markdown(f'Total rows in analysis: **{len(new_data)}** of **{len(data)}** ({round(len(new_data)/len(data)*100,2)}%)')
                st_profile_report(profile, height=800, navbar=True)  
            except:
                st.info("Error reading file. Please ensure that the input parameters are correctly defined.")
                sys.exit()
        else:
            st.write("Error: No record found!")

    ## ===============================================
    ## 3. PyGWalker Visualization
    ## ===============================================
    if selected == 'Interactive visual exploration':

        st.write( '### 3. Interactive visual exploration')
        st.markdown('Use the interactive interface below to experiment with different visualization. Refer to the [documentation](https://docs.kanaries.net/graphic-walker/data-viz/create-data-viz) for guide.')

        pyg_app = StreamlitRenderer(data, appearance="light")
        pyg_app.explorer()

    ## ===============================================
    ## 4. Statistical experimentation 
    ## ===============================================
    if selected == 'Statistical experimentation':

        st.write( '### 4. Statistical experimentation')

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
                    new_data = data
            else:
                new_data = data
        with col2:
            # Button for help dialog
            if st.button("Help", type='secondary'):
                open_help_dialog()

        # Check if there is data
        if len(new_data) > 0:
            st.markdown(f'Total rows in analysis: **{len(new_data)}** of **{len(data)}** ({round(len(new_data)/len(data)*100,2)}%)')
        else:
            st.write("Error: No record found!")

        # Prepare functions
        def check_normality(data, colname):
            test_stat_normality, p_value_normality=stats.normaltest(data)
            if p_value_normality <0.05:
                to_print = f'- p-value for {colname}: {p_value_normality:.10f} >> Reject null hypothesis (The data is not normally distributed)'
            else:
                to_print = f'- p-value for {colname}: {p_value_normality:.10f} >> Fail to reject null hypothesis (The data is normally distributed)'

            return p_value_normality, to_print

        def check_variance_homogeneity(groups):
            test_stat_var, p_value_var= stats.levene(*groups)
            if p_value_var <0.05:
                to_print = f'- p-value: {p_value_var:.10f} >> Reject null hypothesis (The variances of the samples are different)'
            else:
                to_print = f'- p-value: {p_value_var:.10f} >> Fail to reject null hypothesis (The variances of the samples are same)'

            return p_value_var, to_print

        # Get categorical and numeric variables
        categorical_cols =  [col for col in new_data.columns if new_data[col].nunique() <= 8]
        numerical_cols =    [col for col in new_data.select_dtypes(include=['float','int'])]

        if len(numerical_cols) >= 2 or (len(categorical_cols) >= 1 and len(numerical_cols) >= 1):

            st.write('Experiment with various hypothesis testing metrics to verify statistical \
                     significance of the differences between various groups of data. \
                     Here, the level of significance is 0.05.')
            
            st.write('Tip: If a certain categorical column is not shown, then there are too many \
                     distinct values. Use the filter to include only up to 8 desired values in a categorical column \
                     (i.e. car brands, year values). You may also utilize the filter to control your other variables.')
            
            # Initialize experiment options
            experiments = []
            if len(numerical_cols) >= 2: 
                experiments.append("Paired samples test (requires 2 similar internal/ratio variables from all rows)")
            if len(categorical_cols) >= 1 and len(numerical_cols) >= 1:
                experiments.append("Independent samples test (requires 1 categorical variable and 1 interval/ratio variable)")
            if len(categorical_cols) >= 2 and len(numerical_cols) >= 1:
                experiments.append("Two-way ANOVA test (requires 2 categorical variables and 1 interval/ratio variable)")

            experiment = st.radio("****Select experiment type to perform:****", experiments)

            # Show columns to select
            if experiment == 'Paired samples test (requires 2 similar internal/ratio variables from all rows)':
                col_1, col_2, col_3 = st.columns([1,1,1])

                with col_1:
                    var_1 = st.selectbox( "****Select interval/ratio column 1:****", 
                                        numerical_cols, key=1)
                with col_2:
                    var_2 = st.selectbox( "****Select interval/ratio column 2:****", 
                                        numerical_cols, key=2)
                with col_3:
                    count = st.number_input( "****Input number of samples:****",
                                            min_value=10, step=1, 
                                            max_value=len(new_data), value = min(100,len(new_data)))
                    
                if st.button('Analyze', type='primary'):
                    # Check if repeated columns
                    if var_1 == var_2:
                        st.write('Error: The two interval/ratio columns must be different.')
                    else:
                        # Drop rows with NA values
                        new_data.dropna(subset=[var_1,var_2],axis=0,inplace=True)
                        # Sample
                        new_data = new_data.sample(n=count)

                        # Assumption checks
                        is_parametric = True
                        st.markdown('''
                            ##### Assumption check 1: Normality of distribution (D'Agostino and Pearson's test)
                            $H_0$: The data is normally distributed.
                            $H_1$: The data is not normally distributed.
                        ''')

                        for var in [var_1, var_2]:
                            pval, text = check_normality(new_data[var].to_numpy(), var)
                            is_parametric = is_parametric and pval > 0.05
                            st.write(text)

                        st.write('')
                        st.markdown('''
                            ##### Assumption check 2: Homogeneity of variance (Levene's test)
                            $H_0$: The variances of the samples are the same.
                            $H_1$: The variances of the samples are different.
                        ''')

                        pval, text = check_variance_homogeneity([new_data[var_1].to_numpy(),new_data[var_2].to_numpy()])
                        is_parametric = is_parametric and pval > 0.05
                        st.write(text)
                        st.write('')

                        # Test selection
                        if is_parametric:
                            # Main test: Paired t-test
                            st.markdown('''
                                ##### Assumptions are satisfied, performing Paired t-test
                                $H_0$: The true mean difference is zero.
                                $H_1$: The true mean difference is greater or less than zero.
                            ''')
                            test,pvalue = stats.ttest_rel(new_data[var_1],new_data[var_2]) ##alternative default two sided
                            if pvalue < 0.05:
                                st.markdown(f'- p-value: {pvalue:.10f} Reject null hypothesis \
                                             ##### Conclusion: There is a significant difference between the two groups.')
                            else:
                                st.markdown(f'- p-value: {pvalue:.10f} Fail to reject null hypothesis \
                                             ##### Conclusion: There is a significant difference between the two groups.')

                        else:
                            # Main test: Wilcoxon Signed Rank test
                            st.markdown('''
                                ##### Assumptions are not satisfied, performing Wilcoxon Signed Rank test
                                $H_0$: The true mean difference is zero.
                                $H_1$: The true mean difference is greater or less than zero.
                            ''')
                            test,pvalue = stats.wilcoxon(new_data[var_1],new_data[var_2]) ##alternative default two sided
                            if pvalue < 0.05:
                                st.markdown(f'- p-value: {pvalue:.10f} >> Reject null hypothesis')
                                st.markdown('##### Conclusion: There is a significant difference between the two groups.')
                            else:
                                st.markdown(f'- p-value: {pvalue:.10f} >> Fail to reject null hypothesis')
                                st.markdown('##### Conclusion: There is no significant difference between the two groups.')

                        st.write('')
                    
            elif experiment == 'Independent samples test (requires 1 categorical variable and 1 interval/ratio variable)':
                col_1, col_2, col_3 = st.columns([1,1,1])
                with col_1:
                    var_1 = st.selectbox( "****Select categorical column:****", 
                                        categorical_cols, key=3)
                with col_2:
                    var_2 = st.selectbox( "****Select interval/ratio column:****", 
                                        numerical_cols, key=4)
                with col_3:
                    count = st.number_input( "****Input # samples per group:****",
                                            min_value=10, step=1, 
                                            max_value=len(new_data), value = min(100,len(new_data)))
                
                if st.button('Analyze', type='primary'):
                    # Drop rows with NA values
                    new_data.dropna(subset=[var_1,var_2],axis=0,inplace=True)
                    # Split new_data per unique categorical value
                    dfs = dict(tuple(new_data.groupby(var_1)))
                    st.write(f'Number of groups: {len(list(dfs.keys()))}')

                    # Sample in each subgroup
                    for column_val in list(dfs.keys()):
                        dfs[column_val] = dfs[column_val].sample(n=min(count,len(dfs[column_val])))
                        st.markdown(f"- {column_val} - {len(dfs[column_val])} samples")

                    # Assumption checks
                    is_parametric = True
                    st.markdown('''
                        ##### Assumption check 1: Normality of distribution (D'Agostino and Pearson's test)
                        $H_0$: The data is normally distributed.
                        $H_1$: The data is not normally distributed.
                    ''')

                    for column_val in list(dfs.keys()):
                        pval, text = check_normality(dfs[column_val][var_2].to_numpy(), var_2)
                        is_parametric = is_parametric and pval > 0.05
                        st.write(text)

                    st.write('')
                    st.markdown('''
                        ##### Assumption check 2: Homogeneity of variance (Levene's test)
                        $H_0$: The variances of the samples are the same.
                        $H_1$: The variances of the samples are different.
                    ''')

                    pval, text = check_variance_homogeneity([dfs[column_val][var_2].to_numpy() for column_val in list(dfs.keys())])
                    is_parametric = is_parametric and pval > 0.05
                    st.write(text)
                    st.write('')

                    # Test selection
                    if len(list(dfs.keys())) == 2: # Independent T test or nonparametric equivalent
                        if is_parametric:
                            st.markdown('''
                                ##### Assumptions are satisfied, performing Independent t-test
                                $H_0$: The true mean difference is zero.
                                $H_1$: The true mean difference is greater or less than zero.
                            ''')
                            value_groups = [dfs[column_val][var_2].to_numpy() for column_val in list(dfs.keys())]
                            test,pvalue = stats.ttest_ind(*value_groups)                            
                            if pvalue < 0.05:
                                st.markdown(f'- p-value: {pvalue:.10f} Reject null hypothesis')
                                st.markdown('##### Conclusion: There is a significant difference between the two groups.')
                            else:
                                st.markdown(f'- p-value: {pvalue:.10f} Fail to reject null hypothesis')
                                st.markdown('##### Conclusion: There is no significant difference between the two groups.')

                        else:
                            st.markdown('''
                                ##### Assumptions are not satisfied, performing Mann Whitney U test
                                $H_0$: The true mean difference is zero.
                                $H_1$: The true mean difference is greater or less than zero.
                            ''')
                            value_groups = [dfs[column_val][var_2].to_numpy() for column_val in list(dfs.keys())]
                            test,pvalue = stats.mannwhitneyu(*value_groups) 
                            if pvalue < 0.05:
                                st.markdown(f'- p-value: {pvalue:.10f} >> Reject null hypothesis')
                                st.markdown('##### Conclusion: There is a significant difference between the two groups.')
                            else:
                                st.markdown(f'- p-value: {pvalue:.10f} >> Fail to reject null hypothesis')
                                st.markdown('##### Conclusion: There is no significant difference between the two groups.')

                    else: # ANOVA or nonparametric equivalent
                        if is_parametric:

                            # Main test: ANOVA
                            st.markdown('''
                                ##### Assumptions are satisfied, performing one-way ANOVA:
                                $H_0$: The means of the groups are the same.
                                $H_1$: At least one of the groups' means is different.
                            ''')
                            value_groups = [dfs[column_val][var_2].to_numpy() for column_val in list(dfs.keys())]
                            test,pvalue = stats.f_oneway(*value_groups) 
                            if pvalue < 0.05:
                                st.markdown(f'- p-value: {pvalue:.10f} Reject null hypothesis')
                                st.markdown('##### Conclusion: At least one of the groups\' means are different.')
                            else:
                                st.markdown(f'- p-value: {pvalue:.10f} Fail to reject null hypothesis')
                                st.markdown('##### Conclusion: There is no significant difference between the groups.')

                            # Post-hoc tests
                            st.write('')
                            st.markdown('##### Performing pairwise independent T-test for pairwise comparison between groups ')
                            posthoc_df = sp.posthoc_ttest(value_groups, equal_var=True, p_adjust = 'bonferroni')
                            group_names= list(dfs.keys())
                            posthoc_df.columns= group_names
                            posthoc_df.index= group_names
                            
                            st.write('The generated matrix shows the p-value results for each pairwise comparisons. \
                                     p-values below 0.05 indicate the means for each pair of groups are significantly different.')
                            st.dataframe(posthoc_df)
                        
                        else:
                            # Main test: Keuskal-Wallis test
                            st.markdown('''
                                ##### Assumptions are not satisfied, performing Kruskal-Wallis test
                                $H_0$: The means of the groups are the same.
                                $H_1$: At least one of the sample' means is different.
                            ''')
                            value_groups = [dfs[column_val][var_2].to_numpy() for column_val in list(dfs.keys())]
                            test,pvalue = stats.kruskal(*value_groups) 
                            if pvalue < 0.05:
                                st.markdown(f'- p-value: {pvalue:.10f} Reject null hypothesis')
                                st.markdown('##### Conclusion: At least one of the groups\' means are different.')
                            else:
                                st.markdown(f'- p-value: {pvalue:.10f} Fail to reject null hypothesis')
                                st.markdown('##### Conclusion: There is no significant difference between the groups.')                            # Post-hoc tests
                            
                            # Post-hoc tests
                            st.write('')
                            st.markdown('##### Performing Mann Whitney U test for pairwise comparison between groups ')
                            posthoc_df = sp.posthoc_mannwhitney(value_groups, p_adjust = 'bonferroni')
                            group_names= list(dfs.keys())
                            posthoc_df.columns= group_names
                            posthoc_df.index= group_names
          
                            st.write('The generated matrix shows the p-value results for each pairwise comparisons. \
                                     p-values below 0.05 indicate the means for each pair of groups are significantly different.')
                            st.dataframe(posthoc_df)

                    st.write('')


            
            elif experiment == 'Two-way ANOVA test (requires 2 categorical variables and 1 interval/ratio variable)':
                col_1, col_2, col_3 = st.columns([1,1,1])
                with col_1:
                    var_1 = st.selectbox( "****Select categorical column 1:****", 
                                        categorical_cols, key=5)
                with col_2:
                    var_2 = st.selectbox( "****Select categorical column 2:****", 
                                        categorical_cols, key=6)
                with col_3:
                    var_3 = st.selectbox( "****Select interval/ratio column:****", 
                                        numerical_cols, key=7)
                    
                
            
                if st.button('Analyze', type='primary'):
                    # Check if repeated columns
                    if var_1 == var_2:
                        st.write('Error: The two categorical columns must be different.')
                    else:
                        # Drop rows with NA values
                        new_data.dropna(subset=[var_1,var_2,var_3],axis=0,inplace=True)
                        
                        # Count values
                        st.markdown('##### Count of values per combination of groups:')
                        groups_count = new_data[[var_1,var_2]].value_counts().reset_index(name='count')
                        st.dataframe(groups_count)
                        
                        # Perform two way ANOVA
                        st.markdown('##### Performing two-way ANOVA')
                        model = ols(f'{var_3} ~ C({var_1}) + C({var_2}) + C({var_1}):C({var_2})', data=new_data).fit()
                        anova_df = sm.stats.anova_lm(model, typ=2)
                        st.dataframe(anova_df)

                        # Interpretations
                        if math.isnan(anova_df.iloc[0,3]):
                            st.write(f'The p-value for {var_1} nor its significance can be determined.')
                        if anova_df.iloc[0,3] < 0.05:
                            st.write(f'The p-value for {var_1} is {anova_df.iloc[0,3]:.10f} (< 0.05) >> {var_1} has a statistically significant effect on {var_3}.')
                        else:
                            st.write(f'The p-value for {var_1} is {anova_df.iloc[0,3]:.10f} (>= 0.05) >> {var_1} has no statistically significant effect on {var_3}.')
                        
                        if math.isnan(anova_df.iloc[1,3]):
                            st.write(f'The p-value for {var_2} nor its significance can be determined.')
                        elif anova_df.iloc[1,3] < 0.05:
                            st.write(f'The p-value for {var_2} is {anova_df.iloc[1,3]:.10f} (< 0.05) >> {var_2} has a statistically significant effect on {var_3}.')
                        else:
                            st.write(f'The p-value for {var_2} is {anova_df.iloc[1,3]:.10f} (>= 0.05) >> {var_2} has no statistically significant effect on {var_3}.')

                        if anova_df.iloc[2,3] < 0.05:
                            st.write(f'The p-value for the interaction effect is {anova_df.iloc[2,3]:.10f} (< 0.05) >> {var_2} has a significant interaction effect between {var_1} and {var_2} on {var_3}.')
                        else:
                            st.write(f'The p-value for the interaction effect is {anova_df.iloc[2,3]:.10f} (>= 0.05) >> {var_2} has no significant interaction effect between {var_1} and {var_2} on {var_3}.')


                         # Post-hoc tests
                        st.write('')
                        st.markdown('##### Performing Mann Whitney U test for pairwise comparison between groups ')
                        
                        # Create df groups per combination of variables
                        value_groups = []
                        group_names = []
                        for i, row in groups_count.iterrows():
                            # Fetch names
                            group_names.append(row[0] + ', ' + row[1])
                            # Fetch filtered values on target column
                            value_groups.append(new_data[(new_data[var_1] == row[0]) & (new_data[var_2] == row[1])][var_3].to_numpy())

                        posthoc_df = sp.posthoc_mannwhitney(value_groups, p_adjust = 'bonferroni')
                        posthoc_df.columns= group_names
                        posthoc_df.index= group_names
        
                        st.write(f'The generated matrix shows the p-value results for each pairwise comparisons ({var_1} and {var_2}) against the target variable ({var_3}).')
                        st.write('p-values below 0.05 indicate the means for each pair of groups are significantly different.')
                        st.dataframe(posthoc_df)
            

        else:
            st.write("Error: Cannot perform statical experimentation in this dataset as it either does not contain \
                     any categorical data or does not contain any numeric data. Both kinds of data should be present \
                     for this feature.")

        st.markdown('Read the guide for hypothesis testing [here](https://towardsdatascience.com/hypothesis-testing-with-python-step-by-step-hands-on-tutorial-with-practical-examples-e805975ea96e).')

else:
    st.title("Welcome to Data Express!")
    st.subheader("Import a dataset (CSV/Excel) or use a sample dataset to begin exploring.")
    st.write("")
    st.markdown("By Wayne Dayata [(Github)](https://github.com/20100215)| June 9, 2024 ")