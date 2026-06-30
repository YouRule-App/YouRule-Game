# Server is ran using Flask
from flask import Flask,jsonify,render_template,request, send_from_directory
from flask_cors import CORS
import shared_state_multipleTags
import json
import os
import shutil
app = Flask(__name__)
CORS(app)
HTML_FOLDER = os.path.abspath(os.path.dirname(__file__)) 
field =None


# Displays positions readings on the location "/positions"
@app.route("/positions")
def getPositionsFromTag():
    with shared_state_multipleTags.lock:
        return jsonify(shared_state_multipleTags.positions)


@app.route('/reader_config')
def readerConfig():
    with open("pozyx_reader_config.json") as f:
        return jsonify(json.load(f))

@app.route('/reader_config', methods=["POST"])
def save_reader_config():
    with open("pozyx_reader_config.json","w") as f:
        json.dump(request.get_json(), f, indent=2)
    with open("restart.flag","w") as f:
        f.write("restart")
    return jsonify({"status": "ok"})
    
@app.route('/zones')
def list_zones():
    if not os.path.isdir("Zones"):
        return jsonify([])
    name = [n for n in os.listdir("Zones")
    if os.path.isdir(os.path.join("Zones",n)) ]
    return jsonify(name)

@app.route("/zone/<name>")
def get_zone(name):
    path = os.path.join("Zones",name,"zone.json")
    if not os.path.exists(path):
        return jsonify({"error":"zone file not found"}), 404
    with open(path) as f:
        return jsonify(json.load(f))

@app.route("/zone/<name>", methods = ["POST"])
def save_zone(name):
    folder = os.path.join("Zones", name)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder,"zone.json"),"w") as f:
        json.dump(request.get_json(), f, indent=2)
    return jsonify({"status": "ok"})

@app.route("/rename/<type>",methods=["POST"])
def edit_zone_audio(type):
    print("went through edit zone/audio")
    data = request.get_json()
    for entry in data.values():
        if not entry['new_name'].strip():
            continue
        old_path = os.path.join(type,entry['old_name'])
        new_path = os.path.join(type,entry['new_name'])
        if old_path == new_path:
            print("file have same name")
            continue
        if not os.path.exists(old_path):
            print("old path doesnt exist")
            return jsonify({'error':'a folder was not found'}),400
        if os.path.exists(new_path):
            print("new path already taken")
            return jsonify({'error':'a folder already exists'}),400
        os.rename(old_path,new_path)
    print("Looped through the list of zones/audios")
    return jsonify({'status':'ok'})
    
@app.route("/zone/<name>", methods=["DELETE"])
def delete_zone(name):
    folder = os.path.join("Zones", name)
    if not os.path.isdir(folder):
        return jsonify({"error":"file not found"}), 404
    shutil.rmtree(folder)
    return jsonify({"status":"ok"})


@app.route("/audios")
def list_audios():
    if not os.path.isdir("Audios"):
        return jsonify([])
    name = [n for n in os.listdir("Audios")
    if os.path.isdir(os.path.join("Audios",n)) ]
    return jsonify(name) 

@app.route("/audio/<name>")
def get_audio(name):
    path = os.path.join("Audios",name)
    print("Looking for folder:" , path)
    print("abs path: ",os.path.abspath(path))
    print("Exists? ", os.path.isdir(path))
    print("content: ", os.listdir(path))
    if not os.path.isdir(path):
        
        return jsonify({"error":"audio folder not found"}), 404
    files = [f for f in os.listdir(path) if f.lower().endswith(('.mp3','.wav','.ogg','.webm'))]
    if not files:
        return jsonify({"error":"no audios inside folder"}), 404
    return send_from_directory(os.path.abspath(path), files[0])


@app.route("/audio/<name>",methods = ["POST"])
def save_audio(name):

    if "file" not in request.files:
        return jsonify({"error": "no file uploaded"}), 400
    file = request.files["file"]
    type = os.path.splitext(file.filename)[1].lower()
    if type not in ('.mp3','.wav','.ogg','.webm'):
        return jsonify({"error":"file is not of audio type"})
    folder = os.path.join("Audios",name)
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder,"sound"+type))
    return jsonify({"status":"ok"})

@app.route("/audio/<name>", methods=["DELETE"])
def delete_audio(name):
    folder = os.path.join("Audios", name)
    print("folder:",folder)
    if not os.path.isdir(folder):
        return jsonify({"error":"file not found"}), 404
    shutil.rmtree(folder)
    return jsonify({"status":"ok"})

@app.route("/game", methods = ["POST"])
def save_game():
    data = request.get_json()
    gameName = data.get("game_name","")
    gameFile = data.get("content","")

    folder = os.path.join("Games",gameName)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder,"game.txt"),"w") as f:
        f.write(gameFile)
    return jsonify({"status":"ok"})

@app.route("/game/<name>")
def get_game(name):
    path = os.path.join("Games",name,"game.txt")
    if not os.path.exists(path):
        return jsonify({"error":"file not found"}), 404
    with open(path) as f:
        content = f.read()
    return jsonify({"content":content})

@app.route("/games")
def list_games():
    if not os.path.isdir("Games"):
        return jsonify([])
    return jsonify([n for n in os.listdir("Games") if os.path.isdir(os.path.join("Games",n))])

@app.route("/game/<name>",methods=["DELETE"])
def delete_game(name):
    folder = os.path.join("Games",name)
    if not os.path.isdir(folder):
        return jsonify({"error":"file not found"}), 404
    shutil.rmtree(folder)
    return jsonify({"status":"ok"})

@app.route("/records/<name>", methods=["POST"])
def save_record(name):
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400
    frames = data.get("frames", [])


    def fmt_elapsed(ms):
        minutes = int(ms // 60000)
        seconds = int((ms % 60000) // 1000)
        millis  = int(ms % 1000)
        return f"{minutes:02d}:{seconds:02d}:{millis:03d}"   # MM:SS:mmm


    by_tag = {}
    for frame in frames:
        t = frame.get("t")
        for tag, pos in frame.get("positions", {}).items():
            by_tag.setdefault(tag, []).append((t, pos.get("x"), pos.get("y")))


    lines = []
    for tag, entries in by_tag.items():
        lines.append(f"Player {tag}:")
        lines.append(f"(coordinates recorded in cm precision)")
        for (t, x, y) in entries:
            lines.append(f"  {fmt_elapsed(t)}: (x: {x}, y: {y})")
        lines.append("")


    text = "\n".join(lines)
    folder = os.path.join("Records", name)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "record.txt"), "w") as f:
        f.write(text)
    return jsonify({"status": "ok"})




@app.route('/') 
def index(): 
    return send_from_directory(HTML_FOLDER, 'anchor_setup.html') 

@app.route('/<path:filename>') 
def serve_file(filename): 
    return send_from_directory(HTML_FOLDER, filename) 