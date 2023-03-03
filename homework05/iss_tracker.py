import xmltodict
import requests
from typing import List
from flask import Flask, request

app = Flask(__name__)
data = None

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
            return f"{str(speed)} {state['Z_DOT']['@units']}\n"
    return "Error: Epoch not found\n", 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    
