from docker.models.containers import Container
import docker, os, re, shutil

client = docker.from_env()

class MCServer(Container):

    def __new__(cls, username: str, server_name: str):
        full_name = username + '.' + server_name

        image = client.containers.get(full_name).image.tags[0]

        if image.split(':')[0] != 'itzg/minecraft-server':
            return None 
        
        return super().__new__(cls)

    def __init__(self, username: str, server_name: str):

        self.username = username
        "User that owns the server"

        self.server_name = server_name
        "Name of the Minecraft server in the dashboard"

        self.full_name = self.username + '.' + self.server_name
        "Name of the docker container"

        container_attrs = client.containers.get(self.full_name).attrs
        super().__init__(attrs=container_attrs, client=client)

    def __str__(self):
        return self.full_name
        
    # properties

    @property
    def image(self) -> str:
        "The image name of the container"
        return super().image.tags[0]

    @property
    def path(self):
        "Path to the folder, where the server's data is stored"
        return os.getcwd() + "/containers/" + self.username + '/' + self.server_name
    
    @property
    def status(self) -> str:
        "Current state of the server"
        return super().status
    
    @property
    def port(self) -> str:
        "Port binding for the container"
        return self.attrs['HostConfig']['PortBindings']['25565/tcp'][0]['HostPort']
    
    @property
    def env(self) -> list:
        "Environment variables of the container"
        return self.attrs['Config']['Env']
    
    @property
    def env_dict(self) -> dict:
        "Environment variables of the container"
        return dict(item.split('=', 1) for item in self.env)
    
    @property
    def motd(self) -> str:
        "Message of the day"
        return self.env_dict["MOTD"]
    
    @property
    def version(self) -> str:
        "Minecraft version"
        return self.env_dict["VERSION"]
    
    @property
    def mode(self) -> str:
        "Game mode"
        return self.env_dict["MODE"]
    
    @property
    def memory(self) -> str:
        "Memory allocated to server"
        return self.env_dict["MEMORY"]
    
    @property
    def type(self) -> str:
        "Type of Minecraft server. For example, ``vanilla``"
        return self.env_dict["TYPE"]
    
    @property
    def info(self) -> dict:
        """
        The `dict` contains:
        - NAME: Server name,
        - STATUS: Status of the container. For example, running or exited,
        - MEMORY: Ram allocated to server,
        - PORT: Public port of the server,
        - VERSION: Minecraft Version,
        - MODE: Gamemode,
        - MOTD: Message of the day
        """
        return {
            "NAME": self.server_name,
            "STATUS": self.status,
            "MEMORY": self.memory,
            "PORT": self.port,
            "VERSION": self.version,
            "MODE": self.mode,
            "MOTD": self.motd
        }
    
    # methods
    def start(self):
        super().start()
        print("\nStarting server: " + self.full_name)

    def stop(self):
        super().stop()
        print("\nStopping server: " + self.full_name)

    def reset(self):
        """
        Deletes world data.
        """
        self.stop()
        print("\nDeleting world data: " + self.path)
        try:
            shutil.rmtree(f"{self.path}/world")
            shutil.rmtree(f"{self.path}/world_nether")
            shutil.rmtree(f"{self.path}/world_the_end")
        except FileNotFoundError:
            pass

    def send_to_console(self, command: str):
        exec_result = self.exec_run("rcon-cli " + command)
        print("\nExecuting command: " + command)
        print(exec_result.output)
        return exec_result
    
    def print(self):
        print('\n' + 15 * '#' + "  " + self.full_name + "  " + 15 * '#')
        print("Status: \t" + self.status)
        print("Name: \t" + self.server_name)
        print("User: \t" + self.username)
        print("Path: \t" + self.path)
        print("Image: \t" + self.image)
        print("Port: \t" + self.port)


def get_containers(username:str) -> list[MCServer]:
    containers = []
    for container in client.containers.list(all=True):
        if bool(re.match(fr'^{re.escape(username)}\..*', container.name)):
            mc_server = MCServer(*container.name.split('.'))

            if mc_server != None:
                containers.append(mc_server)
    return containers

def get_servers(username:str) -> list[dict]:
    """
    Returns a list of all servers of a given user.

    Returns:
        A `list` containing the `MCServer.info` object of all servers.

    """
    servers = []
    for container in get_containers(username):
        servers.append(container.info)
    return servers

def create(username: str, 
           server_name: str, 
           port: int,
           version: str,
           mode: str,
           memory: int,
           motd: str):
    
    image = "itzg/minecraft-server"
    username=username
    server_name=server_name
    container_path = os.getcwd() + "/containers/" + username + '/' + server_name

    volume=[f'{container_path}:/data']
    container_name=f"{username}.{server_name}"
    port_binding={'25565/tcp': port}

    environment = {
        'MODE': mode,
        'VERSION': version,
        'MEMORY': memory,
        'MOTD': motd,
        'EULA': 'TRUE'
    }
    client.containers.create(image=image, name=container_name, ports=port_binding,
            environment=environment, volumes=volume)


def delete(username: str, server_name: str):
    server = MCServer(username, server_name)
    server.stop()
    server.remove()
    shutil.rmtree(server.path)
