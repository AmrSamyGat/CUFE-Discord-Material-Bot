import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

def plot_function(function_str, x_min, x_max, num_points):
    """Plots a mathematical function given as a string.

    Args:
        function_str (str): The mathematical function as a string.
        x_min (float): The minimum value of the x-axis.
        x_max (float): The maximum value of the x-axis.
        num_points (int): The number of points to sample for the plot.

    Returns:
        bytes: The plot image data in bytes format, or None on error.
    """
    # Create a list of x-axis values with the desired number of points
    x_values = np.linspace(x_min, x_max, num_points)

    # Try to evaluate the function using the 'sympy' library
    try:
        from sympy import sympify, lambdify

        # Convert the function string to a symbolic expression
        expr = sympify(function_str)

        # Create a Python lambda function for efficient evaluation
        y_func = lambdify('x', expr)

        # Evaluate the function at the x-values
        y_values = y_func(x_values)

    except ImportError:
        print("The 'sympy' library is not installed. Using numpy's built-in functions.")

        # Attempt to evaluate the function directly using numpy
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