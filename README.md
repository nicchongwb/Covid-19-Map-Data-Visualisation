# Covid Map Mercator Projection
Simple map data visualisation application written in Python Flask. Takes in data set of COVID cases with geographical information and plot on a map of Singapore.

## Installation

There are some dependencies that you need to install in order to run this project.

The first thing would be the Flask framework which you can install by going to the project directory via command 
line and typing this:

Anaconda environment usage: Before installing any APIs to anaconda, ensure that you create a new anaconda environment in Anaconda Navigator and install them there instead of base environment.



```bash
pip install flask
conda install -c anaconda flask
```

The next thing would be the Pandas framework:

```bash
pip install pandas
conda install pandas
```

```
pip install bokeh
conda install bokeh
```

```
pip install pandas-bokeh
conda install -c patrikhlobil pandas-bokeh
```

With that, we should be able to run the program now.
=======
Following that, we will need the pandas-bokeh dependency that handles the plotting of interactive graphs:

```bash
pip install pandas-bokeh
```

We also need to install the xlrd framework since we are reading xlsx files:

```bash
pip install xlrd
```

With that, we should be able to run the program now.

## Execution

In order to view the web application, we need to set the FLASK_APP by typing this into
the command line:

```bash
set FLASK_APP=main.py
```

You then run the program by typing:

```bash
flask run
```

Proceed to your web browser and type in localhost:5000 to access the web application.
