import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------- SAFE USER INPUT ----------------


def int_input(message, minimum, maximum):
    while True:
        try:
            number = int(input(message))
            if minimum <= number <= maximum:
                return number

            print(f"Please enter a number between {minimum} and {maximum}.\n")

        except ValueError:
            print("Invalid input! Please enter a whole number.\n")


def float_input(message):
    while True:
        try:
            return float(input(message))
        except ValueError:
            print("Invalid input! Please enter a valid number.\n")


def text_input(message):
    while True:
        value = input(message).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.\n")


# ---------------- HAPPINESS DATA ANALYZER ----------------


class HappinessDataAnalyzer:

    def __init__(self):
        self.data = None
        self.result = None
        self.last_figure = None

        self.factor_columns = [
            "GDP per capita",
            "Social support",
            "Healthy life expectancy",
            "Freedom to make life choices",
            "Generosity",
            "Perceptions of corruption",
        ]

    def check_data(self):
        if self.data is None:
            print("\nPlease load a CSV dataset first (Main Menu option 1).\n")
            return False
        return True

    def show_countries(self):
        countries = sorted(self.data["Country or region"].astype(str))
        print("\nAvailable countries:")
        for country in countries:
            print(f"- {country}")

    def choose_column(self, numeric_only=False):
        if numeric_only:
            columns = self.data.select_dtypes(include="number").columns.tolist()
        else:
            columns = self.data.columns.tolist()

        print("\nAvailable columns:")
        for column in columns:
            print(column)

        while True:
            column = input("\nEnter column name exactly as shown: ").strip()

            if column in columns:
                return column

            print("Column not found. Please try again.\n")

    # 1. LOAD DATASET ---------------------------------------------------------

    def load_data(self, file_path):
        try:
            if not os.path.exists(file_path):
                print(
                    "File not found! Keep data_set.csv in the same folder as main.py."
                )
                return

            data = pd.read_csv(file_path)

            if data.empty:
                print("The CSV file is empty!")
                return

            required_columns = [
                "Overall rank",
                "Country or region",
                "Score",
            ] + self.factor_columns
            missing_columns = [c for c in required_columns if c not in data.columns]

            if missing_columns:
                print("Missing columns:", missing_columns)
                return

            self.data = data
            self.result = None
            self.last_figure = None

            print("\nDataset loaded successfully!")
            print("Total rows:", self.data.shape[0])
            print("Total columns:", self.data.shape[1])
            print("\nFirst 5 rows:\n")
            print(self.data.head())

        except pd.errors.EmptyDataError:
            print("The CSV file is empty!")

        except pd.errors.ParserError:
            print("Invalid CSV file format!")

        except Exception as error:
            print(f"Unable to load dataset: {error}")

    # 2. EXPLORE DATA ---------------------------------------------------------

    def explore_data(self):
        if not self.check_data():
            return

        while True:
            print("\n---------------- EXPLORE DATA ----------------")
            print("1. Display first rows")
            print("2. Data types and dataset information")
            print("3. Back to main menu")

            choice = int_input("Enter your choice: ", 1, 3)

            if choice == 1:
                n = int_input(
                    f"Enter number of rows (1-{len(self.data)}): ", 1, len(self.data)
                )
                print(self.data.head(n))

            elif choice == 2:
                print("\nDataset information:")
                self.data.info()

            elif choice == 3:
                break

    # 3. CLEAN DATA -----------------------------------------------------------

    def clean_data(self):
        if not self.check_data():
            return

        while True:
            print("\n---------------- CLEAN DATA ----------------")
            print("1. Check missing values")
            print("2. Remove rows containing missing values")
            print("3. Fill missing numeric values with mean")
            print("4. Back to main menu")

            choice = int_input("Enter your choice: ", 1, 4)

            if choice == 1:
                print("\nMissing values in each column:\n")
                print(self.data.isna().sum())
                print("\nTotal missing values:", self.data.isna().sum().sum())

            elif choice == 2:
                before = len(self.data)
                self.data = self.data.dropna().copy()
                print(f"Removed {before - len(self.data)} rows.")

            elif choice == 3:
                for column in self.data.select_dtypes(include="number").columns:
                    self.data[column] = self.data[column].fillna(
                        self.data[column].mean()
                    )

                print("Missing numeric values filled successfully.")

            elif choice == 4:
                break

    # 4. SEARCH, SORT AND FILTER ---------------------------------------------

    def search_sort_filter(self):
        if not self.check_data():
            return

        while True:
            print("\n------------- SEARCH / SORT / FILTER -------------")
            print("1. Search for a country")
            print("2. Sort by a column")
            print("3. Filter countries by happiness score range")
            print("4. Back to main menu")

            choice = int_input("Enter your choice: ", 1, 4)

            if choice == 1:
                self.show_countries()
                country = text_input("\nEnter country name or part of name: ")
                matches = self.data["Country or region"].str.contains(
                    country, case=False, na=False
                )
                self.result = self.data[matches]
                print(self.result)

            elif choice == 2:
                column = self.choose_column()
                order = int_input("1. Ascending  2. Descending: ", 1, 2)
                self.result = self.data.sort_values(by=column, ascending=(order == 1))
                print(self.result.head(20))

            elif choice == 3:
                low, high = self.data["Score"].min(), self.data["Score"].max()
                print(f"\nHappiness scores in this dataset range from {low} to {high}.")
                minimum = float_input("Enter minimum happiness score: ")
                maximum = float_input("Enter maximum happiness score: ")

                if minimum > maximum:
                    print("Minimum score cannot be greater than maximum score.")
                    continue

                self.result = self.data[
                    self.data["Score"].between(minimum, maximum)
                ].sort_values("Score", ascending=False)

                print(self.result)

            elif choice == 4:
                break

    # 5. AGGREGATION FUNCTIONS -----------------------------------------------

    def aggregate_functions(self):
        if not self.check_data():
            return

        while True:
            print("\n---------------- AGGREGATION ----------------")
            print("1. Mean")
            print("2. Median")
            print("3. Country count by Happiness Category")
            print("4. Back to main menu")

            choice = int_input("Enter your choice: ", 1, 4)

            if choice in [1, 2]:
                column = self.choose_column(numeric_only=True)
                values = self.data[column]

                if choice == 1:
                    print("Mean:", round(values.mean(), 3))
                else:
                    print("Median:", round(values.median(), 3))

            elif choice == 3:
                category_counts = {
                    "Low (<4)": 0,
                    "Medium (4-6)": 0,
                    "High (>6)": 0,
                }

                for score in self.data["Score"]:
                    if score <= 4:
                        category_counts["Low (<4)"] += 1
                    elif score <= 6:
                        category_counts["Medium (4-6)"] += 1
                    elif score > 6:
                        category_counts["High (>6)"] += 1

                print("\nCountry count by happiness category:\n")
                for category, count in category_counts.items():
                    print(f"{category}: {count}")

            elif choice == 4:
                break

    # 6. STATISTICAL ANALYSIS -----------------------------------------------

    def statistical_analysis(self):
        if not self.check_data():
            return

        print("\n---------------- STATISTICAL ANALYSIS ----------------")

        print("\nDescriptive statistics:\n")
        print(self.data.select_dtypes(include="number").describe())

        print("\nCorrelation matrix (excluding Overall rank):\n")
        correlation_data = self.data[["Score"] + self.factor_columns].corr()
        print(correlation_data.round(3))

        print("\nCorrelation of each factor with Happiness Score:\n")
        score_correlation = correlation_data["Score"].drop("Score")
        print(score_correlation.sort_values(ascending=False).round(3))

    # 7. HAPPINESS ANALYSIS ---------------------------------------------------

    def happiness_analysis(self):
        if not self.check_data():
            return

        while True:
            print("\n---------------- HAPPINESS ANALYSIS ----------------")
            print("1. Top 10 happiest countries")
            print("2. Bottom 10 least happy countries")
            print("3. Compare selected countries")
            print("4. Find factor most strongly correlated with happiness")
            print("5. Back to main menu")

            choice = int_input("Enter your choice: ", 1, 5)

            if choice == 1:
                self.result = self.data.nlargest(10, "Score")[
                    ["Overall rank", "Country or region", "Score"]
                ]
                print("\nTop 10 happiest countries:\n")
                print(self.result.to_string(index=False))

            elif choice == 2:
                self.result = self.data.nsmallest(10, "Score")[
                    ["Overall rank", "Country or region", "Score"]
                ]
                print("\nBottom 10 least happy countries:\n")
                print(self.result.to_string(index=False))

            elif choice == 3:
                self.show_countries()
                countries = text_input("\nEnter country names separated by commas: ")
                names = [c.strip().lower() for c in countries.split(",") if c.strip()]

                self.result = self.data[
                    self.data["Country or region"].str.lower().isin(names)
                ][["Country or region", "Score"] + self.factor_columns]

                if self.result.empty:
                    print("No matching countries found.")
                else:
                    print("\nCountry comparison:\n")
                    print(self.result.to_string(index=False))

            elif choice == 4:
                correlation = (
                    self.data[["Score"] + self.factor_columns]
                    .corr()["Score"]
                    .drop("Score")
                )

                strongest_factor = correlation.abs().idxmax()

                print("\nFactor with strongest correlation to Happiness Score:")
                print("Factor:", strongest_factor)
                print("Correlation:", round(correlation[strongest_factor], 3))

            elif choice == 5:
                break

    # 8. DATA VISUALIZATION ---------------------------------------------------

    def visualize_data(self):
        if not self.check_data():
            return

        while True:
            print("\n---------------- DATA VISUALIZATION ----------------")
            print("1. Top 10 happiest countries (bar chart)")
            print("2. Countries by Happiness Category (pie chart)")
            print("3. Happiness Score distribution (histogram)")
            print("4. Happiness factors spread (box plot)")
            print("5. GDP per capita vs Happiness Score (scatter plot)")
            print("6. Top 10 vs bottom 10 average factors (grouped bar chart)")
            print("7. Happiness Score by overall rank (line chart)")
            print("8. Correlation of each factor with Score (horizontal bar chart)")
            print("9. Correlation heatmap")
            print("10. Back to main menu")

            choice = int_input("Enter your choice: ", 1, 10)

            if choice == 10:
                break

            figure = None

            try:
                figure, ax = plt.subplots(figsize=(10, 6))
                correlation_data = self.data[["Score"] + self.factor_columns].corr()

                if choice == 1:
                    chart_data = self.data.nlargest(10, "Score").sort_values("Score")
                    sns.barplot(
                        data=chart_data, x="Score", y="Country or region", ax=ax
                    )
                    ax.set_title("Top 10 Happiest Countries - 2019")
                elif choice == 2:
                    category_counts = {
                        "Low (<4)": 0,
                        "Medium (4-6)": 0,
                        "High (>6)": 0,
                    }

                    for score in self.data["Score"]:
                        if score <= 4:
                            category_counts["Low (<4)"] += 1
                        elif score <= 6:
                            category_counts["Medium (4-6)"] += 1
                        elif score > 6:
                            category_counts["High (>6)"] += 1

                    category_labels = []
                    category_values = []
                    for name, count in category_counts.items():
                        if count > 0:
                            category_labels.append(name)
                            category_values.append(count)

                    ax.pie(
                        category_values,
                        labels=category_labels,
                        autopct="%1.1f%%",
                        startangle=90,
                    )
                    ax.set_title("Countries by Happiness Category - 2019")
                elif choice == 3:
                    sns.histplot(data=self.data, x="Score", bins=15, kde=True, ax=ax)
                    ax.set_title("Distribution of Happiness Scores - 2019")
                elif choice == 4:
                    sns.boxplot(data=self.data[self.factor_columns], orient="h", ax=ax)
                    ax.set_title("Spread of Happiness Factors - 2019")
                elif choice == 5:
                    sns.regplot(data=self.data, x="GDP per capita", y="Score", ax=ax)
                    ax.set_title("GDP per capita vs Happiness Score")
                elif choice == 6:
                    top = self.data.nlargest(10, "Score")[self.factor_columns].mean()
                    bottom = self.data.nsmallest(10, "Score")[
                        self.factor_columns
                    ].mean()
                    pd.DataFrame({"Top 10": top, "Bottom 10": bottom}).plot(
                        kind="bar", ax=ax
                    )
                    ax.set_title("Average Factors: Top 10 vs Bottom 10 Countries")
                    plt.xticks(rotation=30, ha="right")
                elif choice == 7:
                    ranked = self.data.sort_values("Overall rank")
                    ax.plot(
                        ranked["Overall rank"],
                        ranked["Score"],
                        marker="o",
                        markersize=3,
                    )
                    ax.set_title("Happiness Score by Overall Rank")
                    ax.set_xlabel("Overall rank")
                    ax.set_ylabel("Happiness Score")
                elif choice == 8:
                    correlation = correlation_data["Score"].drop("Score").sort_values()
                    ax.barh(correlation.index, correlation.values)
                    ax.set_title("Correlation of Each Factor with Happiness Score")
                    ax.set_xlabel("Correlation coefficient")
                elif choice == 9:
                    sns.heatmap(
                        correlation_data, annot=True, cmap="coolwarm", fmt=".2f", ax=ax
                    )
                    ax.set_title("Correlation Heatmap - World Happiness 2019")

                plt.tight_layout()
                self.last_figure = figure
                plt.show()

            except Exception as error:
                if figure is not None:
                    plt.close(figure)
                print(f"Unable to create chart: {error}")

    # 9. SAVE DATASET / RESULT ----------------------------------------------

    def save_result(self):
        if not self.check_data():
            return

        print("\n---------------- SAVE DATA ----------------")
        print("1. Save current dataset as CSV")
        print("2. Save last result as CSV")
        print("3. Back to main menu")

        choice = int_input("Enter your choice: ", 1, 3)

        if choice == 3:
            return

        filename = text_input("Enter output file name (without extension): ") + ".csv"

        try:
            if choice == 1:
                self.data.to_csv(filename, index=False)

            else:
                if self.result is None:
                    print("No result available. Perform an analysis first.")
                    return

                self.result.to_csv(filename, index=True)

            print(f"File saved successfully: {os.path.abspath(filename)}")

        except Exception as error:
            print(f"Unable to save file: {error}")

    # 10. SAVE VISUALIZATION --------------------------------------------------

    def save_visualization(self):
        if not self.check_data():
            return

        if self.last_figure is None:
            print("\nPlease create a chart from Data Visualization first.")
            return

        filename = text_input("Enter image file name (without extension): ") + ".png"

        try:
            self.last_figure.savefig(filename, bbox_inches="tight", dpi=300)
            print(f"Visualization saved successfully: {os.path.abspath(filename)}")

        except Exception as error:
            print(f"Unable to save visualization: {error}")


# ---------------- MAIN PROGRAM ----------------------------------------------

if __name__ == "__main__":

    analysis = HappinessDataAnalyzer()

    while True:
        print("\n================ GLOBAL HAPPINESS REPORT ANALYSIS ================")
        print("1. Load Dataset")
        print("2. Explore Data")
        print("3. Handle Missing Data / Clean Data")
        print("4. Search, Sort and Filter")
        print("5. Aggregation Functions")
        print("6. Statistical Analysis")
        print("7. Happiness Analysis")
        print("8. Data Visualization")
        print("9. Save Dataset / Result")
        print("10. Save Visualization")
        print("11. Exit")

        choice = int_input("Enter your choice: ", 1, 11)

        if choice == 1:
            file_path = input(
                "Enter CSV file name (press Enter for data_set.csv): "
            ).strip()

            if not file_path:
                file_path = "data_set.csv"

            analysis.load_data(file_path)
        elif choice == 2:
            analysis.explore_data()
        elif choice == 3:
            analysis.clean_data()
        elif choice == 4:
            analysis.search_sort_filter()
        elif choice == 5:
            analysis.aggregate_functions()
        elif choice == 6:
            analysis.statistical_analysis()
        elif choice == 7:
            analysis.happiness_analysis()
        elif choice == 8:
            analysis.visualize_data()
        elif choice == 9:
            analysis.save_result()
        elif choice == 10:
            analysis.save_visualization()
        elif choice == 11:
            print("\nExiting the program. Goodbye!")
            break
