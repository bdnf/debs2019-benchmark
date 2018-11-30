import requests
import json
import pandas as pd
import os
NUMBER_OF_SCENES = 50


def host_url(host, path):
    return "http://" + host + path

# def get_scenes():
#     response = requests.get(host_url('/scenes/'))
#     if (response.ok):
#         data = json.loads(response.content)
#         print(data)
#         return data
    # return requests.get(host_url('/scenes/'))


def get_scene(host, number):
    response = requests.get(host_url(host, '/scene/'+str(number)))
    if (response.ok):
        data = response.json() #json.loads(response.content)
        print(data)
        return data
    # else: return response


def post_answer(host, scene, payload):
    headers = {'Content-type': 'application/json'}
    response = requests.post(host_url(host, '/prediction/scene/'+str(scene)), json = payload, headers=headers)

    print('Response status is: ', response.status_code)
    if (response.status_code == 201):
        return {'status': 'success', 'message': 'updated'}
    if (response.status_code == 400):
        print({'message': '''A scene {} already exist.
                If you want to update your value try to use PUT request'''
                .format(scene)})


if __name__ == "__main__":
    print('ENV is ', os.getenv('SERVER_CONTAINER_NAME', default='benchmark-server'))
    print('Getting the scenes for predictions...')
    host = os.getenv('SERVER_CONTAINER_NAME', default='benchmark-server')
    if host is None:
        print('Error reading Server address!')
    # Here is an automated script for getting all scenes
    # and submitting prediction for each of them
    # you may change it to fit your needs

    for i in range(1, NUMBER_OF_SCENES+1):

        # making GET request
        data = get_scene(host, i)

        # example of reconstruction json payload from GET request into DataFrame
        reconstructed_scene = pd.read_json(data['scene'], orient='records')
        # DO YOUR PREDICTIONS HERE
        # return the result in format in plain json:
        # for example:
        example_result = {'car': 1, 'armchair': 2}
        # after making the result in correct form you need to submit it
        # to the corresponding scene
        # via POST request
        post_answer(host, scene=i, payload=example_result)

    print('Submission was done successfully!')
