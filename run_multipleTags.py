import pozyx_reader_multipleTags
from server import app
import json

data = {
      "anchors":[],
      "remotetags":[],
      "ball_id":None
}
# Returns anchor IDs and coordinates input from the user
def anchorsInput():
            global data
            count = int(input("How many anchors do you want to save? Enter an integer: "))
            for i in range(count):
                print(f"Enter anchor no.{i+1} address, followed by a comma then enter the anchor's coordinates (x,y,z) separated by comma: ")
                anchorInput = input()
                splittedInput = anchorInput.split(",")
                data["anchors"].append({
                      "address": splittedInput[0],
                      "x": int(splittedInput[1]),
                      "y": int(splittedInput[2]),
                      "z": int(splittedInput[3])
                })
           



# Returns remote tag IDs input from the user
def remoteTagsInput():
        global data
        count = int(input("How many players do you want to track? Enter an integer: "))
        for i in range(count):
            tag= input(f"Enter remote tag no.{i+1} address: ")
            data["remotetags"].append(tag)

# Returns the ball's remote tag ID input from the user
def ballTagInput():
    global data
    ball_id = input('Enter the tag address attached to the ball: ')
    data["ball_id"] = ball_id




if __name__ == "__main__":

    
    #pozyx_reader_multipleTags.start_thread()
    app.run(
        host="0.0.0.0",
        port=5002,
        debug=False)

    