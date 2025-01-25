from flask import Flask, request, jsonify
from flask_cors import CORS
import docker
import mc_server
from mc_server import MCServer
import responses as res

app = Flask(__name__)

CORS(app)

client = docker.from_env()

@app.route('/ping', methods=['GET'])
def ping():
    return ('Pong', 200)

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
        MCServer(username, server_name).remove()
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
    request_data: dict = request.get_json()
    username = request_data.get("username")
    server_name = request_data.get("server_name")

    if not username:
        return res.UserMissing
    if not server_name:
        return res.ServerNameMissing

    MCServer(username, server_name).reset()    
    return res.Success    
        
    
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

@app.route('/op', methods=['POST'])
def op():
    request_data: dict = request.get_json()
    username = request_data.get("username")
    server_name = request_data.get("server_name")
    mc_user = request_data.get("mc_user")

    if not username:
        return res.UserMissing
    if not server_name:
        return res.ServerNameMissing

    exec_result = MCServer(username, server_name).send_to_console("op " + mc_user)
    if exec_result.exit_code != 0:
        return res.UnexpectedError(exec_result.output)
    return res.Success

