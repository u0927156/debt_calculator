# %%
from budgeter.obligation import Obligation
from budgeter.obligation_types import ObligationType
from budgeter.payment_plan import run_payment_plan

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# %%
# Set up debt parameters
debt_params_list = [
    dict(
        name="loan_a",
        amount=5000,
        obligation_type=ObligationType.LOAN,
        interest_rate=3,
        minimum_payment=100,
    ),
    dict(
        name="loan_b",
        amount=20000,
        obligation_type=ObligationType.LOAN,
        interest_rate=8,
        minimum_payment=100,
    ),
    dict(
        name="loan_c",
        amount=1000,
        obligation_type=ObligationType.LOAN,
        interest_rate=0,
        minimum_payment=10,
    ),
    dict(
        name="loan_d",
        amount=1500,
        obligation_type=ObligationType.LOAN,
        interest_rate=10,
        minimum_payment=50,
    ),
]

monthly_funds = 750


# %%
# Run snowball method
snowball_debt_list = [Obligation(**debt_param) for debt_param in debt_params_list]
snowball_debt_list = sorted(
    snowball_debt_list, key=lambda debt: debt.amount, reverse=False
)
snowball_df = run_payment_plan(snowball_debt_list, monthly_funds=monthly_funds)

# %%
# Run avalanche method
avalanche_debt_list = [Obligation(**debt_param) for debt_param in debt_params_list]
avalanche_debt_list = sorted(
    avalanche_debt_list, key=lambda debt: debt.interest_rate, reverse=True
)
avalanche_df = run_payment_plan(avalanche_debt_list, monthly_funds=monthly_funds)
# %%
# Compare results


def get_and_plot_results(debt_list, debt_df: pd.DataFrame, title):
    fig = go.Figure()

    balance_columns = sorted([col for col in debt_df.columns if "_balance" in col])
    total_paid_columns = sorted(
        [col for col in debt_df.columns if "_total_paid" in col]
    )

    for balance_col in balance_columns:
        fig.add_trace(
            go.Scatter(
                x=debt_df["month"],
                y=debt_df[balance_col],
                name=balance_col,
            )
        )

    for total_paid_col in total_paid_columns:
        fig.add_trace(
            go.Scatter(
                x=debt_df["month"],
                y=debt_df[total_paid_col],
                name=total_paid_col,
            )
        )

    fig.update_layout(title=title, xaxis_title="Months", yaxis_title="Dollars ($)")

    total_paid = sum(
        debt_df.iloc[-1][[f"{debt.name}_total_paid" for debt in debt_list]]
    )

    return fig, total_paid


snowball_figure, snowball_total = get_and_plot_results(
    snowball_debt_list, snowball_df, "Snowball Method"
)
avalanche_figure, avalanche_total = get_and_plot_results(
    avalanche_debt_list, avalanche_df, "Avalanche Method"
)


snowball_figure.show()
avalanche_figure.show()
print(f"Snowball method total paid = {snowball_total:.2f}")
print(f"Avalanche method total paid = {avalanche_total:.2f}")


# %%
