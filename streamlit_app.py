import streamlit as st
import pandas as pd

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="RupeeLens",
    page_icon="💰",
    layout="wide"
)

st.title("💰 RupeeLens")
st.subheader("See where your money really goes.")

st.write(
    "Upload your bank statement and RupeeLens will automatically "
    "categorize your transactions, analyze your spending and help "
    "identify potential savings."
)

st.divider()


# --------------------------------------------------
# TRANSACTION CATEGORIZATION
# --------------------------------------------------

def categorize_transaction(description):

    description = str(description).lower()

    # EMI / Loans
    if any(word in description for word in [
        "emi", "loan", "bajaj finance",
        "home loan", "personal loan"
    ]):
        return "🏦 EMI"

    # Petrol / Fuel
    elif any(word in description for word in [
        "petrol", "fuel", "iocl",
        "indian oil", "hpcl", "bpcl", "shell"
    ]):
        return "⛽ Petrol"

    # Grocery
    elif any(word in description for word in [
        "dmart", "d mart", "reliance smart",
        "grocery", "supermarket", "more supermarket"
    ]):
        return "🛒 Grocery"

    # Food
    elif any(word in description for word in [
        "swiggy", "zomato", "restaurant",
        "cafe", "dominos", "mcdonald"
    ]):
        return "🍔 Food"

    # Entertainment
    elif any(word in description for word in [
        "pvr", "inox", "bookmyshow",
        "gaming", "cinema"
    ]):
        return "🎬 Entertainment"

    # Travel
    elif any(word in description for word in [
        "uber", "ola", "irctc",
        "indigo", "air india",
        "makemytrip", "rapido"
    ]):
        return "✈️ Travel"

    # Subscriptions
    elif any(word in description for word in [
        "netflix", "spotify",
        "youtube premium",
        "hotstar", "prime video"
    ]):
        return "🔁 Subscriptions"

    else:
        return "💳 Normal Transactions"


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

st.header("📄 Upload Bank Statement")

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel bank statement",
    type=["csv", "xlsx"]
)

st.caption(
    "🔒 During development, use only fictional or sample bank statements."
)


# --------------------------------------------------
# ANALYSIS
# --------------------------------------------------

if uploaded_file is not None:

    try:

        # Read file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ Bank statement uploaded successfully!")

        st.subheader("📋 Statement Preview")

        st.dataframe(
            df,
            use_container_width=True
        )

        # --------------------------------------------------
        # FIND REQUIRED COLUMNS
        # --------------------------------------------------

        columns_lower = {
            str(col).lower().strip(): col
            for col in df.columns
        }

        description_column = None
        debit_column = None

        # Find description column
        possible_description_columns = [
            "description",
            "narration",
            "transaction details",
            "transaction description",
            "particulars",
            "remarks"
        ]

        for name in possible_description_columns:
            if name in columns_lower:
                description_column = columns_lower[name]
                break

        # Find debit column
        possible_debit_columns = [
            "debit",
            "withdrawal",
            "withdrawal amount",
            "debit amount",
            "amount"
        ]

        for name in possible_debit_columns:
            if name in columns_lower:
                debit_column = columns_lower[name]
                break


        # --------------------------------------------------
        # RUN ANALYSIS
        # --------------------------------------------------

        if description_column and debit_column:

            # Clean debit values
            df[debit_column] = (
                df[debit_column]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("₹", "", regex=False)
            )

            df[debit_column] = pd.to_numeric(
                df[debit_column],
                errors="coerce"
            ).fillna(0)

            # Categorize transactions
            df["Category"] = df[
                description_column
            ].apply(categorize_transaction)

            st.divider()

            st.header("🔍 RupeeLens Analysis")

            # Total spending
            total_spending = df[debit_column].sum()

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "💸 Total Spending",
                    f"₹{total_spending:,.0f}"
                )

            with col2:
                st.metric(
                    "🧾 Transactions",
                    len(df)
                )

            st.divider()

            # --------------------------------------------------
            # CATEGORY ANALYSIS
            # --------------------------------------------------

            st.subheader("💰 Spending by Category")

            category_spending = (
                df.groupby("Category")[debit_column]
                .sum()
                .sort_values(ascending=False)
            )

            st.bar_chart(category_spending)

            st.dataframe(
                category_spending.reset_index(
                    name="Amount"
                ),
                use_container_width=True
            )

            st.divider()

            # --------------------------------------------------
            # TRANSACTIONS
            # --------------------------------------------------

            st.subheader("🏷️ Categorized Transactions")

            st.dataframe(
                df,
                use_container_width=True
            )

            st.divider()

            # --------------------------------------------------
            # BASIC SAVINGS ANALYSIS
            # --------------------------------------------------

            st.header("💡 Potential Savings")

            savings_categories = [
                "🍔 Food",
                "🎬 Entertainment",
                "🔁 Subscriptions"
            ]

            discretionary_spending = 0

            for category in savings_categories:

                if category in category_spending.index:

                    discretionary_spending += (
                        category_spending[category]
                    )

            estimated_savings = (
                discretionary_spending * 0.20
            )

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Flexible Spending",
                    f"₹{discretionary_spending:,.0f}"
                )

            with col2:

                st.metric(
                    "Possible Monthly Saving",
                    f"₹{estimated_savings:,.0f}"
                )

            if estimated_savings > 0:

                st.info(
                    "💡 RupeeLens identified spending in categories "
                    "that may be flexible. Reducing Food, Entertainment "
                    "and Subscription spending by 20% could save "
                    f"approximately ₹{estimated_savings:,.0f}."
                )

                st.success(
                    f"🌱 Potential annual saving: "
                    f"₹{estimated_savings * 12:,.0f}"
                )

            else:

                st.info(
                    "No obvious flexible spending opportunities "
                    "were identified in this statement."

                )

        else:

            st.warning(
                "⚠️ RupeeLens could not automatically identify "
                "the Description and Debit columns in this statement."
            )

            st.write(
                "Detected columns:",
                list(df.columns)
            )


    except Exception as error:

        st.error(
            "RupeeLens could not read this statement."
        )

        st.write(error)


# --------------------------------------------------
# EMPTY STATE
# --------------------------------------------------

else:

    st.info(
        "👆 Upload a sample bank statement to begin."
    )

    st.divider()

    st.header("🔍 What RupeeLens can analyze")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("💸 Spending")
        st.write(
            "See where your money is going."
        )

    with col2:
        st.subheader("🔁 Subscriptions")
        st.write(
            "Identify recurring expenses."
        )

    with col3:
        st.subheader("💡 Savings")
        st.write(
            "Find opportunities to save money."
        )


st.divider()

st.caption(
    "RupeeLens • Personal finance made clearer"
)