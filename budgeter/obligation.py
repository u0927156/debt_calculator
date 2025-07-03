from budgeter.obligation_types import ObligationType


class Obligation:

    def __init__(
        self,
        name: str,
        amount: float,
        obligation_type: ObligationType = ObligationType.LOAN,
        interest_rate: float = 0.0,
        fixed_costs: float | None = None,
        minimum_payment: float | None = None,
    ):

        # Set non-optional parameters
        self.amount: float = amount
        self.name = name
        self.obligation_type = obligation_type
        self.minimum_payment = minimum_payment

        # Error checks
        if interest_rate < 0:
            raise ValueError("Interest rates must be positive.")

        if self.obligation_type != ObligationType.LOAN and fixed_costs is not None:
            raise ValueError("Only loans can have fixed costs.")

        self.interest_rate: float = interest_rate
        self.fixed_costs: float | None = fixed_costs

        self.is_finished: bool = False

        # Totals for record keeping
        self.total_interest = 0
        self.total_costs = 0
        self.total_paid = 0

        if self.obligation_type == ObligationType.LOAN:
            self._balance = self.amount

        elif self.obligation_type == ObligationType.SAVINGS:
            self._balance = 0

    def calculate_interest(self):
        return self._balance * ((self.interest_rate / 100) / 12)

    def get_balance(self):
        return round(self._balance, 2)

    def get_total_interest_paid(self):
        return round(self.total_interest, 2)

    def get_total_costs_paid(self):
        return round(self.total_costs, 2)

    def get_total_paid(self):
        return round(self.total_paid, 2)

    def advance_month(self, payment: float | None = None) -> float:
        """
        Calculates the new balances for an obligation. Returns the amount of left-over payment which
        is usually 0.

        Parameters
        ----------
        payment : float
            The amount to pay towards the obligation

        Returns
        -------
        float
            Any left-over payment
        """
        if self.obligation_type == ObligationType.LOAN:

            if payment is None:
                payment = self.minimum_payment
            if self.is_finished:
                return payment

            interest_amount = self.calculate_interest()

            self.total_interest += interest_amount
            amount_possible_to_pay = self._balance + interest_amount

            if self.fixed_costs is not None:
                self.total_costs += self.fixed_costs
                amount_possible_to_pay += self.fixed_costs

            if payment > amount_possible_to_pay:
                self.is_finished = True
                self._balance = 0
                self.total_paid += amount_possible_to_pay
                return payment - amount_possible_to_pay
            else:
                self._balance += interest_amount

                if self.fixed_costs is not None:
                    self._balance += self.fixed_costs

                self._balance -= payment
                self.total_paid += payment

            return 0

        elif self.obligation_type == ObligationType.SAVINGS:

            # Handle interest
            interest_amount = self.calculate_interest()
            self.total_interest += interest_amount

            self._balance += interest_amount

            if self.is_finished:
                return payment
            # This case is if interest takes care of the rest of the goal
            elif self._balance >= self.amount:
                self.is_finished = True
                return payment
            elif self._balance + payment >= self.amount:
                self.is_finished = True

                amount_to_pay = self.amount - self._balance
                remaining_payment = payment - amount_to_pay

                self.total_paid += amount_to_pay

                self._balance = self.amount
                return remaining_payment
            else:
                self._balance += payment
                self.total_paid += payment

            return 0

    def __str__(self):
        return f"{self.name}: amount: {self.amount}, apr: {self.interest_rate}"

    def __repr__(self):
        return f"{self.name}: amount: {self.amount}, apr: {self.interest_rate}"
