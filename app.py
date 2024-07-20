import sys
import math
import ast
import numpy as np
from PySide2.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QMessageBox
from PySide2.QtGui import Qt, QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.figure import Figure

# define a custom canvas class that inherits from FigureCanvas (a widget)
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        # the subplot this app uses
        self.axes = fig.add_subplot()

        # calls FigureCanvas
        super().__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.testing_mode = False
        self.init_UI()

    def init_UI(self):
        '''
            Initiates the window title, size and icon then adds\n
            the UI layout and the matplot next to each other in a\n
            QHBoxLayout, clears the plot then applies the style.
        '''
        self.setWindowTitle("Function Plotter")
        self.setFixedSize(1280, 720)
        self.setWindowIcon(QIcon("icons/icon.png"))

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QHBoxLayout(main_widget)
        layout.addWidget(self.create_UI_layout(), 1)
        layout.addWidget(self.create_plot_layout(), 1)

        # focuses on formula input field (looks better)
        self.formula_input.setFocus()
    
        self.clear_plot()
        self.apply_styles()
        self.show()

    def create_UI_layout(self):
        '''
            Creates QWidget and places all the buttons on, then creates\n
            input fields using this widget.
        '''
        button_widget = QWidget()
        button_widget.setObjectName("buttonWidget")

        start_button = QPushButton("Start", button_widget)
        start_button.setObjectName("startButton")
        start_button.clicked.connect(self.input_parser)
        start_button.move(520, 610)

        clear_button = QPushButton("Clear", button_widget)
        clear_button.setObjectName("clearButton")
        clear_button.move(20, 610)
        clear_button.clicked.connect(self.clear_all)

        self.create_input_fields(button_widget)

        return button_widget
    
    def create_input_fields(self, parent):
        '''
            Creates the 3 input fields used in this app along with\n
            their labels and hardcoded positions.
        '''
        formula_label = QLabel("Enter Formula:", parent)
        formula_label.setObjectName("formulaLabel")
        formula_label.move(120, 140)

        self.formula_input = QLineEdit(parent)
        self.formula_input.setObjectName("formulaInput")
        self.formula_input.move(120, 180)
        self.formula_input.resize(400, 100)
        self.formula_input.setPlaceholderText("Enter the formula")

        min_label = QLabel("Enter Min:", parent)
        min_label.setObjectName("minMaxLabel")
        min_label.move(20, 360)

        self.min_input = QLineEdit(parent)
        self.min_input.setObjectName("minInput")
        self.min_input.move(20, 380)
        self.min_input.resize(200, 50)
        self.min_input.setPlaceholderText("Enter the min value")

        max_label = QLabel("Enter Max:", parent)
        max_label.setObjectName("minMaxLabel")
        max_label.move(420, 360)

        self.max_input = QLineEdit(parent)
        self.max_input.setObjectName("maxInput")
        self.max_input.move(420, 380)
        self.max_input.resize(200, 50)
        self.max_input.setPlaceholderText("Enter the max value")

    def create_plot_layout(self):
        '''
            Creates QWidget and makes the matplotlib canvas.
        '''
        plot_widget = QWidget()
        plot_widget.setObjectName("plotWidget")
        plot_layout = QVBoxLayout(plot_widget)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        plot_layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_layout.addWidget(self.toolbar)

        return plot_widget

    def input_parser(self):
        '''
            Parses the input from min and max then attempts to plot.\n
            Will throw a ValueError if min and max cannot be parsed to floats.
        '''
        try:
            if(self.min_input.text() == ''):
                raise ValueError("Min value is empty!")
            elif(self.max_input.text() == ''):
                raise ValueError("Max value is empty!")
            
            min_val = float(self.min_input.text())
            max_val = float(self.max_input.text())

            if(min_val > max_val):
                raise ValueError(f"Min value bigger than max value: ({min_val} > {max_val})")
            
            print(f"Min: {min_val}, Max: {max_val}")
            self.plot(min_val, max_val)
        except ValueError as e:
            self.show_error_message(str(e))
            print(f"Error parsing input: {e}")

    def str_eval(self, x_value):
        '''
            String evaluation using built-in eval().\n
            Will throw an Exception if there is an error with the string.
        '''
        expression = self.formula_input.text()
        if(expression == ''):
            str = "Error evaluating expression: Expression empty"
            print(str)
            raise Exception(str)
        expression = expression.replace('^', '**')

        def log10(x):
            if(x < 0):
                raise ValueError("Negative values not allowed in log10 function")
            else:
                return math.log10(x)
        
        def sqrt(x):
            if(x < 0):
                raise ValueError("Negative values not allowed in sqrt function")
            else:
                return math.sqrt(x)


        safe_names = {"x": x_value, "log10": log10, "sqrt": sqrt}

        # shamelessly stolen from stackoverflow 
        # basically parses formula in an abstract tree and rejects names that arent safe
        try:
            parsed = ast.parse(expression)
            for node in ast.walk(parsed):
                if isinstance(node, ast.Name) and node.id not in safe_names:
                    raise NameError(f"Error evaluating expression: name '{node.id}' is not defined")
        except SyntaxError as e:
            str = f"Error evaluating expression: Syntax error - {e}"
            print(str)
            raise ValueError(str)


        # to handle log10 & sqrt safely and stop builtins injections
        try:
            return eval(expression, {"__builtins__": None}, safe_names)
        except Exception as e:
            str = f"Error evaluating expression: {e}"

            # makes it look cleaner and hides internal workings
            str = str.replace("MainWindow.str_eval.<locals>.sqrt()","sqrt()")
            str = str.replace("MainWindow.str_eval.<locals>.log10()","log10()")

            print(str)
            raise Exception(str)

    def plot(self, min_val, max_val):
        '''
            Computes x and y and tries to plot the data.\n
            Will show an error message if string evaluation was unsuccessful.
        '''
        print("Plotting")
        step = 0.001
        x = np.arange(min_val, max_val + step, step).tolist()

        # lim -> 0
        if(0 in x):
            x[x.index(0)] = 0.0000000001
        
        try:
            y = [self.str_eval(x_val) for x_val in x]
        except Exception as e:
            self.show_error_message(str(e))
            return
        
        self.clear_plot()
        self.canvas.axes.plot(x, y)
        self.canvas.draw()

    def show_error_message(self, error_text):
        '''
            Shows an informative error QMessageBox unless in testing mode.
        '''
        self.msg = QMessageBox()
        self.msg.setWindowIcon(QIcon("icons/error-icon.png"))
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setText(error_text)
        self.msg.setWindowTitle("Error")
        self.msg.setStandardButtons(QMessageBox.Ok)
        if(not self.testing_mode):
            self.msg.exec_()

    def clear_all(self):
        '''
            Clears plot and all input fields.
        '''
        self.clear_plot()
        self.formula_input.clear()
        self.min_input.clear()
        self.max_input.clear()

    def clear_plot(self):
        '''
            Clears the plot by redrawing the axes, setting their limits,\n
            and adjusting the labeling.
        '''
        ax = self.canvas.axes
        ax.clear()

        # the 0.1s are to make the grid appear fully
        ax.set_xlim(-20, 20.1)
        ax.set_ylim(-20.1, 20)
        ax.axhline(y=0, color='black', linewidth=1)
        ax.axvline(x=0, color='black', linewidth=1)

        # removes top and right borders(looks better)
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')

        # draws numbers on axes
        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')

        # enables the grid 
        ax.grid(True, which='both')

        # x and y are equal in size
        ax.set_aspect('equal', adjustable='box')
        self.canvas.draw()

    def keyPressEvent(self, event):
        '''
            Detects when the enter key is pressed and starts plotting
        '''
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            # Trigger the input parser method
            self.input_parser()
        
        # Call the base class implementation if needed
        super().keyPressEvent(event)

    def apply_styles(self):
        '''
            Pure CSS styling for the front end.
        '''
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QWidget#buttonWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 10px;
            }
            QLabel#formulaLabel {
                font-size: 26px;
                color: #333333;
            }
            QLabel#minMaxLabel {
                font-size: 16px;
                color: #333333;
            }
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                background-color: #ffffff;
                color: #333333;
            }
            QLineEdit#formulaInput {
                font-size: 36px;
            }
            QLineEdit#minInput, QLineEdit#maxInput {
                font-size: 16px;
            }
            QPushButton {
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 5px;
            }
            QPushButton#startButton {
                background-color: #4CAF50;
            }
            QPushButton#startButton:hover {
                background-color: #45a049;
            }
            QPushButton#clearButton {
                background-color: #f44336;
            }
            QPushButton#clearButton:hover {
                background-color: #da190b;
            }
            QWidget#plotWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 10px;
            }
        """)

def main():
    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()