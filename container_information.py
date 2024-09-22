import docker, re, os
client = docker.from_env()
containers_path = os.getcwd() + "/containers/"
def full_path(username, server_name):
    return f'{containers_path}{username}/{server_name}'
def config_path(username, server_name):
    return f'{containers_path}{username}/{server_name}/config.json'

def validate_mc_username(mc_username:str):
    pattern = r'^[a-zA-Z0-9_]{3,16}$'
    return bool(re.match(pattern, mc_username))

def get_container_config(username, server_name):
    container = client.containers.get(f'{username}.{server_name}')
    server_name = container.name.replace(f'{username}.', '')
    public_port = container.attrs['HostConfig']['PortBindings']['25565/tcp'][0]['HostPort']
    environment_list = container.attrs['Config']['Env']
    environment = dict(item.split('=', 1) for item in environment_list)
    config = {
        'username': username,
        'server_name': server_name,
        'port': public_port
    }
    config.update(environment)
    return config

def get_environment(username, server_name):
    container = client.containers.get(f'{username}.{server_name}')
    environment_list = container.attrs['Config']['Env']
    environment = dict(item.split('=', 1) for item in environment_list)
    return environment

def get_start_options(username, server_name):
    container = client.containers.get(f'{username}.{server_name}')
    port = container.attrs['HostConfig']['PortBindings']['25565/tcp'][0]['HostPort']
    start_options = {
        'username': username,
        'server_name': server_name,
        'port': port, 
        'image': container.image.tags[0]
    }
    return start_options

def disjoin_data(data:dict) -> list: 
    environment = data
    start_options = {
        'username': environment.pop('username'),
        'server_name': environment.pop('server_name'),
        'port': environment.pop('port')
    }
    environment['EULA']='TRUE'
    environment['CREATE_CONSOLE_IN_PIPE']='TRUE'
    return start_options, environment


def get_servers(username):
    running = []
    not_running = []
    containers = client.containers.list(filters={'name': f'{username}.'}, all=True)
    for container in containers:
        server_name = container.name.replace(f'{username}.', '')
        public_port = container.attrs['HostConfig']['PortBindings']['25565/tcp'][0]['HostPort']
        status = container.status
        environment_list = container.attrs['Config']['Env']
        environment = dict(item.split('=', 1) for item in environment_list)
        memory = environment['MEMORY'] if 'MEMORY' in environment else '1G'
        version = environment['VERSION']
        if status == 'running':
            running.append({
                "name": server_name,
                "status": status,
                "memory": memory,
                "port": public_port,
                "version": version
            })
        else:
            not_running.append({
                "name": server_name,
                "status": status,
                "memory": memory,
                "port": public_port,
                "version": version
            })
    
    return [running, not_running]




