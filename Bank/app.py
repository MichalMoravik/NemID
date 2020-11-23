# run.py is a module running this application
# app variable exists in the package, inside __init__.py class
from nemidbank import app
import os
# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port = int(os.environ.get('PORT', 33507))
)
