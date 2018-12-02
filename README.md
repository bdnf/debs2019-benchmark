# DEBS 2019 Challenge Example Kit

This repository contains instructions and example of basic benchmark system that you can run locally, and test your solutions early on.

Please use this repository as a template for your work. The final evaluation benchmark system will be similar to one used here.

We use Docker Compose to help you reduce the complexity for integration with the HOBBIT system.
Please read the instructions below, to get insight how you can get started.

## About this repository

This repository contains project structure for your implementation.
`Dataset` folder should contain your training datasets `in.csv` and `out.csv`.
`Client_app` folder for your implementation.
`docker-compose.yml` - defines the services that run together(HTTP-client against our Benchmarking system).
`Dockerfile.client` - defines the steps needed to build container with your prediction system (if decided to use another language than Python, you will need to redefine this file appropriately).


## Before you start

Place your `out.csv` and `in.csv` files in `/dataset` folder for the benchmark system to be able to use them.

Make sure you have Docker Engine and Docker Compose installed.
You may use the official link below for downloading:
[Download Docker Engine](https://docs.docker.com/get-started/#prepare-your-docker-environment
https://docs.docker.com/compose/install/#install-compose)

Check your installation:
```
  $ docker --version
  $ docker-compose --version
```

## How to get started

You need to implement your solution as HTTP-client. Example client, written in Python, is already provided in `/client_app` folder.
You may use this code as it is, we already implemented all basic functionality that you may need. Just plug in your prediction system and you are ready to submit the final solution.
However you are free to use any language that suits your needs.

1. Clone this repository
2. Use the project structure as it is. Place all your code in /client_app folder, and your .csv files into `/dataset` folder.
3. Implement your HTTP-client as RESTful web service (you may see an example implementation in `client_app.py`).

    >Basically this means, that you client should request data via GET method, and submit your answer >via POST method.
    >Use `/scene/` path for your requests.
    >For each GET request you will receive a new chunk of data with a specific scene.
    >After you submit your answer to this scene via POST request - new scene will be available to you >via new GET request.
    >After all 50 scenes were submitted to our benchmark system your client should stop upon seeing >`404` status code. Now you ready for the next step.

4. Add your dependencies to `Dockerfile.client`. If you use Python, check `line 12`, and add dependencies that you may need for your client system to run.
5. To start the evaluation of your solution run:
    ```
    $ docker-compose up
    ```
6. Check the logs of `'benchmark-server'` Docker container to see details of your run.
    Use this command:
      ```
      $ docker logs benchmark-system
      ```
7. Make changes to your system if needed.
After any change to your system or HTTP-client, please run these commands:
      ```
      $ docker-compose down
      ```
    This will stop the previous run of benchmark system. Then run:
      ```
      $ docker-compose up --build
      ```
    To rebuild with changes you made.

`Note!` If you willing to use another language for your development you need to change contents of Dockerfile.client to support language of your choice.
