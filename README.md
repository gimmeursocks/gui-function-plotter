# Function Plotter GUI Application

This is a Python GUI application that lets users plot mathematical function of `x`. Automated testing and input validation ensures the user input is correct. The GUI is built using PySide2 and the plots are generated using Matplotlib.
Currently supports these operators + - / * ^ log10() sqrt() and is immune to command injection.

## Dependencies

- Python < 3.11
- PySide2
- matplotlib
- numpy
- pytest-qt

## Installation

1. Clone the repo:
```
git clone https://github.com/gimmeursocks/gui-function-plotter.git
cd gui-function-plotter
```
2. Install dependencies:
```
pip install PySide2 matplotlib numpy
```

## Usage

1. Run program:
```
python app.py
```
2. Enter the formula, min & max and press Enter or click Start


## Automated Tests

1. Install testing dependencies:
```
pip install pytest pytest-qt
```

2. Run the tests:
```
pytest
```

## Examples
<img src='snapshots/main.png'>

### Working Examples
<img src='snapshots/working_1.png'>
<img src='snapshots/working_2.png'>
<img src='snapshots/working_3.png'>
<img src='snapshots/working_4.png'>
<img src='snapshots/working_5.png'>

### Wrong Examples
<img src='snapshots/wrong_1.png'>
<img src='snapshots/wrong_2.png'>
<img src='snapshots/wrong_3.png'>
<img src='snapshots/wrong_4.png'>
<img src='snapshots/wrong_5.png'>
<img src='snapshots/wrong_6.png'>
