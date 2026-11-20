# 🌍 Global Happiness Report Analysis

  📊 Explore • 🧹 Clean • 🔍 Analyze • 📈 Visualize

---

## 📌 About The Project

**Global Happiness Report Analysis** is a Python-based data analysis project that explores the happiness levels of different countries using the World Happiness Report 2019 dataset.

The project uses **Pandas, NumPy, Matplotlib, and Seaborn** to perform data exploration, data cleaning, statistical analysis, country comparisons, and interactive data visualization through a menu-driven interface.

It helps users understand how different factors, such as GDP per capita, social support, healthy life expectancy, freedom, generosity, and perceptions of corruption, relate to the happiness scores of countries.

### 🎯 Project Objectives

- Explore and understand the happiness dataset.
- Identify the happiest and least happy countries.
- Analyze the relationship between happiness scores and different factors.
- Perform statistical and numerical analysis.
- Create meaningful visualizations to understand data patterns.
- Save analyzed results and visualizations for future reference.

---

## ✨ Key Features

### 1️⃣ Dataset Management
- Load CSV datasets.
- Validate required dataset columns.
- Display dataset dimensions (rows and columns).
- Preview the first five rows.

### 2️⃣ Data Exploration
- Display the first N rows.
- Explore dataset information.
- Understand column names and data types.

### 3️⃣ Data Cleaning
- Identify missing values in each column.
- Remove rows containing missing values.
- Fill missing numerical values using the column mean.

### 4️⃣ Search, Sort & Filter
- Search countries by full or partial names.
- Sort dataset using any selected column.
- Sort data in ascending or descending order.
- Filter countries using a happiness score range.

### 5️⃣ Aggregation Functions
- Calculate Mean.
- Calculate Median.
- Categorize countries based on happiness scores:
  - 😊 Low Happiness (Score ≤ 4)
  - 🙂 Medium Happiness (4 < Score ≤ 6)
  - 😄 High Happiness (Score > 6)
- Count countries in each happiness category.

### 6️⃣ Statistical Analysis
- Generate descriptive statistics.
- Calculate the correlation matrix.
- Analyze the correlation between happiness scores and different factors.
- Identify factors with stronger positive or negative correlations.

### 7️⃣ Happiness Analysis
- 🏆 Find the Top 10 Happiest Countries.
- 📉 Find the Bottom 10 Least Happy Countries.
- 🌎 Compare selected countries.
- 🔎 Identify the factor most strongly correlated with happiness.

### 8️⃣ Data Visualization

The project provides nine different visualization options:

| No. | Visualization | Purpose |
|---|---|---|
| 1 | 📊 Bar Chart | Top 10 Happiest Countries |
| 2 | 🥧 Pie Chart | Countries by Happiness Category |
| 3 | 📈 Histogram | Distribution of Happiness Scores |
| 4 | 📦 Box Plot | Spread of Happiness Factors |
| 5 | 🔵 Scatter Plot | GDP per Capita vs Happiness Score |
| 6 | 📊 Grouped Bar Chart | Top 10 vs Bottom 10 Average Factors |
| 7 | 📉 Line Chart | Happiness Score by Overall Rank |
| 8 | 📊 Horizontal Bar Chart | Correlation of Factors with Happiness |
| 9 | 🔥 Correlation Heatmap | Relationship Between Happiness Factors |

### 9️⃣ Save Dataset & Results
- Save the complete dataset as a CSV file.
- Save the latest analysis result as a CSV file.
- Export generated charts as PNG images.
- Save visualizations in high resolution (300 DPI).

### 🔟 Input Validation & Error Handling
- Validate integer inputs within a specified range.
- Handle invalid numerical and text inputs.
- Handle missing files and invalid CSV formats.
- Handle empty datasets and missing required columns.
- Display meaningful error messages.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| 🐍 Python | Core programming language |
| 🐼 Pandas | Data manipulation and analysis |
| 🔢 NumPy | Numerical operations |
| 📊 Matplotlib | Data visualization |
| 🎨 Seaborn | Statistical data visualization |
| 📁 CSV | Dataset storage and file handling |

---

## 📂 Project Structure

```
Final Project/
│
├── 📄 .gitignore
│
├── 📊 data_set.csv
│
├── 🐍 main_ui.py
│
├── 🐍 main.py
│
└── 📘 README.md
```

### 📁 File Description

| File | Description |
|---|---|
| `.gitignore` | Specifies files and folders Git should ignore. |
| `data_set.csv` | Contains the World Happiness Report dataset used for analysis. |
| `main_ui.py` | Additional Python file included in the project structure. |
| `main.py` | Contains the core data analysis logic, class methods, menu-driven interface, and visualization functionality. |
| `README.md` | Provides project documentation, features, and execution instructions. |

---

================ GLOBAL HAPPINESS REPORT ANALYSIS ================

1.  Load Dataset
2.  Explore Data
3.  Handle Missing Data / Clean Data
4.  Search, Sort and Filter
5.  Aggregation Functions
6.  Statistical Analysis
7.  Happiness Analysis
8.  Data Visualization
9.  Save Dataset / Result
10. Save Visualization
11. Exit

Enter your choice:
```

### 📖 Basic Workflow

1. Select **Option 1** to load the CSV dataset.
2. Use **Option 2** to explore the dataset.
3. Use **Option 3** to identify and handle missing values.
4. Use **Option 4** to search, sort, and filter countries.
5. Use **Option 5 & 6** for aggregation and statistical analysis.
6. Use **Option 7** to explore happiness rankings and compare countries.
7. Use **Option 8** to generate different visualizations.
8. Use **Option 9 & 10** to export datasets, results, and charts.
9. Select **Option 11** to exit the program.

---

## 📊 Happiness Factors Analyzed

The project analyzes the following six factors:

| Factor | Description |
|---|---|
| 💰 GDP per capita | Economic contribution to happiness |
| 🤝 Social support | Social support available to individuals |
| ❤️ Healthy life expectancy | Expected healthy lifespan |
| 🕊️ Freedom to make life choices | Freedom in making personal decisions |
| 🎁 Generosity | Generosity-related contribution |
| ⚖️ Perceptions of corruption | Perception of corruption |

These factors are analyzed in relation to the overall happiness score.

---

## 📚 Concepts Applied

This project demonstrates practical implementation of:

- Python Functions and Object-Oriented Programming (OOP).
- Classes, Objects, Constructors, and Instance Attributes.
- Conditional Statements and Loops.
- Exception Handling and Input Validation.
- File Handling and CSV Operations.
- Pandas Series and DataFrames.
- Data Cleaning and Data Manipulation.
- Filtering, Sorting, and Aggregation.
- Descriptive Statistics and Correlation.
- Data Visualization and Graphical Analysis.

---

## 🎓 Learning Outcomes

Through this project, I gained practical experience in:

- Working with real-world structured datasets.
- Performing data preprocessing and cleaning.
- Applying Pandas and NumPy for data analysis.
- Understanding statistical relationships between variables.
- Creating different types of data visualizations.
- Building a menu-driven Python application using OOP.
- Handling user inputs, errors, and file operations.
- Extracting meaningful insights from data.

**🌍 Turning Happiness Data into Meaningful Insights! 📊**

