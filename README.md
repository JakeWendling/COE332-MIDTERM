# Midterm Project: ISS Position App Container

Scenario: You have found an abundance of interesting positional and velocity data for the International Space Station (ISS). It is a challenge, however, to sift through the data manually to find what you are looking for. 

This Flask application is used for querying and returning interesting information from the ISS data set. It allows the user to request recent position and velocity data of the ISS, along with other miscellaneous information found in the data set.

The data used in this program can be found at [this link](https://spotthestation.nasa.gov/trajectory_data.cfm). This data is found in an xml file and contains a dictionary of header data and position/velocity vectors of the ISS every four minutes. The position vectors contain the date, time, and position and velocity in the three coordinate directions (X, Y, Z) at each epoch.

## Installation

Install this project by cloning the repository:
```bash
git clone git@github.com:JakeWendling/ISS-Tracker.git
```

## Creating the Docker Container
### Using the prebuilt container
Enter the following to pull the prebuilt container:
```bash
docker pull jakewendling/iss_tracker:midterm
```
### Building a Docker image using the Dockerfile
Enter the following to build the container using the Dockerfile contained in this repository:
```bash
docker build . -t jakewendling/iss_tracker:midterm
```
## Running the Code

This code has several functions:
1. Return the entire data set in dictionary format.
2. Return a list of the epochs/times when positional data of the ISS was taken.
3. Return a dictionary of the position and velocity vectors at a provided epoch.
4. Return a dictionary of information about the location of the ISS at a given epoch.
5. Return the speed of the ISS at a given epoch.
6. Return various other info found in the ISS data.

To perform these functions:

### Starting the Flask app
First start the Flask app:
```bash
docker-compose up
```

### Requesting Data

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
#### To request the geoposition of the ISS:
```bash
curl localhost:5000/epochs/<epoch>/location
```
To request the most recent geoposition:
```bash
curl localhost:5000/now
```
Example usage:
```bash
curl localhost:5000/epochs/"2023-063T11:59:00.000Z"/location
```
or
```
curl localhost:5000/now
```
Which gives something similar to the following:
```bash
{
  "location": {
    "altitude": 426.493361256541,
    "geoposition": "over the ocean",
    "latitude": 3.693612400678767,
    "longitude": 67.77071661260686
  },
  "speed": {
    "speed": 7.6603442162552815,
    "units": "km/s"
  }
}
```
#### To Request other info:
The ISS posistion dataset contains other info, including comment, header, and metadata.
Comment:
```bash
curl localhost:5000/comment
```
This returns:
```bash
[
  "Units are in kg and m^2",
  "MASS=473291.00",
  "DRAG_AREA=1421.50", ...
```
Header:
```bash
curl localhost:5000/header
```
This returns:
```bash
{
  "CREATION_DATE": "2023-067T21:02:49.080Z",
  "ORIGINATOR": "JSC"
}
```
Metadata:
```bash
curl localhost:5000/metadata
```
This returns:
```bash
{
  "CENTER_NAME": "EARTH",
  "OBJECT_ID": "1998-067-A", ...
```

#### Reloading the data:
If the application has been open for an extended period of time, you can reload the data by running the following:

To delete the data from the app, run the following
```bash
curl -X DELETE localhost:5000/delete-data
```
Doing this will cause all of the other requesting routes to fail.

To load the data back into the app, run the following:
```bash
curl -X POST localhost:5000/post-data
```
This will make sure the app has the most recent data.