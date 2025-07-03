import pandas as pd

from budgeter.obligation import Obligation


def _get_total_balance(debts: list[Obligation]):
    total_balance = 0
    for debt in debts:
        debt_balance = debt.get_balance()

        total_balance += debt_balance

    return total_balance


def _get_total_paid(debts: list[Obligation]):
    total_paid = 0
    for debt in debts:
        paid = debt.get_total_paid()

        total_paid += paid

    return total_paid


def run_payment_plan(debts: list[Obligation], monthly_funds: float):

    dataframe_cols = (
        ["month"]
        + [f"{debt.name}_balance" for debt in debts]
        + [f"{debt.name}_total_paid" for debt in debts]
        + ["total_balance", "total_paid"]
    )

    df = pd.DataFrame(columns=dataframe_cols)

    df.loc[0] = {col: 0 for col in dataframe_cols}

    total_balance = 0
    for debt in debts:
        debt_balance = debt.get_balance()
        df[f"{debt.name}_balance"] = debt_balance

        total_balance += debt_balance

    df["total_balance"] = total_balance

    month = 1

    while not all([debt.is_finished for debt in debts]):
        total_minimum_payment = sum(
            [debt.minimum_payment for debt in debts if not debt.is_finished]
        )
        extra_payment = monthly_funds - total_minimum_payment

        monthly_dict = {}
        has_paid_extra = False
        for debt in debts:

            if debt.is_finished:
                monthly_dict[f"{debt.name}_balance"] = debt.get_balance()
                monthly_dict[f"{debt.name}_total_paid"] = debt.get_total_paid()
                continue

            extra_payment = debt.advance_month(debt.minimum_payment + extra_payment)

            monthly_dict[f"{debt.name}_balance"] = debt.get_balance()
            monthly_dict[f"{debt.name}_total_paid"] = debt.get_total_paid()

        # Keep track of time
        monthly_dict["month"] = month
        monthly_dict["total_balance"] = _get_total_balance(debts=debts)
        monthly_dict["total_paid"] = _get_total_paid(debts=debts)

        month += 1

        df.loc[len(df)] = monthly_dict

        # Break if we've gone on too long
        if month > (12 * 100):
            break

    return df
