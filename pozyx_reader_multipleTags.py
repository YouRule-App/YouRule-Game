from pypozyx import *
import threading
import shared_state_multipleTags
import time
import json
from statistics import median



anchors = []
    # DeviceCoordinates(anchor address, 1=anchor or 2=tag, Coordinates(x,y,z))
    

remoteTags_ID = []

tag_data = {}
alpha = 0.6
window_size = 5


def start():
    global anchors
    global remoteTags_ID
    global alpha
    global tag_data

    """"
    Need to first find the serial port that connects the master tag to the laptop(e.g. COM3), and 
    create an object of pozyx to begin reading the coordinates
    """
    serialport = get_first_pozyx_serial_port()
    print(f"detected port: {serialport}")
    pozyx = PozyxSerial(serialport)

    # Load json file containing the anchor tags IDs and coordinates, remote tag IDs and ball tag ID
    with open("pozyx_reader_config.json","r") as file:
        data = json.load(file)
    
    for anchor in data["anchors"]:
        anchors.append(DeviceCoordinates(int(anchor["address"],16), 1, Coordinates(anchor["x"],anchor["y"],anchor["z"])))
    
    for tag in data["remotetags"]:
        remoteTags_ID.append(int(tag["address"],16))
    
    for tag in data["ball_id"]:
        remoteTags_ID.append(int(tag["address"],16))
    
    for tag in remoteTags_ID:
        pozyx.clearDevices(tag)
        for anchor in anchors:
            pozyx.addDevice(anchor, tag) #Now we add all anchors info to the remote tag
    
    # The variable that will save each remote tag's coordinates
    position = Coordinates()
    
    while True:
        for tag_id in remoteTags_ID:
            # For each tag, read its 3D position and save it in position variable
            reading = pozyx.doPositioning(
                position, 
                dimension=POZYX_3D , 
                algorithm=POZYX_POS_ALG_UWB_ONLY,
                remote_id=tag_id
            )
            # If the reading is successful, save it inside the variable of another Python file called "shared_state_multipleTags".
            # This method was implemented to eliminate race condition, where the script writes and the app reads to and from the positions variable 
            # at the same time.
            if reading == POZYX_SUCCESS:
                with shared_state_multipleTags.lock:
                    shared_state_multipleTags.positions[hex(tag_id)] = {
                        "x":position.x,
                        "y":position.y,
                        "z":position.z,
                    }
                
            else:
                print("Positioning failed")



def filterReadingsEMA(positions, tag_id):
    # Filter readings incoming from a tag using Exponential Moving Average function (EMA) on each dimension
    # EMA = alpha * median(reading) + (1-alpha) * EMA
    global alpha
    if tag_id not in tag_data:
        tag_data[tag_id] = {
            "x_readings":[],
            "y_readings":[],
            "z_readings":[],
            "ema_x":0,
            "ema_y":0,
            "ema_z":0,
        }
    data = tag_data[tag_id]
    data["x_readings"].append(positions.x)
    data["y_readings"].append(positions.y)
    data["z_readings"].append(positions.z)
    if len(data["x_readings"]) > 3:
        data["x_readings"].pop(0)
        data["y_readings"].pop(0)
        data["z_readings"].pop(0)
    data["ema_x"] = alpha * median(data["x_readings"]) +  (1 - alpha) * data["ema_x"]
    data["ema_y"] = alpha * median(data["y_readings"]) +  (1 - alpha) * data["ema_y"]
    data["ema_z"] = alpha * median(data["z_readings"]) +  (1 - alpha) * data["ema_z"]

    return data["ema_x"],data["ema_y"],data["ema_z"]


    

def start_thread():
    thread = threading.Thread(target=start, daemon= True)
    thread.start()
