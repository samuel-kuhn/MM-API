from flask import Flask, request
import docker
import json
import container_manager as manager
import container_information as CI

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
    username = request.args.get('username')
    server_name = request.args.get('server_name')
    return ("get config error", 500) if (username == "" or server_name == "") else (CI.get_container_config(username, server_name), 200)

@app.route('/create', methods=['POST'])
def create():
    data:dict = eval(request.get_json())
    start_options, environment = CI.disjoin_data(data)
    message = manager.create(start_options, environment)
    return ("ok", 200) if message is None else (message, 500)

@app.route('/edit', methods=['POST'])
def edit():
    request_data = eval(request.get_json())
    new_start_options, new_environment = CI.disjoin_data(request_data)
    username=new_start_options['username']
    server_name=new_start_options['server_name']

    environment = CI.get_environment(username=username, server_name=server_name)
    environment.update(new_environment)

    start_options = CI.get_start_options(username=username, server_name=server_name)
    start_options.update(new_start_options)

    message = manager.edit(username=username, server_name=server_name, start_options=start_options, environment=environment)
    return ("ok", 200) if message is None else (message, 500)

@app.route('/start', methods=['POST'])
def start():
    request_data = request.get_json()
    username = request_data.get("username")
    server_name = request_data.get("server_name")

    if not username:
        return res.UserMissing
    if not server_name:
        return res.ServerNameMissing
    
    try:
        server = mc_server.MCServer(username=username, server_name=server_name)
    except docker.errors.NotFound:
        return res.ServerNotFound
    except Exception as exception:
        return res.UnexpectedError(exception)

    server.start()
    return res.Success

@app.route('/stop', methods=['POST'])
def stop():
    request_data = request.get_json()
    message = manager.stop(**request_data)
    return ("ok", 200) if message is None else (message, 500)

@app.route('/reset', methods=['POST'])
def reset():
    request_data = request.get_json()
    message = manager.reset(**request_data)
    return ("ok", 200) if message is None else (message, 500)
    
@app.route('/delete', methods=['POST'])
def delete():
    request_data = request.get_json()
    message = manager.delete(**request_data)
    return ("ok", 200) if message is None else (message, 500)

@app.route('/exec', methods=['POST'])
def exec():
    request_data = eval(request.get_json())
    if CI.validate_mc_username(request_data['command'][3:]):
        message = manager.exec(**request_data) 
    else:
        message = "Invalid username!"
    return ("ok", 200) if message is None else (message, 500)


