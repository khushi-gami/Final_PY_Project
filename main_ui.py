import io
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)
from matplotlib.figure import Figure

FACTOR_COLUMNS = [
    "GDP per capita",
    "Social support",
    "Healthy life expectancy",
    "Freedom to make life choices",
    "Generosity",
    "Perceptions of corruption",
]

REQUIRED_COLUMNS = ["Overall rank", "Country or region", "Score"] + FACTOR_COLUMNS

CHART_OPTIONS = [
    "Top 10 happiest countries (bar chart)",
    "Countries by Happiness Category (pie chart)",
    "Happiness Score distribution (histogram)",
    "Happiness factors spread (box plot)",
    "GDP per capita vs Happiness Score (scatter plot)",
    "Top 10 vs bottom 10 average factors (grouped bar chart)",
    "Happiness Score by overall rank (line chart)",
    "Correlation of each factor with Score (horizontal bar chart)",
    "Correlation heatmap",
]

CATEGORY_NAMES = ["Low (<4)", "Medium (4-6)", "High (>6)"]


def happiness_category_counts(scores):
    """Count countries in Low / Medium / High happiness categories."""
    counts = {name: 0 for name in CATEGORY_NAMES}
    for score in scores.dropna():
        if score < 4:
            counts["Low (<4)"] += 1
        elif score <= 6:
            counts["Medium (4-6)"] += 1
        else:
            counts["High (>6)"] += 1
    return counts


# ---------------- OUTPUT PANE (table or text) ----------------


class OutputPane(ttk.Frame):
    """A area that can show either a DataFrame as a table, or plain text."""

    def __init__(self, master):
        super().__init__(master)

        # Table view
        self.tree_frame = ttk.Frame(self)
        self.tree = ttk.Treeview(self.tree_frame, show="headings")
        tree_vsb = ttk.Scrollbar(
            self.tree_frame, orient="vertical", command=self.tree.yview
        )
        tree_hsb = ttk.Scrollbar(
            self.tree_frame, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(yscrollcommand=tree_vsb.set, xscrollcommand=tree_hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_vsb.grid(row=0, column=1, sticky="ns")
        tree_hsb.grid(row=1, column=0, sticky="ew")
        self.tree_frame.rowconfigure(0, weight=1)
        self.tree_frame.columnconfigure(0, weight=1)

        # Text view
        self.text_frame = ttk.Frame(self)
        self.text = tk.Text(self.text_frame, font=("Consolas", 10), wrap="none")
        text_vsb = ttk.Scrollbar(
            self.text_frame, orient="vertical", command=self.text.yview
        )
        text_hsb = ttk.Scrollbar(
            self.text_frame, orient="horizontal", command=self.text.xview
        )
        self.text.configure(yscrollcommand=text_vsb.set, xscrollcommand=text_hsb.set)
        self.text.grid(row=0, column=0, sticky="nsew")
        text_vsb.grid(row=0, column=1, sticky="ns")
        text_hsb.grid(row=1, column=0, sticky="ew")
        self.text_frame.rowconfigure(0, weight=1)
        self.text_frame.columnconfigure(0, weight=1)

        self.show_text("Output will appear here.")

    def show_df(self, df):
        self.text_frame.pack_forget()
        self.tree_frame.pack(fill="both", expand=True)

        self.tree.delete(*self.tree.get_children())
        columns = [str(c) for c in df.columns]
        self.tree["columns"] = columns

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=max(90, len(column) * 9), anchor="center")

        for _, row in df.head(2000).iterrows():
            values = [round(v, 3) if isinstance(v, float) else v for v in row]
            self.tree.insert("", "end", values=values)

    def show_text(self, content):
        self.tree_frame.pack_forget()
        self.text_frame.pack(fill="both", expand=True)

        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.configure(state="disabled")


# ---------------- MAIN APPLICATION ----------------


class HappinessApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Global Happiness Report Analysis")
        self.geometry("1180x740")
        self.minsize(980, 620)

        self.data = None
        self.result = None
        self.last_figure = None

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 15, "bold"))
        style.configure("TButton", padding=5)

        self.build_header()
        self.build_tabs()
        self.build_statusbar()

    # ---------- layout ----------

    def build_header(self):
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill="x")

        ttk.Label(
            header, text="Global Happiness Report Analysis", style="Title.TLabel"
        ).pack(side="left")

        ttk.Button(header, text="Load Dataset", command=self.load_data).pack(
            side="right"
        )
        ttk.Button(header, text="Browse...", command=self.browse_file).pack(
            side="right", padx=6
        )
        self.file_var = tk.StringVar(value="data_set.csv")
        ttk.Entry(header, textvariable=self.file_var, width=38).pack(
            side="right", padx=6
        )
        ttk.Label(header, text="CSV file:").pack(side="right")

    def build_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        self.build_explore_tab()
        self.build_clean_tab()
        self.build_search_tab()
        self.build_aggregation_tab()
        self.build_statistics_tab()
        self.build_happiness_tab()
        self.build_visualization_tab()
        self.build_save_tab()

    def build_statusbar(self):
        self.status_var = tk.StringVar(
            value="No dataset loaded. Choose a CSV file and click 'Load Dataset'."
        )
        ttk.Label(
            self, textvariable=self.status_var, relief="sunken", anchor="w", padding=4
        ).pack(fill="x", side="bottom")

    def new_tab(self, title):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text=title)
        return tab

    # ---------- helpers ----------

    def need_data(self):
        if self.data is None:
            messagebox.showwarning(
                "No dataset", "Please load a CSV dataset first (top right)."
            )
            return False
        return True

    def set_status(self, message):
        self.status_var.set(message)

    def numeric_columns(self):
        return self.data.select_dtypes(include="number").columns.tolist()

    def refresh_widgets(self):
        """Update dropdowns and lists after the dataset changes."""
        if self.data is None:
            return

        all_columns = self.data.columns.tolist()
        self.sort_combo["values"] = all_columns
        if all_columns:
            self.sort_combo.set(all_columns[0])

        numeric = self.numeric_columns()
        self.agg_combo["values"] = numeric
        if numeric:
            self.agg_combo.set(numeric[0])

        self.country_list.delete(0, "end")
        for country in sorted(self.data["Country or region"].astype(str)):
            self.country_list.insert("end", country)

        low, high = self.data["Score"].min(), self.data["Score"].max()
        self.range_hint.configure(
            text=f"Scores in this dataset range from {low} to {high}"
        )

    # ---------- 1. LOAD DATASET ----------

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Select World Happiness CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.file_var.set(path)

    def load_data(self):
        file_path = self.file_var.get().strip() or "data_set.csv"

        try:
            if not os.path.exists(file_path):
                messagebox.showerror(
                    "File not found",
                    "File not found!\nKeep data_set.csv in the same folder as "
                    "this program, or use Browse.",
                )
                return

            data = pd.read_csv(file_path)

            if data.empty:
                messagebox.showerror("Empty file", "The CSV file is empty!")
                return

            missing = [c for c in REQUIRED_COLUMNS if c not in data.columns]
            if missing:
                messagebox.showerror(
                    "Missing columns",
                    "These required columns are missing:\n\n" + "\n".join(missing),
                )
                return

            self.data = data
            self.result = None
            self.last_figure = None
            self.refresh_widgets()

            self.explore_pane.show_df(self.data.head(5))
            self.set_status(
                f"Loaded {os.path.basename(file_path)} - "
                f"{self.data.shape[0]} rows, {self.data.shape[1]} columns."
            )
            self.notebook.select(0)

        except pd.errors.EmptyDataError:
            messagebox.showerror("Empty file", "The CSV file is empty!")
        except pd.errors.ParserError:
            messagebox.showerror("Invalid file", "Invalid CSV file format!")
        except Exception as error:
            messagebox.showerror("Error", f"Unable to load dataset: {error}")

    # ---------- 2. EXPLORE DATA ----------

    def build_explore_tab(self):
        tab = self.new_tab("Explore Data")

        controls = ttk.Frame(tab)
        controls.pack(fill="x", pady=(0, 8))

        ttk.Label(controls, text="Number of rows:").pack(side="left")
        self.rows_var = tk.IntVar(value=10)
        ttk.Spinbox(
            controls, from_=1, to=1000, textvariable=self.rows_var, width=6
        ).pack(side="left", padx=6)
        ttk.Button(controls, text="Display first rows", command=self.show_rows).pack(
            side="left", padx=4
        )
        ttk.Button(controls, text="Data types & info", command=self.show_info).pack(
            side="left", padx=4
        )

        self.explore_pane = OutputPane(tab)
        self.explore_pane.pack(fill="both", expand=True)

    def show_rows(self):
        if not self.need_data():
            return
        try:
            n = int(self.rows_var.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Invalid input", "Enter a whole number of rows.")
            return
        n = max(1, min(n, len(self.data)))
        self.explore_pane.show_df(self.data.head(n))
        self.set_status(f"Showing first {n} rows.")

    def show_info(self):
        if not self.need_data():
            return
        buffer = io.StringIO()
        self.data.info(buf=buffer)
        self.explore_pane.show_text("Dataset information:\n\n" + buffer.getvalue())

    # ---------- 3. CLEAN DATA ----------

    def build_clean_tab(self):
        tab = self.new_tab("Clean Data")

        controls = ttk.Frame(tab)
        controls.pack(fill="x", pady=(0, 8))

        ttk.Button(
            controls, text="Check missing values", command=self.check_missing
        ).pack(side="left", padx=4)
        ttk.Button(
            controls, text="Remove rows with missing values", command=self.drop_missing
        ).pack(side="left", padx=4)
        ttk.Button(
            controls,
            text="Fill missing numeric values with mean",
            command=self.fill_mean,
        ).pack(side="left", padx=4)

        self.clean_pane = OutputPane(tab)
        self.clean_pane.pack(fill="both", expand=True)

    def check_missing(self):
        if not self.need_data():
            return
        counts = self.data.isna().sum()
        text = (
            "Missing values in each column:\n\n"
            + counts.to_string()
            + f"\n\nTotal missing values: {counts.sum()}"
        )
        self.clean_pane.show_text(text)

    def drop_missing(self):
        if not self.need_data():
            return
        before = len(self.data)
        self.data = self.data.dropna().copy()
        removed = before - len(self.data)
        self.refresh_widgets()
        self.clean_pane.show_text(
            f"Removed {removed} rows.\nRows left: {len(self.data)}"
        )
        self.set_status(f"Removed {removed} rows with missing values.")

    def fill_mean(self):
        if not self.need_data():
            return
        for column in self.numeric_columns():
            self.data[column] = self.data[column].fillna(self.data[column].mean())
        self.clean_pane.show_text("Missing numeric values filled with column means.")
        self.set_status("Missing numeric values filled with mean.")

    # ---------- 4. SEARCH / SORT / FILTER ----------

    def build_search_tab(self):
        tab = self.new_tab("Search / Sort / Filter")

        # Search
        search_box = ttk.LabelFrame(tab, text="Search country", padding=6)
        search_box.pack(fill="x", pady=(0, 6))
        self.search_var = tk.StringVar()
        ttk.Entry(search_box, textvariable=self.search_var, width=30).pack(
            side="left", padx=4
        )
        ttk.Button(search_box, text="Search", command=self.do_search).pack(
            side="left", padx=4
        )
        ttk.Label(search_box, text="(full or partial country name)").pack(side="left")

        # Sort
        sort_box = ttk.LabelFrame(tab, text="Sort by a column", padding=6)
        sort_box.pack(fill="x", pady=(0, 6))
        self.sort_combo = ttk.Combobox(sort_box, state="readonly", width=32)
        self.sort_combo.pack(side="left", padx=4)
        self.sort_order = tk.IntVar(value=2)
        ttk.Radiobutton(
            sort_box, text="Ascending", variable=self.sort_order, value=1
        ).pack(side="left", padx=4)
        ttk.Radiobutton(
            sort_box, text="Descending", variable=self.sort_order, value=2
        ).pack(side="left", padx=4)
        ttk.Button(sort_box, text="Sort", command=self.do_sort).pack(
            side="left", padx=4
        )

        # Filter
        filter_box = ttk.LabelFrame(tab, text="Filter by happiness score", padding=6)
        filter_box.pack(fill="x", pady=(0, 8))
        ttk.Label(filter_box, text="Min:").pack(side="left")
        self.min_var = tk.StringVar()
        ttk.Entry(filter_box, textvariable=self.min_var, width=8).pack(
            side="left", padx=4
        )
        ttk.Label(filter_box, text="Max:").pack(side="left")
        self.max_var = tk.StringVar()
        ttk.Entry(filter_box, textvariable=self.max_var, width=8).pack(
            side="left", padx=4
        )
        ttk.Button(filter_box, text="Filter", command=self.do_filter).pack(
            side="left", padx=4
        )
        self.range_hint = ttk.Label(filter_box, text="")
        self.range_hint.pack(side="left", padx=10)

        self.search_pane = OutputPane(tab)
        self.search_pane.pack(fill="both", expand=True)

    def do_search(self):
        if not self.need_data():
            return
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Empty input", "Enter a country name to search.")
            return
        matches = self.data["Country or region"].str.contains(
            query, case=False, na=False, regex=False
        )
        self.result = self.data[matches]
        self.search_pane.show_df(self.result)
        self.set_status(f"Search found {len(self.result)} matching row(s).")

    def do_sort(self):
        if not self.need_data():
            return
        column = self.sort_combo.get()
        if not column:
            return
        ascending = self.sort_order.get() == 1
        self.result = self.data.sort_values(by=column, ascending=ascending)
        self.search_pane.show_df(self.result.head(20))
        self.set_status(f"Sorted by '{column}' (showing top 20 rows).")

    def do_filter(self):
        if not self.need_data():
            return
        try:
            minimum = float(self.min_var.get())
            maximum = float(self.max_var.get())
        except ValueError:
            messagebox.showerror(
                "Invalid input", "Enter valid numbers for min and max."
            )
            return

        if minimum > maximum:
            messagebox.showerror(
                "Invalid range", "Minimum score cannot be greater than maximum score."
            )
            return

        self.result = self.data[
            self.data["Score"].between(minimum, maximum)
        ].sort_values("Score", ascending=False)
        self.search_pane.show_df(self.result)
        self.set_status(
            f"{len(self.result)} countries have Score between {minimum} and {maximum}."
        )

    # ---------- 5. AGGREGATION ----------

    def build_aggregation_tab(self):
        tab = self.new_tab("Aggregation")

        controls = ttk.Frame(tab)
        controls.pack(fill="x", pady=(0, 8))

        ttk.Label(controls, text="Column:").pack(side="left")
        self.agg_combo = ttk.Combobox(controls, state="readonly", width=32)
        self.agg_combo.pack(side="left", padx=6)
        ttk.Button(controls, text="Mean", command=lambda: self.aggregate("mean")).pack(
            side="left", padx=4
        )
        ttk.Button(
            controls, text="Median", command=lambda: self.aggregate("median")
        ).pack(side="left", padx=4)
        ttk.Button(
            controls, text="Count by Happiness Category", command=self.category_count
        ).pack(side="left", padx=12)

        self.agg_pane = OutputPane(tab)
        self.agg_pane.pack(fill="both", expand=True)

    def aggregate(self, kind):
        if not self.need_data():
            return
        column = self.agg_combo.get()
        if not column:
            return
        values = self.data[column]
        value = values.mean() if kind == "mean" else values.median()
        self.agg_pane.show_text(f"{kind.capitalize()} of '{column}': {round(value, 3)}")

    def category_count(self):
        if not self.need_data():
            return
        counts = happiness_category_counts(self.data["Score"])
        lines = ["Country count by happiness category:\n"]
        lines += [f"{name}: {count}" for name, count in counts.items()]
        self.agg_pane.show_text("\n".join(lines))

    # ---------- 6. STATISTICAL ANALYSIS ----------

    def build_statistics_tab(self):
        tab = self.new_tab("Statistical Analysis")

        controls = ttk.Frame(tab)
        controls.pack(fill="x", pady=(0, 8))
        ttk.Button(
            controls, text="Run statistical analysis", command=self.run_statistics
        ).pack(side="left")

        self.stats_pane = OutputPane(tab)
        self.stats_pane.pack(fill="both", expand=True)

    def run_statistics(self):
        if not self.need_data():
            return
        correlation = self.data[["Score"] + FACTOR_COLUMNS].corr()
        score_corr = correlation["Score"].drop("Score").sort_values(ascending=False)

        text = (
            "Descriptive statistics:\n\n"
            + self.data.select_dtypes(include="number").describe().round(3).to_string()
            + "\n\n\nCorrelation matrix (excluding Overall rank):\n\n"
            + correlation.round(3).to_string()
            + "\n\n\nCorrelation of each factor with Happiness Score:\n\n"
            + score_corr.round(3).to_string()
        )
        self.stats_pane.show_text(text)

    # ---------- 7. HAPPINESS ANALYSIS ----------

    def build_happiness_tab(self):
        tab = self.new_tab("Happiness Analysis")

        left = ttk.Frame(tab)
        left.pack(side="left", fill="y", padx=(0, 10))

        ttk.Button(left, text="Top 10 happiest countries", command=self.top10).pack(
            fill="x", pady=2
        )
        ttk.Button(
            left, text="Bottom 10 least happy countries", command=self.bottom10
        ).pack(fill="x", pady=2)
        ttk.Button(
            left, text="Strongest factor for happiness", command=self.strongest_factor
        ).pack(fill="x", pady=2)

        ttk.Label(left, text="\nCompare countries (Ctrl+click for many):").pack(
            anchor="w"
        )
        list_frame = ttk.Frame(left)
        list_frame.pack(fill="y", expand=True)
        self.country_list = tk.Listbox(
            list_frame, selectmode="extended", exportselection=False, width=30
        )
        scroll = ttk.Scrollbar(list_frame, command=self.country_list.yview)
        self.country_list.configure(yscrollcommand=scroll.set)
        self.country_list.pack(side="left", fill="y", expand=True)
        scroll.pack(side="left", fill="y")
        ttk.Button(left, text="Compare selected", command=self.compare_countries).pack(
            fill="x", pady=4
        )

        self.happy_pane = OutputPane(tab)
        self.happy_pane.pack(side="left", fill="both", expand=True)

    def top10(self):
        if not self.need_data():
            return
        self.result = self.data.nlargest(10, "Score")[
            ["Overall rank", "Country or region", "Score"]
        ]
        self.happy_pane.show_df(self.result)
        self.set_status("Top 10 happiest countries.")

    def bottom10(self):
        if not self.need_data():
            return
        self.result = self.data.nsmallest(10, "Score")[
            ["Overall rank", "Country or region", "Score"]
        ]
        self.happy_pane.show_df(self.result)
        self.set_status("Bottom 10 least happy countries.")

    def compare_countries(self):
        if not self.need_data():
            return
        selected = [self.country_list.get(i) for i in self.country_list.curselection()]
        if not selected:
            messagebox.showwarning("Nothing selected", "Select one or more countries.")
            return
        names = [name.lower() for name in selected]
        self.result = self.data[self.data["Country or region"].str.lower().isin(names)][
            ["Country or region", "Score"] + FACTOR_COLUMNS
        ]
        self.happy_pane.show_df(self.result)
        self.set_status(f"Comparing {len(self.result)} countries.")

    def strongest_factor(self):
        if not self.need_data():
            return
        correlation = (
            self.data[["Score"] + FACTOR_COLUMNS].corr()["Score"].drop("Score")
        )
        strongest = correlation.abs().idxmax()
        self.happy_pane.show_text(
            "Factor with strongest correlation to Happiness Score:\n\n"
            f"Factor:       {strongest}\n"
            f"Correlation:  {round(correlation[strongest], 3)}\n\n"
            "All factors:\n\n"
            + correlation.sort_values(ascending=False).round(3).to_string()
        )

    # ---------- 8. DATA VISUALIZATION ----------

    def build_visualization_tab(self):
        tab = self.new_tab("Visualization")

        controls = ttk.Frame(tab)
        controls.pack(fill="x", pady=(0, 8))

        ttk.Label(controls, text="Chart:").pack(side="left")
        self.chart_combo = ttk.Combobox(
            controls, state="readonly", values=CHART_OPTIONS, width=58
        )
        self.chart_combo.current(0)
        self.chart_combo.pack(side="left", padx=6)
        ttk.Button(controls, text="Generate chart", command=self.draw_chart).pack(
            side="left", padx=4
        )
        ttk.Button(controls, text="Save chart as image", command=self.save_chart).pack(
            side="left", padx=4
        )

        chart_frame = ttk.Frame(tab)
        chart_frame.pack(fill="both", expand=True)

        self.figure = Figure(figsize=(9, 5.5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        toolbar = NavigationToolbar2Tk(self.canvas, chart_frame)
        toolbar.update()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def draw_chart(self):
        if not self.need_data():
            return

        choice = self.chart_combo.current() + 1
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        try:
            correlation_data = self.data[["Score"] + FACTOR_COLUMNS].corr()

            if choice == 1:
                chart_data = self.data.nlargest(10, "Score").sort_values("Score")
                sns.barplot(data=chart_data, x="Score", y="Country or region", ax=ax)
                ax.set_title("Top 10 Happiest Countries")

            elif choice == 2:
                counts = happiness_category_counts(self.data["Score"])
                labels = [name for name, count in counts.items() if count > 0]
                values = [count for count in counts.values() if count > 0]
                ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
                ax.set_title("Countries by Happiness Category")

            elif choice == 3:
                sns.histplot(data=self.data, x="Score", bins=15, kde=True, ax=ax)
                ax.set_title("Distribution of Happiness Scores")

            elif choice == 4:
                sns.boxplot(data=self.data[FACTOR_COLUMNS], orient="h", ax=ax)
                ax.set_title("Spread of Happiness Factors")

            elif choice == 5:
                sns.regplot(data=self.data, x="GDP per capita", y="Score", ax=ax)
                ax.set_title("GDP per capita vs Happiness Score")

            elif choice == 6:
                top = self.data.nlargest(10, "Score")[FACTOR_COLUMNS].mean()
                bottom = self.data.nsmallest(10, "Score")[FACTOR_COLUMNS].mean()
                pd.DataFrame({"Top 10": top, "Bottom 10": bottom}).plot(
                    kind="bar", ax=ax
                )
                ax.set_title("Average Factors: Top 10 vs Bottom 10 Countries")
                for label in ax.get_xticklabels():
                    label.set_rotation(30)
                    label.set_ha("right")

            elif choice == 7:
                ranked = self.data.sort_values("Overall rank")
                ax.plot(
                    ranked["Overall rank"], ranked["Score"], marker="o", markersize=3
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
                ax.set_title("Correlation Heatmap - World Happiness")

            self.figure.tight_layout()
            self.canvas.draw()
            self.last_figure = self.figure
            self.set_status(f"Chart created: {self.chart_combo.get()}")

        except Exception as error:
            messagebox.showerror("Chart error", f"Unable to create chart: {error}")

    def save_chart(self):
        if not self.need_data():
            return
        if self.last_figure is None:
            messagebox.showwarning(
                "No chart", "Please generate a chart first, then save it."
            )
            return
        path = filedialog.asksaveasfilename(
            title="Save chart",
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
        )
        if not path:
            return
        try:
            self.last_figure.savefig(path, bbox_inches="tight", dpi=300)
            self.set_status(f"Chart saved: {path}")
            messagebox.showinfo("Saved", f"Visualization saved successfully:\n{path}")
        except Exception as error:
            messagebox.showerror("Save error", f"Unable to save visualization: {error}")

    # ---------- 9 & 10. SAVE ----------

    def build_save_tab(self):
        tab = self.new_tab("Save")

        box = ttk.LabelFrame(tab, text="Export", padding=14)
        box.pack(anchor="nw", padx=6, pady=6)

        ttk.Button(
            box, text="Save current dataset as CSV", command=self.save_dataset, width=34
        ).pack(pady=5)
        ttk.Button(
            box, text="Save last result as CSV", command=self.save_last_result, width=34
        ).pack(pady=5)
        ttk.Button(
            box, text="Save last chart as PNG", command=self.save_chart, width=34
        ).pack(pady=5)

    def write_csv(self, frame, include_index):
        path = filedialog.asksaveasfilename(
            title="Save CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        try:
            frame.to_csv(path, index=include_index)
            self.set_status(f"File saved: {path}")
            messagebox.showinfo("Saved", f"File saved successfully:\n{path}")
        except Exception as error:
            messagebox.showerror("Save error", f"Unable to save file: {error}")

    def save_dataset(self):
        if not self.need_data():
            return
        self.write_csv(self.data, include_index=False)

    def save_last_result(self):
        if not self.need_data():
            return
        if self.result is None:
            messagebox.showwarning(
                "No result", "No result available. Perform an analysis first."
            )
            return
        self.write_csv(self.result, include_index=True)


if __name__ == "__main__":
    app = HappinessApp()
    app.mainloop()
