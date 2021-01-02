# run.py is a module running this application
# app variable exists in the package, inside __init__.py class
from bank import app

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 81)
