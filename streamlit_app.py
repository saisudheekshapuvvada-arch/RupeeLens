import streamlit as st
import pandas as pd
from io import BytesIO

# =========================================================
# RUPEELENS v0.2
# =========================================================

st.set_page_config(
    page_title="RupeeLens",
    page_icon="💰",
    layout="wide"
)

# ---------------------------------------------------------
# CATEGORY RULES
# ---------------------------------------------------------

CATEGORY_RULES = {
    "🏦 EMI / Loans": [
        "emi", "loan", "bajaj finance", "home loan",
        "personal loan", "vehicle loan", "car loan"
    ],
    "⛽ Petrol / Fuel": [
        "petrol", "fuel", "iocl", "indian oil",
        "hpcl", "bpcl", "shell"
    ],
    "🛒 Grocery": [
        "dmart", "d mart", "reliance smart", "grocery",
        "supermarket", "more supermarket", "instamart",
        "blinkit", "zepto"
    ],
    "🍔 Food": [
        "swiggy", "zomato", "restaurant", "cafe",
        "dominos", "mcdonald", "starbucks", "kfc"
    ],
    "🎬 Entertainment": [
        "pvr", "inox", "bookmyshow", "gaming",
        "cinema"
    ],
    "✈️ Travel": [
        "uber", "ola", "irctc", "indigo", "air india",
        "makemytrip", "rapido", "redbus"
    ],
    "🔁 Subscriptions": [
        "netflix", "spotify", "youtube premium",
        "hotstar", "prime video", "apple.com/bill"
    ],
    "🛍️ Shopping": [
        "amazon", "flipkart", "myntra", "ajio",
        "meesho", "nykaa"
    ],
    "🏠 Rent": [
        "rent", "house rent"
    ],
    "💡 Utilities": [
        "electricity", "water bill", "broadband",
        "internet", "airtel", "jio", "bescom",
        "tsspdcl", "gas bill"
    ],
    "🏥 Healthcare": [
        "hospital", "pharmacy", "medical",
        "apollo", "medplus", "clinic"
    ],
    "🛡️ Insurance": [
        "insurance", "lic", "policy premium"
    ],
    "📈 Investments": [
        "mutual fund", "sip", "zerodha",
        "groww", "investment"
    ],
    "🏧 Cash Withdrawal": [
        "atm", "cash withdrawal"
    ]
}

ALL_CATEGORIES = list(CATEGORY_RULES.keys()) + [
    "💳 Normal Transactions"
]


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def categorize_transaction(description):
    """Assign a spending category using merchant keywords."""

    text = str(description).lower()

    # Grocery delivery needs to be checked before Food
    # because "Swiggy Instamart" contains "Swiggy".
    grocery_priority = [
        "instamart", "blinkit", "zepto"
    ]

    if any(word in text for word in grocery_priority):
        return "🛒 Grocery"

    for category, keywords in CATEGORY_RULES.items():
        if any(keyword in text for keyword in keywords):
            return category

    return "💳 Normal Transactions"


def find_column(df, possibilities):
    """Find a likely column using common bank statement names."""

    normalized = {
        str(column).lower().strip(): column
        for column in df.columns
    }

    for possibility in possibilities:
        if possibility in normalized:
            return normalized[possibility]

    return None


def clean_amount(series):
    """Convert bank amount columns to numbers."""

    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("INR", "", regex=False)
        .str.strip()
    )

    return pd.to_numeric(
        cleaned,
        errors="coerce"
    ).fillna(0)


def rupee(value):
    return f"₹{value:,.0f}"


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("💰 RupeeLens")

st.subheader("See where your money really goes.")

st.write(
    "Turn your bank statement into a clear picture of your income, "
    "expenses, EMIs, spending habits and potential savings."
)

st.caption("RupeeLens v0.2 • Financial clarity from your bank statement")

st.divider()


# ---------------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------------

st.header("📄 Upload Bank Statement")

uploaded_file = st.file_uploader(
    "Upload CSV or Excel (.xlsx)",
    type=["csv", "xlsx"]
)

st.caption(
    "🔒 Development version: use fictional or sample statements only."
)


# ---------------------------------------------------------
# EMPTY STATE
# ---------------------------------------------------------

if uploaded_file is None:

    st.info("👆 Upload a sample statement to start your analysis.")

    st.header("What RupeeLens analyzes")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("💸 Expenses")
        st.write("Understand where your money goes.")

    with col2:
        st.subheader("🏦 EMIs")
        st.write("Measure your monthly debt burden.")

    with col3:
        st.subheader("🔁 Recurring")
        st.write("Spot subscriptions and recurring expenses.")

    with col4:
        st.subheader("💡 Savings")
        st.write("Find realistic opportunities to save.")

    st.stop()


# ---------------------------------------------------------
# READ FILE
# ---------------------------------------------------------

try:

    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(
            uploaded_file,
            engine="openpyxl"
        )

except Exception as error:

    st.error("❌ RupeeLens could not read this statement.")
    st.code(str(error))
    st.stop()


st.success("✅ Statement uploaded successfully!")


# ---------------------------------------------------------
# IDENTIFY COLUMNS
# ---------------------------------------------------------

date_column = find_column(
    df,
    [
        "date",
        "transaction date",
        "txn date",
        "value date"
    ]
)

description_column = find_column(
    df,
    [
        "description",
        "narration",
        "transaction details",
        "transaction description",
        "particulars",
        "remarks"
    ]
)

debit_column = find_column(
    df,
    [
        "debit",
        "withdrawal",
        "withdrawal amount",
        "debit amount"
    ]
)

credit_column = find_column(
    df,
    [
        "credit",
        "deposit",
        "deposit amount",
        "credit amount"
    ]
)

amount_column = find_column(
    df,
    ["amount"]
)


# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------

if description_column is None:

    st.error(
        "❌ RupeeLens could not identify the transaction "
        "description column."
    )

    st.write("Columns found:", list(df.columns))

    st.stop()


# ---------------------------------------------------------
# PREPARE AMOUNTS
# ---------------------------------------------------------

if debit_column is not None:

    df["Debit_RupeeLens"] = clean_amount(
        df[debit_column]
    )

else:

    df["Debit_RupeeLens"] = 0.0


if credit_column is not None:

    df["Credit_RupeeLens"] = clean_amount(
        df[credit_column]
    )

else:

    df["Credit_RupeeLens"] = 0.0


# Fallback for statements with only an Amount column.
if (
    debit_column is None
    and credit_column is None
    and amount_column is not None
):

    amounts = clean_amount(
        df[amount_column]
    )

    df["Debit_RupeeLens"] = amounts.where(
        amounts > 0,
        0
    )


# ---------------------------------------------------------
# DATE CLEANING
# ---------------------------------------------------------

if date_column is not None:

    df["Date_RupeeLens"] = pd.to_datetime(
        df[date_column],
        errors="coerce",
        dayfirst=True
    )


# ---------------------------------------------------------
# TRANSACTION TYPE
# ---------------------------------------------------------

df["Transaction Type"] = "Expense"

df.loc[
    df["Credit_RupeeLens"] > 0,
    "Transaction Type"
] = "Income"


# ---------------------------------------------------------
# CATEGORIZATION
# ---------------------------------------------------------

df["Category"] = df[
    description_column
].apply(categorize_transaction)

df.loc[
    df["Transaction Type"] == "Income",
    "Category"
] = "💰 Income"


# ---------------------------------------------------------
# CALCULATIONS
# ---------------------------------------------------------

total_income = df["Credit_RupeeLens"].sum()

total_expenses = df["Debit_RupeeLens"].sum()

net_cash_flow = total_income - total_expenses

if total_income > 0:

    savings_rate = (
        net_cash_flow / total_income
    ) * 100

else:

    savings_rate = 0


emi_amount = df.loc[
    df["Category"] == "🏦 EMI / Loans",
    "Debit_RupeeLens"
].sum()


if total_income > 0:

    emi_burden = (
        emi_amount / total_income
    ) * 100

else:

    emi_burden = 0


# ---------------------------------------------------------
# FINANCIAL DASHBOARD
# ---------------------------------------------------------

st.divider()

st.header("📊 Financial Snapshot")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "💰 Income",
        rupee(total_income)
    )

with col2:

    st.metric(
        "💸 Expenses",
        rupee(total_expenses)
    )

with col3:

    st.metric(
        "🟢 Net Cash Flow",
        rupee(net_cash_flow)
    )

with col4:

    st.metric(
        "📈 Savings Rate",
        f"{savings_rate:.1f}%"
    )


col1, col2 = st.columns(2)

with col1:

    st.metric(
        "🏦 EMI Payments",
        rupee(emi_amount)
    )

with col2:

    st.metric(
        "⚖️ EMI Burden",
        f"{emi_burden:.1f}% of income"
    )


# ---------------------------------------------------------
# SPENDING BREAKDOWN
# ---------------------------------------------------------

st.divider()

st.header("💸 Where Your Money Went")

expense_df = df[
    df["Transaction Type"] == "Expense"
].copy()

category_spending = (
    expense_df.groupby("Category")["Debit_RupeeLens"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(category_spending)

category_table = category_spending.reset_index()

category_table.columns = [
    "Category",
    "Amount"
]

category_table["Share of Expenses"] = (
    category_table["Amount"]
    / total_expenses
    * 100
).fillna(0)

category_table["Amount"] = category_table[
    "Amount"
].map(rupee)

category_table["Share of Expenses"] = (
    category_table["Share of Expenses"]
    .map(lambda x: f"{x:.1f}%")
)

st.dataframe(
    category_table,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# SAVINGS ENGINE
# ---------------------------------------------------------

st.divider()

st.header("💡 RupeeLens Savings Opportunities")

savings_rules = {
    "🍔 Food": {
        "rate": 0.20,
        "message":
            "Reducing restaurant and food-delivery spending by 20%"
    },

    "🎬 Entertainment": {
        "rate": 0.25,
        "message":
            "Reducing discretionary entertainment spending by 25%"
    },

    "🔁 Subscriptions": {
        "rate": 0.30,
        "message":
            "Reviewing subscriptions and reducing them by 30%"
    },

    "🛍️ Shopping": {
        "rate": 0.15,
        "message":
            "Reducing discretionary shopping by 15%"
    }
}

potential_savings = 0
recommendations = []

for category, rule in savings_rules.items():

    category_amount = expense_df.loc[
        expense_df["Category"] == category,
        "Debit_RupeeLens"
    ].sum()

    if category_amount > 0:

        saving = category_amount * rule["rate"]

        potential_savings += saving

        recommendations.append(
            (
                category,
                category_amount,
                saving,
                rule["message"]
            )
        )


col1, col2 = st.columns(2)

with col1:

    st.metric(
        "🌱 Potential Monthly Saving",
        rupee(potential_savings)
    )

with col2:

    st.metric(
        "🚀 Potential Annual Saving",
        rupee(potential_savings * 12)
    )


for (
    category,
    spending,
    saving,
    message
) in recommendations:

    st.info(
        f"{category} **{rupee(spending)} spent**\n\n"
        f"{message} could save approximately "
        f"**{rupee(saving)} per month**."
    )


# ---------------------------------------------------------
# SUBSCRIPTION ANALYSIS
# ---------------------------------------------------------

st.divider()

st.header("🔁 Subscription Check")

subscription_df = expense_df[
    expense_df["Category"] == "🔁 Subscriptions"
].copy()

if len(subscription_df) > 0:

    subscription_total = subscription_df[
        "Debit_RupeeLens"
    ].sum()

    st.metric(
        "Subscription Spending",
        rupee(subscription_total)
    )

    display_columns = [
        description_column,
        "Debit_RupeeLens"
    ]

    st.dataframe(
        subscription_df[display_columns],
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "No known subscription payments detected."
    )


# ---------------------------------------------------------
# EDITABLE TRANSACTION REVIEW
# ---------------------------------------------------------

st.divider()

st.header("✏️ Review Transaction Categories")

st.write(
    "RupeeLens may occasionally misunderstand a merchant. "
    "You can correct categories below."
)

review_columns = []

if date_column is not None:
    review_columns.append(date_column)

review_columns += [
    description_column,
    "Debit_RupeeLens",
    "Credit_RupeeLens",
    "Category"
]

review_df = df[review_columns].copy()

edited_df = st.data_editor(
    review_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Category": st.column_config.SelectboxColumn(
            "Category",
            options=["💰 Income"] + ALL_CATEGORIES
        )
    },
    disabled=[
        column
        for column in review_columns
        if column != "Category"
    ]
)


# ---------------------------------------------------------
# DOWNLOAD ANALYZED TRANSACTIONS
# ---------------------------------------------------------

st.divider()

st.header("📥 Export Analysis")

csv_data = edited_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Categorized Transactions",
    data=csv_data,
    file_name="RupeeLens_Analyzed_Transactions.csv",
    mime="text/csv"
)


# ---------------------------------------------------------
# DISCLAIMER
# ---------------------------------------------------------

st.divider()

st.caption(
    "RupeeLens provides automated spending insights for informational "
    "purposes. Categories and savings estimates should be reviewed by "
    "the user and are not financial advice."
)