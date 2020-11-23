# run.py is a module running this application
# app variable exists in the package, inside __init__.py class
from nemidskat import app

# Run app
if __name__ == "__main__":
    app.run(port=5555, debug=True)