import pytest
from PySide2.QtWidgets import QApplication, QPushButton
from PySide2.QtCore import Qt, QSize

from app import MainWindow 

def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def app(qapp, qtbot):
    app = MainWindow()
    
    # this prevents QMessage from showing
    app.testing_mode = True
    
    qtbot.addWidget(app)
    return app

def test_init_ui(app, qtbot):
    assert app.size() == QSize(1280, 720)
    assert app.windowTitle() == "Function Plotter"
    assert app.formula_input.placeholderText() == "Enter the formula"
    assert app.min_input.placeholderText() == "Enter the min value"
    assert app.max_input.placeholderText() == "Enter the max value"

def test_empty_min_input(app, qtbot):
    app.max_input.setText("10")
    qtbot.mouseClick(app.findChild(QPushButton, "startButton"), Qt.LeftButton)

    assert app.min_input.text() == ""
    assert app.max_input.text() == "10"
    assert app.msg.text() == "Min value is empty!"

def test_empty_max_input(app, qtbot):
    app.min_input.setText("0")
    qtbot.mouseClick(app.findChild(QPushButton, "startButton"), Qt.LeftButton)

    assert app.min_input.text() == "0"
    assert app.max_input.text() == ""
    assert app.msg.text() == "Max value is empty!"

def test_min_greater_than_max(app, qtbot):
    app.min_input.setText("10")
    app.max_input.setText("0")
    qtbot.mouseClick(app.findChild(QPushButton, "startButton"), Qt.LeftButton)
    
    assert app.min_input.text() == "10"
    assert app.max_input.text() == "0"
    assert "Min value bigger than max value:" in app.msg.text()

def test_wrong_formula_input_not_x(app, qtbot):
    app.min_input.setText("0")
    app.max_input.setText("10")
    app.formula_input.setText("c^2")
    qtbot.mouseClick(app.findChild(QPushButton, "startButton"), Qt.LeftButton)

    assert app.min_input.text() == "0"
    assert app.max_input.text() == "10"    
    assert app.msg.text() == "Error evaluating expression: name 'c' is not defined"

def test_wrong_formula_input_empty_log10(app, qtbot):
    app.min_input.setText("0")
    app.max_input.setText("10")
    app.formula_input.setText("x^2 + log10()")
    qtbot.mouseClick(app.findChild(QPushButton, "startButton"), Qt.LeftButton)

    assert app.min_input.text() == "0"
    assert app.max_input.text() == "10"    
    assert app.msg.text() == "Error evaluating expression: log10() missing 1 required positional argument: 'x'"

def test_wrong_formula_input_negative_log10(app, qtbot):
    app.min_input.setText("-5")
    app.max_input.setText("10")
    app.formula_input.setText("x^2 + log10(x)")
    qtbot.mouseClick(app.findChild(QPushButton, "startButton"), Qt.LeftButton)

    assert app.min_input.text() == "-5"
    assert app.max_input.text() == "10"    
    assert app.msg.text() == "Error evaluating expression: Negative values not allowed in log10 function"

def test_wrong_formula_input_misspelt_sqrt(app, qtbot):
    app.min_input.setText("1")
    app.max_input.setText("10")
    app.formula_input.setText("sqr(x)")
    qtbot.mouseClick(app.findChild(QPushButton, "startButton"), Qt.LeftButton)

    assert app.min_input.text() == "1"
    assert app.max_input.text() == "10"   
    assert app.msg.text() == "Error evaluating expression: name 'sqr' is not defined"

def test_wrong_formula_input_negative_sqrt(app, qtbot):
    app.min_input.setText("-5")
    app.max_input.setText("-2")
    app.formula_input.setText("sqrt(x)")
    qtbot.mouseClick(app.findChild(QPushButton, "startButton"), Qt.LeftButton)

    assert app.min_input.text() == "-5"
    assert app.max_input.text() == "-2"   
    assert app.msg.text() == "Error evaluating expression: Negative values not allowed in sqrt function"

def test_wrong_formula_input_2_arguments_sqrt(app, qtbot):
    app.min_input.setText("2")
    app.max_input.setText("9")
    app.formula_input.setText("sqrt(x,2)")
    qtbot.mouseClick(app.findChild(QPushButton, "startButton"), Qt.LeftButton)

    assert app.min_input.text() == "2"
    assert app.max_input.text() == "9"   
    assert app.msg.text() == "Error evaluating expression: sqrt() takes 1 positional argument but 2 were given"

def test_wrong_formula_input_empty(app, qtbot):
    app.min_input.setText("1")
    app.max_input.setText("10")
    qtbot.mouseClick(app.findChild(QPushButton, "startButton"), Qt.LeftButton)

    assert app.min_input.text() == "1"
    assert app.max_input.text() == "10"   
    assert app.msg.text() == "Error evaluating expression: Expression empty"

def test_plotting(app, qtbot):
    app.min_input.setText("0")
    app.max_input.setText("10")
    app.formula_input.setText("x^2")
    qtbot.mouseClick(app.findChild(QPushButton, "startButton"), Qt.LeftButton)

    # Check that there are lines other than x and y axes
    assert len(app.canvas.axes.lines) > 2

def test_clear_plot(app, qtbot):
    app.min_input.setText("0")
    app.max_input.setText("10")
    app.formula_input.setText("x^2")
    qtbot.mouseClick(app.findChild(QPushButton, "startButton"), Qt.LeftButton)
    qtbot.mouseClick(app.findChild(QPushButton, "clearButton"), Qt.LeftButton)

    # Check that there are no lines other than x and y axes
    assert len(app.canvas.axes.lines) == 2