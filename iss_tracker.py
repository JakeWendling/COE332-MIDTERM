import xmltodict
import requests
import math
import time
from geopy.geocoders import Nominatim
from typing import List
from flask import Flask, request

app = Flask(__name__)
data = None

@app.route('/comment', methods=['GET'])
def getComment() -> list:
    """
    Returns the comments from the ISS location data.

    Returns:
        list: list of strings (comments) from ISS data 
    """
    commentList = data['ndm']['oem']['body']['segment']['data']['COMMENT']
    return commentList

@app.route('/header', methods=['GET'])
def getHeader() -> dict:
    """
    Returns the header from the ISS location data.

    Returns:
        dictionary: contains header info from ISS data 
    """
    header = data['ndm']['oem']['header']
    return header

@app.route('/metadata', methods=['GET'])
def getMetadata() -> dict:
    """
    Returns the metadata from the ISS location data.

    Returns:
        dictionary: contains metadata from ISS data 
    """
    metadata = data['ndm']['oem']['body']['segment']['metadata']
    return metadata

@app.route('/now', methods=['GET'])
def getNow() -> dict:
    """
    Returns the most recent location of the ISS.

    Returns:
        dictionary: contains info about the location the ISS is floating over 
    """
    lastEpoch = getEpochs()[len(getEpochs())-1]
    now = getLocation(lastEpoch)
    return now

@app.route('/epochs/<epoch>/location', methods=['GET'])
def getLocation(epoch: str) -> dict:
    """
    Calculates the logitude, latitude, and altitude of the ISS at a given epoch.
    It then returns the location of the ISS above the surface.

    Returns:
        dictionary: contains info about the location the ISS is floating over at the given epoch 
    """
    global data
    if not data:
        return "Data not found\n", 400
    stateList = data['ndm']['oem']['body']['segment']['data']['stateVector']
    for state in stateList:
        if state['EPOCH'] == epoch:
            MEAN_EARTH_RADIUS = 6371 #km
            x = float(state['X']['#text'])
            y = float(state['Y']['#text'])
            z = float(state['Z']['#text'])
            t = time.strptime(epoch[9:-5], '%H:%M:%S')
            hrs = t[3]
            mins = t[4]
            lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
            lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 32
            alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS
            if lat > 180.0:
                lat -= 360.0
            elif lat < -180.0:
                lat += 360.0
            if lon > 180.0:
                lon -= 360.0
            elif lon < -180.0:
                lon += 360.0
            geocoder = Nominatim(user_agent='iss_tracker')
            geoloc = None
            i = 0
            while not geoloc:
                try:
                    geoloc = geocoder.reverse((lat, lon), zoom=15-i, language='en')
                except Error as e:
                    return f'Geopy returned an error - {e}', 500
                if i >= 15:
                    return {'location': {'latitude': lat, 'longitude': lon, 'altitude': alt, 'geoposition': 'over the ocean'}, 'speed': getSpeed(epoch)}
                i += 3
            return {'location': {'latitude': lat, 'longitude': lon, 'altitude': alt, 'geoposition': geoloc.raw['address']}, 'speed': getSpeed(epoch)}
    return "Error: Epoch not found\n", 400
    
@app.route('/help', methods=['GET'])
def help() -> str:
    """
    Returns a string that provides info about the different routes available in this flask app.

    Returns:
        helpString: a string that contains help info
    """
    helpString = ""
    helpString += 'Requesting data:\n'
    helpString += '  /                        Return entire data set\n'
    helpString += '  /epochs                  Return list of all Epochs in the data set\n'
    helpString += '  /epochs?                 Return modified list of Epochs given query parameters\n'
    helpString += '     limit=int&               Limits number of epochs in the list\n'
    helpString += '     offset=int               Offsets the start of the list\n'
    helpString += '  /epochs/<epoch>          Return state vectors for a specific Epoch from the data set\n'
    helpString += '  /epochs/<epoch>/speed    Return instantaneous speed for a specific Epoch in the data set\n'
    helpString += '  /epochs/<epoch>/location Return location info for a specific Epoch in the data set\n'
    helpString += '  /now                     Return location info for the most recent Epoch in the data set\n'
    helpString += '  /comment                 Return comments from the data set\n'
    helpString += '  /header                  Return header from the data set\n'
    helpString += '  /metadata                Return metadata from the data set\n'
    helpString += '  /help                    Return help text that briefly describes each route\n'
    helpString += 'Modifying data:\n'
    helpString += '  /delete-data             Delete all data from the dictionary object\n'
    helpString += '  /post-data               Reload the dictionary object with data from the web\n'
    return helpString

@app.route('/post-data', methods=['POST'])
def postData() -> dict:
    """
    Gets the nasa ISS location data and saves the data in dictionary format in the flask app.

    Returns:
        string: Message that tells the user that the data has successfuly been obtained
    """
    response = requests.get('https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    global data
    data = xmltodict.parse(response.text)
    return "Data reloaded\n"

@app.route('/delete-data', methods=['DELETE'])
def deleteData() -> str:
    """
    Deletes the data stored in the flask app

    Returns:
        string: success message
    """
    global data
    data = None
    return "Data deleted\n"

@app.route('/', methods=['GET'])
def getData() -> dict:
    """
    Gets the nasa ISS location data and returns the data in dictionary format

    Returns:
        data: The ISS coordinate data in dictionary format.
    """
    global data
    if not data:
        return "Data not found\n", 400
    return data

@app.route('/epochs', methods=['GET'])
def getEpochs() -> List[str]:
    """
    Gets the nasa ISS location data and returns the list of epochs in dictionary format
    
    Parameters:
        offset: (int) Offsets list start by this amount
        limit: (int) limits the length of the list to this amount
    Returns:
        epochs: a list of epochs(strings) for which ISS coordinate data is available.
    """
    global data
    if not data:
        return "Data not found\n", 400
    stateList = data['ndm']['oem']['body']['segment']['data']['stateVector']
    
    offset = request.args.get('offset', 0)
    try:
        offset = int(offset)
    except:
        return 'Error: offset value must be an integer\n', 400

    limit = request.args.get('limit')
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return 'Error: limit value must be an integer\n', 400
    else:
        limit = len(stateList)
    
    epochs = []
    for state in stateList:
        epochs.append(state['EPOCH'])
    return epochs[offset:limit+offset]

@app.route('/epochs/<epoch>', methods=['GET'])
def getStateVector(epoch: str) -> dict:
    """
    Gets the nasa ISS location data, 
    then returns the state vector for a given epoch, if available. 
    Otherwise returns an error message and error code.
    
    Args:
        epoch: A string representing an epoch.
        
    Returns:
        state:  The state vector for the given epoch, if available. 
    
    Raises:
        If no state vector is available for the given epoch, 
        returns an error message and a 400 status code.
    """
    global data
    if not data:
        return "Data not found\n", 400
    stateList = data['ndm']['oem']['body']['segment']['data']['stateVector']
    for state in stateList:
        if state['EPOCH'] == epoch:
            return state
    return "Error: Epoch not found\n", 400

@app.route('/epochs/<epoch>/speed', methods=['GET'])
def getSpeed(epoch: str) -> float: 
    """
    Gets the nasa ISS location data, 
    then returns the state vector for a given epoch, if available. 
    Otherwise returns an error message and error code.
    
    Args:
        epoch: A string representing an epoch.
        
    Returns:
        speed: A float representing the speed of the ISS at the given epoch, if available. 

    Raises:
        If no speed is available for the given epoch, 
        returns an error message and a 400 status code.
    """
    global data
    if not data:
        return "Data not found\n", 400
    stateList = data['ndm']['oem']['body']['segment']['data']['stateVector']
    for state in stateList:
        if state['EPOCH'] == epoch:
            x_dot = float(state['X_DOT']['#text'])
            y_dot = float(state['Y_DOT']['#text'])
            z_dot = float(state['Z_DOT']['#text'])
            speed = (x_dot**2 + y_dot**2 + z_dot**2)**.5
            return {'speed': speed, 'units': state['Z_DOT']['@units']}
    return "Error: Epoch not found\n", 400

if __name__ == '__main__':
    postData()
    app.run(debug=True, host='0.0.0.0')

    
    
