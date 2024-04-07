import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

def plot_function(function_str, x_min, x_max, num_points):
    try:
        x_values = np.linspace(x_min, x_max, num_points)

        try:
            from sympy import sympify, lambdify

            expr = sympify(function_str)

            y_func = lambdify('x', expr)

            y_values = y_func(x_values)

        except ImportError:
            print("The 'sympy' library is not installed. Using numpy's built-in functions.")

            try:
                y_values = eval(function_str)
            except SyntaxError as e:
                print(f"Error parsing function: {e}")
                return None

        # Create the plot
        fig, ax = plt.subplots()  # Create a figure and axis
        plt.plot(x_values, y_values)

        # Set labels and title
        plt.xlabel("x", loc="right")
        plt.ylabel("f(x)", loc="top")
        plt.title(f"Plot of f(x) = {function_str}")
        
        ax.spines['left'].set_position('center')
        ax.spines['bottom'].set_position('center')
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.set_xlim([-abs(x_max), abs(x_max)])

        # Convert the plot to a PNG image in memory
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Close the plot and clear memory
        plt.close()

        return buffer
    except Exception as e:
        return None