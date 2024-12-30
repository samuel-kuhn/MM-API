from flask import Flask, request, jsonify
import docker
import mc_server
from mc_server import MCServer
import responses as res

app = Flask(__name__)

client = docker.from_env()

@app.route('/ping', methods=['GET'])
def ping():
    return ('online', 200)

@app.route('/containers', methods=['GET'])
def containers():
    username = request.args.get('username', False, str)
    if not username:
        return res.UserMissing  

    servers = mc_server.get_servers(username)
    response = {
        "servers": servers,
        "total": len(servers)
    }
    return jsonify(response), 200

@app.route('/get-config', methods=['GET'])
def get_config():
    username = request.args.get('username', False, str)
    server_name = request.args.get('server_name', False, str)
    if not username:
        return res.UserMissing
    if not server_name:
        return res.ServerNameMissing
    
    config = MCServer(username, server_name).info
    return jsonify(config), 200

@app.route('/create', methods=['POST'])
def create():
    data:dict = request.get_json()
    username = data.get("username")
    server_name = data.get("server_name")
    port = data.get("PORT")
    version = data.get("VERSION")
    mode = data.get("MODE")
    memory = data.get("MEMORY")
    motd = data.get("MOTD")

    try:
        mc_server.create(username=username,
                                server_name=server_name,
                                port=port,
                                version=version,
                                mode=mode,
                                memory=memory,
                                motd=motd)
    except Exception:
        return res.clientError("something went wrong creating this server")
    return res.Success

@app.route('/edit', methods=['POST'])
def edit():
    data:dict = request.get_json()
    username = data.get("username")
    server_name = data.get("server_name")
    port = data.get("PORT")
    mode = data.get("MODE")
    memory = data.get("MEMORY")
    motd = data.get("MOTD")
    version = MCServer(username, server_name).version

    try:    
        mc_server.delete(username, server_name)
        mc_server.create(username=username,
                                server_name=server_name,
                                port=port,
                                version=version,
                                mode=mode,
                                memory=memory,
                                motd=motd)
    except Exception:
        return res.clientError("something went wrong creating this server")
    return res.Success

@app.route('/start', methods=['POST'])
def start():
    request_data: dict = request.get_json()
    username = request_data.get("username")
    server_name = request_data.get("server_name")

    if not username:
        return res.UserMissing
    if not server_name:
        return res.ServerNameMissing
    try:
        MCServer(username, server_name).start()
    except docker.errors.NotFound:
        return res.ServerNotFound
    except Exception:
        return res.UnexpectedError

    return res.Success

@app.route('/stop', methods=['POST'])
def stop():
    request_data: dict = request.get_json()
    username = request_data.get("username")
    server_name = request_data.get("server_name")

    if not username:
        return res.UserMissing
    if not server_name:
        return res.ServerNameMissing
    
    try:
        MCServer(username, server_name).stop()
    except docker.errors.NotFound:
        return res.ServerNotFound
    except Exception:
        return res.UnexpectedError

    return res.Success

@app.route('/reset', methods=['POST'])
def reset():
    request_data = request.get_json()
    message = manager.reset(**request_data)
    return ("ok", 200) if message is None else (message, 500)
    
@app.route('/delete', methods=['POST'])
def delete():
    request_data: dict = request.get_json()
    username = request_data.get("username")
    server_name = request_data.get("server_name")

    if not username:
        return res.UserMissing
    if not server_name:
        return res.ServerNameMissing
    
    try:
        mc_server.delete(username, server_name)
    except docker.errors.APIError:
        return res.UnexpectedError()
    except Exception:
        return res.UnexpectedError
    
    return res.Success

@app.route('/exec', methods=['POST'])
def exec():
    request_data = eval(request.get_json())
    if CI.validate_mc_username(request_data['command'][3:]):
        message = manager.exec(**request_data) 
    else:
        message = "Invalid username!"
    return ("ok", 200) if message is None else (message, 500)


