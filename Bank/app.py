# run.py is a module running this application
# app variable exists in the package, inside __init__.py class
from nemidbank import app

# Run app
if __name__ == "__main__":
    app.run(port=7777, debug=True)
