

from pint import UnitRegistry
#from uncertainties import ufloat
ureg = UnitRegistry()
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import inspect


class Parameter(float):
    """
    This class extends the float object by adding tolerance bounds, streamlining sensitivity analysis

    See this link for float extension hints:
    https://stackoverflow.com/questions/35943789/python-can-a-subclass-of-float-take-extra-arguments-in-its-constructor"""

    def __new__(cls, lower_limit, upper_limit, force_value=None):

        if force_value:
            nominal = force_value
        else:
            nominal = (lower_limit + upper_limit) / 2

        return super().__new__(cls, nominal)

    def __init__(self, lower_limit, upper_limit, force_value=None):
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def roll_dice(self):
        return random.uniform(self.lower_limit, self.upper_limit)



class BaseModel:


    def randomize_parameters(self):
        """Search for all Parameter types and run build in function to 'roll the dice' """

        list_of_parameters = [name for name in dir(self) if type(getattr(self, name)).__name__ == 'Parameter']

        for name in list_of_parameters:
            this_param = getattr(self, name)
            setattr(self, name, Parameter(this_param.lower_limit,
                                          this_param.upper_limit,
                                          force_value=this_param.roll_dice()))

        return list_of_parameters

    def simulate_a_model(self, model, num_simulations=1000):

        list_of_dfs = []

        for simulation_number in range(0, num_simulations):

            list_of_parameters = self.randomize_parameters()

            results_dict = {}

            for name in list_of_parameters:
                this_parameter = getattr(self, name)
                results_dict[name] = [this_parameter]

            results_dict['Model_Output'] = [model()]


            list_of_dfs.append(pd.DataFrame(results_dict))
        #TODO [Mark] set all Parameter types back to nominal (would need to add capabiity to Parameter
        return pd.concat(list_of_dfs, ignore_index=True)

    #TODO: [Mark] add OLS capability: https://stackoverflow.com/questions/19991445/run-an-ols-regression-with-pandas-data-frame

    @staticmethod
    def visualize_sensitivity(results_df, result_name=""):

        parameter_columns = [col for col in results_df.columns if col != "Model_Output"]

        num_cols = 3
        num_rows = math.ceil((len(parameter_columns) + 1) / num_cols)
        f, a = plt.subplots(num_rows, num_cols)
        row_idx = 0
        col_idx = 0
        for idx, parameter_name in enumerate(parameter_columns):
            a[row_idx][col_idx].plot(results_df[parameter_name], results_df.Model_Output, '.')
            a[row_idx][col_idx].set_xlabel(parameter_name)
            if col_idx == 0:
                a[row_idx][col_idx].set_ylabel("Model Output")

            col_idx = col_idx + 1

            if col_idx >= num_cols:
                col_idx = 0
                row_idx = row_idx + 1

        a[-1][-1].hist(results_df.Model_Output)
        a[-1][-1].set_xlabel('Histogram of Model Output')
        a[-1][-1].set_ylabel('counts')

        plt.tight_layout(pad=0.14, w_pad=0.1, h_pad=1.0)
        plt.show()

class SimplePhysicalModel(BaseModel):

    def __init__(self):

        # Bucket subsystem parameters
        self.bucket_length = Parameter(1, 2)
        self.bucket_width = Parameter(2, 3)
        self.bucket_height = Parameter(4, 5)

        # Cable subsystem parameters
        self.cable_diameter = Parameter(.1, .15)
        self.cable_length = Parameter(6, 6.5)

    def calculate_cable_stress(self):

        LIQUID_DENSITY = 1.5 #some unit
        GRAVITATION_ACCELERATION = 9.8
        bucket_mass = self.calculate_bucket_volume() * LIQUID_DENSITY
        cable_force = bucket_mass * GRAVITATION_ACCELERATION
        cable_area = np.pi * (self.cable_diameter/2)**2

        return cable_force / cable_area

    def calculate_bucket_volume(self):

        return self.bucket_length * self.bucket_height * self.bucket_width

    def calculate_bucket_area(self):

        middle_area = 4 * self.bucket_length * self.bucket_height
        end_area = 2 * (self.bucket_height * self.bucket_width)

        return middle_area + end_area


if __name__ == "__main__":

    m = SimplePhysicalModel()
    print(f"The nominal bucket volume is {m.calculate_bucket_volume()}")
    print(f"The nominal bucket area is {m.calculate_bucket_area()}")
    print(f"The nominal cable stress is {m.calculate_cable_stress()}")

    results_df = m.simulate_a_model(m.calculate_cable_stress, num_simulations=3000)
    m.visualize_sensitivity(results_df)

