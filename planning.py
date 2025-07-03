# %%
from budgeter.obligation import Obligation
from budgeter.obligation_types import ObligationType

import plotly.express as px
import plotly.graph_objects as go

# %%

student_loan = Obligation("student_loan", 50000, ObligationType.LOAN, 5, 60)

month = 1
while not student_loan.is_finished:

    student_loan.advance_month(900)
    print(f"Month {month}: Remaining Balance: ${student_loan.get_balance()}")

    month += 1

years_taken = int(month / 12)
remaining_months_taken = month % 12

print(f"It took {years_taken} years and {remaining_months_taken} months")
print(
    f"Total Paid: ${student_loan.get_total_paid()}, Interest: ${student_loan.get_total_interest_paid()}, "
    + f"Fixed Costs: ${student_loan.get_total_costs_paid()}"
)

# %%
# Scenario Constants
PAYMENT_AMOUNT = 6000

student_loan_parameters = {
    "name": "student_loan",
    "amount": 50000,
    "obligation_type": ObligationType.LOAN,
    "interest_rate": 5,
    "fixed_costs": 60,
}
apartment_down_payment_parameters = {
    "name": "apartment",
    "amount": 24800,
    "obligation_type": ObligationType.SAVINGS,
    "interest_rate": 0.1,
}


def make_figure(
    figure_title, months, student_loan_balances, apartment_down_payment_balances
) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=months, y=student_loan_balances, name="Student Loan"))
    fig.add_trace(
        go.Scatter(x=months, y=apartment_down_payment_balances, name="Down Payment")
    )

    fig.update_layout(
        title=figure_title,
        xaxis_title="Months",
        yaxis_title="Balance Amount",
        legend_title="Balances",
    )
    return fig


# %%
# Scenario 1 - Payoff student loan first

student_loan = Obligation(**student_loan_parameters)
aparment_down_payment = Obligation(**apartment_down_payment_parameters)

month = 1
student_loan_balances = []
apartment_down_payment_balances = []
months = []


while not (student_loan.is_finished & aparment_down_payment.is_finished):
    remaining_payment = student_loan.advance_month(PAYMENT_AMOUNT)
    aparment_down_payment.advance_month(remaining_payment)

    student_loan_balances.append(student_loan.get_balance())
    apartment_down_payment_balances.append(aparment_down_payment.get_balance())
    months.append(month)
    month += 1


scenario_1_figure = make_figure(
    "Pay Off Student Loan First",
    months,
    student_loan_balances,
    apartment_down_payment_balances,
)
scenario_1_figure.show()

scenario_1_student_loan_sum = student_loan.get_total_paid()
print(
    f"Total Time: {month} months. ${scenario_1_student_loan_sum} was the total paid to student loans"
)

# %%
# Scenario 2 - Split 2/3 to 1/3


def perform_ratio_experiment(scenario_name, split):
    student_loan = Obligation(**student_loan_parameters)
    aparment_down_payment = Obligation(**apartment_down_payment_parameters)

    month = 1
    student_loan_balances = []
    apartment_down_payment_balances = []
    months = []

    month_down_payment_is_ready = None
    student_loan_payment_amt = PAYMENT_AMOUNT * (split)
    apartment_down_payment_amt = PAYMENT_AMOUNT * (1 - split)

    student_loan_carry_over = 0
    apartment_carry_over = 0

    while not (student_loan.is_finished & aparment_down_payment.is_finished):

        # Don't assume one will finish before the other
        this_month_student_loan_payment = (
            student_loan_payment_amt + apartment_carry_over
        )
        this_month_apartment_down_payment = (
            apartment_down_payment_amt + student_loan_carry_over
        )

        # Reset carry over amounts
        student_loan_carry_over = 0
        apartment_carry_over = 0

        student_loan_carry_over = student_loan.advance_month(
            this_month_student_loan_payment
        )
        apartment_carry_over = aparment_down_payment.advance_month(
            this_month_apartment_down_payment
        )

        student_loan_balances.append(student_loan.get_balance())
        apartment_down_payment_balances.append(aparment_down_payment.get_balance())

        if month_down_payment_is_ready is None and aparment_down_payment.is_finished:
            month_down_payment_is_ready = month

        months.append(month)
        month += 1

    scenario_figure = make_figure(
        f"{scenario_name} Split",
        months,
        student_loan_balances,
        apartment_down_payment_balances,
    )
    scenario_figure.show()
    scenario_student_loan_sum = student_loan.get_total_paid()
    print(
        f"Total Time: {month} months. ${scenario_student_loan_sum} was the total paid to student loans"
    )
    print(f"The down payment was ready on month {month_down_payment_is_ready}")

    return scenario_1_student_loan_sum


perform_ratio_experiment("2/3", 2 / 3)


# %%
perform_ratio_experiment("1/3", 1 / 3)
perform_ratio_experiment("1/3", 1 / 3)

# %%


def get_mortgage_costs_and_time(monthly_payment, starting_balance=631960):
    mortgage = Obligation(
        "mortgage", starting_balance, ObligationType.LOAN, 4.750, 1000
    )

    month = 1
    while not mortgage.is_finished:

        mortgage.advance_month(monthly_payment)
        # print(f"Month {month}: Remaining Balance: ${mortgage.get_balance()}")

        month += 1

    years_taken = int(month / 12)
    remaining_months_taken = month % 12

    return (
        years_taken,
        remaining_months_taken,
        mortgage.get_total_paid(),
        mortgage.get_total_interest_paid(),
        mortgage.get_total_costs_paid(),
    )


normal_payment = get_mortgage_costs_and_time(4602)
payment_500 = get_mortgage_costs_and_time(4602 + 500)
payment_1000 = get_mortgage_costs_and_time(4602 + 1000)
payment_2000 = get_mortgage_costs_and_time(4602 + 2000)
payment_4000 = get_mortgage_costs_and_time(4602 + 4000)
payment_6000 = get_mortgage_costs_and_time(4602 + 6000)


# %%

print(f"Normal Payment: {normal_payment[0]} years {normal_payment[1]} months")
print(f"500 Extra: {payment_500[0]} years {payment_500[1]} months")
print(f"1000 Extra: {payment_1000[0]} years {payment_1000[1]} months")
print(f"2000 Extra: {payment_2000[0]} years {payment_2000[1]} months")
print(f"4000 Extra: {payment_4000[0]} years {payment_4000[1]} months")
# %%
# Time difference


def print_time_difference(payment_1, payment_2, category):
    years_diff = payment_1[0] - payment_2[0]
    months_diff = payment_1[1] - payment_2[1]

    if months_diff < 0:
        years_diff -= 1
        months_diff = -months_diff

    print(f"{category} saved: {years_diff} years {months_diff} months saved")
    pass


print_time_difference(normal_payment, payment_500, "500 dollars per month")
print_time_difference(normal_payment, payment_1000, "1000 dollars per month")
print_time_difference(normal_payment, payment_2000, "2000 dollars per month")
print_time_difference(normal_payment, payment_4000, "4000 dollars per month")
print_time_difference(normal_payment, payment_6000, "6000 dollars per month")


# %%
# Cost Difference
def print_cost_differences(payment_1, payment_2, category):
    print(
        f"{category} saves: ${payment_1[2] - payment_2[2]:,.2f} total, "
        + f"${payment_1[3] - payment_2[3]:,.2f} in interest, "
        + f"${payment_1[4] - payment_2[4]:,.2f} in fixed costs"
    )


print_cost_differences(normal_payment, payment_500, "500 dollars")
print_cost_differences(normal_payment, payment_1000, "1000 dollars")
print_cost_differences(normal_payment, payment_2000, "2000 dollars")
print_cost_differences(normal_payment, payment_4000, "4000 dollars")
print_cost_differences(normal_payment, payment_6000, "6000 dollars")

# %%
normal_payment = get_mortgage_costs_and_time(4602)
initial_payment_10000 = get_mortgage_costs_and_time(
    4602, starting_balance=631960 - 10000
)
initial_payment_20000 = get_mortgage_costs_and_time(
    4602, starting_balance=631960 - 20000
)

print_cost_differences(normal_payment, initial_payment_10000, "10000 dollars now")
print_time_difference(normal_payment, initial_payment_10000, "10000 dollars now")

print_cost_differences(normal_payment, initial_payment_20000, "20000 dollars now")
print_time_difference(normal_payment, initial_payment_20000, "20000 dollars now")
