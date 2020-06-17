from pint import UnitRegistry
ureg = UnitRegistry()

import random

from base_model import Parameter


class QuantityExtra(ureg.Quantity):
    "like a Parameter, with units"

    def __new__(cls, value, units, extra=""):
        return super().__new__(cls, value, units)

    def __init__(self, value, units, extra=""):
        self.extra = extra



class UnitParameter(ureg.Quantity):

    "like a Parameter, with units"
    def __new__(cls, lower_limit, upper_limit, units):

        value = (lower_limit + upper_limit) / 2

        return super().__new__(cls, value, units)

    def __init__(self, lower_limit, upper_limit, units):

        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def roll_dice(self):
        return random.uniform(self.lower_limit, self.upper_limit)





if __name__ == "__main__":

    print("---Simply adding an attribute works---")
    qe_one = QuantityExtra(1, ureg.meters, extra="hello")
    qe_two = QuantityExtra(1000, ureg.mm, extra="hello")

    print(f"qe_one = {qe_one}")
    print(f"qe_two = {qe_two}")
    print(f"qe_one + qe_two = {qe_one + qe_two}")

    print("---Now, use UnitParameter, which does math to calculate value")

    up_one = UnitParameter(0, 2, ureg.meters)
    up_two = UnitParameter(0, 4000, ureg.mm)

    print(f"up_one = {up_one}")
    print(f"up_two = {up_two}")
    stuff = up_one * up_two #when I do math, erros happen
    print(f"stuff = {stuff}")



