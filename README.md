# NemID

The project is a composition of 5 Flask (Python) Rest API servers and Azure functions. All parts are dockerized and represent 6 different Docker containers.
The API endpoints in the containers can be hit via the Ocelot gateway implemented in C#. 

![diagram](/diagram.jpg)

## Start containers locally

1. run docker-compose file <code>docker-compose up</code>
2. run the gateway - direct to the folder with gateway code and run <code>dotnet run</code>
3. try out the endpoints using your rest client (Insomnia/Postman)

## Start without containers locally

1. navigate to the server you want to start, create a Python virtual environment and install packages
1. run <code>python3 app.py</code>
2. download Azure CLI and run Azure functions <code>func start --python</code>. Alternatively you can run it via Azure's extension on VSCode
3. try out the endpoints using your rest client (Insomnia/Postman)

