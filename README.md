# Homework 05: ISS Position App Container

Scenario: You have found an abundance of interesting positional and velocity data for the International Space Station (ISS). It is a challenge, however, to sift through the data manually to find what you are looking for. 

This Flask application is used for querying and returning interesting information from the ISS data set. It returns the most recent position and velocity data of the ISS.

The data used in this program can be found at [this link](https://spotthestation.nasa.gov/trajectory_data.cfm). This data is found in an xml file and contains a dictionary of header data and position/velocity vectors of the ISS every four minutes. It contains the date and time, X, Y, and Z, and X, Y, and Z velocities at each epoch (in km and km/s respectively).

## Installation

Install this project by cloning the repository, making the scripts executable
For example:

```bash
git clone git@github.com:JakeWendlingUT/COE332.git
cd COE332
cd homework05
chmod u+x iss_tracker.py
```

## Creating the Docker Container
### Using the prebuilt container
Enter the following to pull and run the prebuilt container:
```bash
docker pull jakewendling/iss_tracker:hw05
```
### Building a Docker image using the Dockerfile
Enter the following to build the container using the Dockerfile contained in this repository:
```bash
docker build . -t jakewendling/iss_tracker:hw05
```
## Running the Code

This code has three functions:
1. Return the entire data set in dictionary format.
2. Return a list of the epochs/times when positional data of the ISS was taken.
3. Return a dictionary of the position and velocity vectors at a provided epoch.
4. Return the speed of the ISS at a given epoch.

To perform these functions:

### Starting the Flask app
First start the Flask app:
```bash
docker run -it --rm  -p 5000:5000 jakewendling/iss_tracker:hw05
```

### Requesting Data
In a separate terminal, you can request the data.

To load the data into the app, run the following:
```bash
curl -X POST localhost:5000/post-data
```
This will allow the other requesting routes to function.

To delete the data from the app, run the following
```bash
curl -X DELETE localhost:5000/delete-data
```
Doing this will cause all of the other requesting routes to fail.

#### To request the entire dataset:
```bash
curl localhost:5000
```
However, it is recommended to output this data to a file instead of the terminal given its large size:
```bash
curl localhost:5000 --output <filename>
```
#### To request the list of epochs:
```bash
curl localhost:5000/epochs
```
This will return something similar to the following:
```bash
["2023-048T12:00:00.000Z","2023-048T12:04:00.000Z","2023-048T12:08:00.000Z",...
```
#### To request the positional data for a given epoch:
(you can copy one of the epochs given in the previous command)
```bash
curl localhost:5000/epochs/<epoch>
```
Example usage:
```bash
curl localhost:5000/epochs/"2023-063T11:59:00.000Z"
```
This will give the position and velocity vectors of the ISS at the given epoch.
```bash
{"EPOCH":"2023-063T11:59:00.000Z","X":{"#text":"2511.5681106...
```
#### To request the speed at a given epoch:
```bash
curl localhost:5000/epochs/<epoch>/speed
```
Example usage:
```bash
curl localhost:5000/epochs/"2023-063T11:59:00.000Z"/speed
```
Which gives:
```bash
7.662273068417691 km/s
```