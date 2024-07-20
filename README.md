# Data Express

![image](https://github.com/20100215/Data_Express/assets/84717650/85bcc096-331b-4ab5-a3e3-b4385c9fefa6)

A web-based interactive data analysis application supporting .csv and .xlsx files with the following core features: 

1. Dataset profiling with filtering options prior to displays of summary statistics, distributions per column, and relationships between columns 
2. Tableau-like visual exploration interface
3. Statistical experimentation and hypothesis testing
4. Machine learning

## Technologies:

- Python, Pandas, PyGWalker, SciPy, statsmodels, PyCaret, Streamlit

## Setup:

1. Clone the project repo by typing the following in Git Bash or Powershell:

```
git clone https://github.com/20100215/Data_Express.git
```

2. Install the requirements by typing the following in Command Prompt or Powershell:

```
pip install -r requirements.txt
```

3. Start the application

```
$ streamlit run app.py
```

4. If you want to run the app with the automated machine learning feature:

```
$ streamlit run app_with_ML.py
```

Note: The `streamlit-ydata-profiling` only supports up to Python 3.11 as of June 9, 2024
