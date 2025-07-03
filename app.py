import copy

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from budgeter.obligation_types import ObligationType
from budgeter.obligation import Obligation
from budgeter.payment_plan import run_payment_plan

st.markdown("# Debt Calculator")
st.markdown(
    "This is a calculator you can use to see how different debt strategies can affect how much you will pay off over time."
)


def run_payment_plans_for_different_payments(
    debt_list: list[Obligation], payments: list[float], strategy: str
):
    all_dfs = []
    for payment in payments:
        curr_debt_list = copy.deepcopy(debt_list)

        curr_df = run_payment_plan(curr_debt_list, payment)
        curr_df["strategy"] = strategy
        curr_df["monthly_payment"] = payment
        all_dfs.append(curr_df)

    return all_dfs


if "debt_df" not in st.session_state:
    debt_df = pd.DataFrame(
        data={"Amount": [20000], "Interest Rate": [3], "Minimum Payment": [300]}
    )

    st.session_state.debt_df = debt_df
    st.session_state.strategy_disabled = True


if "payment_df" not in st.session_state:
    payment_df = pd.DataFrame(
        data={"Amount": [200]},
    )

    st.session_state.payment_df = payment_df

st.markdown("## Loan Information")
st.markdown(
    """
    Set up information about your loan here. You can probably use personal data because I don't have any particular desire to learn how to steal it from you.
    
    ### Debt Details
    Enter any number of loans, their interest rates, and their minimum payments if they have any in the table below."""
)

curr_debt_df = st.data_editor(
    st.session_state.debt_df,
    column_config={
        "Amount": st.column_config.NumberColumn(
            "Loan Amount",
            min_value=0,
            step=1,
            format="dollar",
            required=True,
        ),
        "Interest Rate": st.column_config.NumberColumn(
            "Interest Rate", min_value=0, step=0.01, format="%f%%", required=True
        ),
        "Minimum Payment": st.column_config.NumberColumn(
            "Minimum Payment", min_value=0, step=1, format="dollar", required=True
        ),
    },
    num_rows="dynamic",
    hide_index=True,
)

st.markdown(
    """
    ### Monthly Payments

    Enter how much money you can put down to all loans combined. You can enter multiple values to see how it will affect your repayment. 
    """
)
curr_payment_df = st.data_editor(
    st.session_state.payment_df,
    column_config={
        "Amount": st.column_config.NumberColumn(
            "Payment Amount",
            min_value=1,
            step=1,
            format="dollar",
            required=True,
        )
    },
    num_rows="dynamic",
)

master_debt_list = []
for i, row in curr_debt_df.iterrows():
    master_debt_list.append(
        Obligation(
            f"Loan {i}",
            amount=row["Amount"],
            interest_rate=row["Interest Rate"],
            minimum_payment=row["Minimum Payment"],
        )
    )

st.markdown(
    """
    ### Strategies

    Check which strategies you want to examine for paying off the loans. These will not do anything if you only have a single loan.

    The snowball method is a favorite of Dave Ramsey. With this method you payoff your smallest debts first and then use the extra money you've 
    freed up to pay off the next biggest debt. For more details see [here](https://www.ramseysolutions.com/debt/how-the-debt-snowball-method-works?srsltid=AfmBOoreCjJEojZdIiVnpkaiBETAU6Q_G9QCmSNMRTrHHS_XlrPtGYXG).

    The avalanche method is where you pay off the debts with the highest interest rates first. See this [article](https://www.nerdwallet.com/article/finance/what-is-a-debt-avalanche) for more detail.

    Finally, the table order will try to pay off the debts as you've entered them in the table above. This will let you test out any custom scenarios. 

    """
)

col1, col2, col3 = st.columns(3)
with col1:
    use_snowball = st.checkbox(
        label="Snowball",
        key="chk_snowball",
        value=True,
    )
with col2:
    use_avalanche = st.checkbox(
        label="Avalanche",
        key="chk_avalanche",
    )
with col3:
    use_table = st.checkbox(
        label="Table Order",
        key="chk_table",
    )

st.markdown("## Results")
if len(curr_debt_df) == 0:
    st.write("Add some debts to get started.")
elif len(curr_payment_df) == 0:
    st.write("Add some payment options to get started.")
elif not use_snowball and not use_avalanche and not use_table:
    st.write("You must select at least one strategy.")
else:

    all_dfs = []
    payments = curr_payment_df["Amount"].tolist()

    if len(curr_debt_df) > 1:
        if use_snowball:
            snowball_debt_list = sorted(
                master_debt_list, key=lambda debt: debt.amount, reverse=False
            )

            all_dfs += run_payment_plans_for_different_payments(
                snowball_debt_list, payments, "snowball"
            )

        if use_avalanche:
            avalanche_debt_list = sorted(
                master_debt_list, key=lambda debt: debt.interest_rate, reverse=True
            )
            all_dfs += run_payment_plans_for_different_payments(
                avalanche_debt_list, payments, "avalanche"
            )

        if use_table:
            all_dfs += run_payment_plans_for_different_payments(
                master_debt_list, payments, "Table Order"
            )
    else:
        all_dfs += run_payment_plans_for_different_payments(
            master_debt_list, payments, "Pay"
        )

    summary_df = pd.DataFrame(
        columns=["Monthly Payment", "Strategy", "Total Paid", "Time Taken", "months"]
    )
    num_to_display = 0

    balance_fig = go.Figure()
    total_fig = go.Figure()

    for df in all_dfs:
        overall_total_paid = df.iloc[-1]["total_paid"]
        initial_total_balance = df.iloc[0]["total_balance"]
        months_took = int(df.iloc[-1]["month"])
        monthly_payment = df.iloc[0]["monthly_payment"]
        strategy = df.iloc[0]["strategy"].title()

        month_tick = 12 if months_took >= 24 else 3

        years_took = int(months_took / 12)
        months_remaining = months_took % 12

        if months_took >= 12 * 100:

            summary_df.loc[len(summary_df)] = {
                "Monthly Payment": monthly_payment,
                "Strategy": strategy,
                "Time Taken": f"Will not pay off in 100 years",
            }

        else:
            num_to_display += 1
            summary_df.loc[len(summary_df)] = {
                "Monthly Payment": monthly_payment,
                "Strategy": strategy,
                "Total Paid": overall_total_paid,
                "Time Taken": f"{years_took:d} year(s) and {months_remaining:d} month(s)",
            }

            balance_fig.add_trace(
                go.Scatter(
                    x=df["month"],
                    y=df["total_balance"],
                    name=f"{strategy} - ${monthly_payment:,.2f}",
                )
            )
            total_fig.add_trace(
                go.Scatter(
                    x=df["month"],
                    y=df["total_paid"],
                    name=f"{strategy} - ${monthly_payment:,.2f}",
                )
            )

    summary_df = summary_df.sort_values(by="Monthly Payment")
    summary_df["Savings from Worst Scenario"] = (
        summary_df["Total Paid"].max() - summary_df["Total Paid"]
    )

    st.dataframe(
        summary_df,
        column_config={
            "Monthly Payment": st.column_config.NumberColumn(
                format="dollar",
            ),
            "Total Paid": st.column_config.NumberColumn(
                format="dollar",
            ),
            "Savings from Worst Scenario": st.column_config.NumberColumn(
                format="dollar",
            ),
        },
        hide_index=True,
    )

    if num_to_display > 0:

        balance_fig.update_layout(
            title="Outstanding Balance by Month",
            xaxis_title="Month",
            yaxis_title="Dollars ($)",
            xaxis=dict(tickmode="linear", tick0=0, dtick=month_tick),
        )
        total_fig.update_layout(
            title="Total Paid by Month",
            xaxis_title="Month",
            yaxis_title="Dollars ($)",
            xaxis=dict(tickmode="linear", tick0=0, dtick=month_tick),
        )

        st.plotly_chart(balance_fig)
        st.plotly_chart(total_fig)

    st.markdown("## Strategy Details")
    st.markdown("Here you can select a specific strategy to see how")
    payment_options = {
        f"{row['Strategy']} - ${row['Monthly Payment']}": (
            row["Strategy"],
            row["Monthly Payment"],
        )
        for i, row in summary_df[["Monthly Payment", "Strategy"]].iterrows()
    }

    selected_strategy_key = st.selectbox(
        label="Select Payment Strategy", options=payment_options.keys()
    )

    selected_strategy, selected_payment_amount = payment_options[selected_strategy_key]

    def find_df_to_breakdown(all_dfs, selected_strategy, selected_payment_amount):
        for df in all_dfs:
            curr_monthly_payment = df.iloc[0]["monthly_payment"]
            curr_strategy = df.iloc[0]["strategy"].title()

            if (
                curr_monthly_payment == selected_payment_amount
                and curr_strategy == selected_strategy
            ):
                return df

    selected_df = find_df_to_breakdown(
        all_dfs, selected_strategy, selected_payment_amount
    )

    breakdown_balance_fig = go.Figure()
    breakdown_total_paid_fig = go.Figure()

    for i in range(len(curr_debt_df)):

        breakdown_balance_fig.add_trace(
            go.Scatter(
                x=selected_df["month"],
                y=selected_df[f"Loan {i}_balance"],
                name=f"Loan {i+1}",
            )
        )
        breakdown_total_paid_fig.add_trace(
            go.Scatter(
                x=selected_df["month"],
                y=selected_df[f"Loan {i}_total_paid"],
                name=f"Loan {i+1}",
            )
        )

    breakdown_balance_fig.update_layout(
        title=f"Outstanding Balance by Month for {selected_strategy_key}",
        xaxis_title="Month",
        yaxis_title="Dollars ($)",
        xaxis=dict(tickmode="linear", tick0=0, dtick=month_tick),
    )
    breakdown_total_paid_fig.update_layout(
        title=f"Total Paid by Month for {selected_strategy_key}",
        xaxis_title="Month",
        yaxis_title="Dollars ($)",
        xaxis=dict(tickmode="linear", tick0=0, dtick=month_tick),
    )

    st.plotly_chart(breakdown_balance_fig)
    st.plotly_chart(breakdown_total_paid_fig)
    # st.dataframe(selected_df)
