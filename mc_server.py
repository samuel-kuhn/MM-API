from docker.models.containers import Container
import docker, os

containers_path = os.getcwd() + "/containers/"

client = docker.from_env()
class MCServer(Container):

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
        return containers_path + self.username + '/' + self.server_name
    
    @property
    def status(self) -> str:
        "Current state of the server"
        return client.containers.get(self.full_name).status
    
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
        - name: Server name,
        - status: Status of the container. For example, running or exited,
        - memory: Ram allocated to server,
        - port: Public port of the server,
        - version: Minecraft Version
        """
        return {
            "name": self.server_name,
            "status": self.status,
            "memory": self.memory,
            "port": self.port,
            "version": self.version
        }
    
    # methods
    def start(self):
        super().start()
        print("\nStarting server: " + self.full_name)

    def stop(self):
        super().stop()
        print("\nStopping server: " + self.full_name)
    
    def print(self):
        print('\n' + 15 * '#' + "  " + self.full_name + "  " + 15 * '#')
        print("Status: \t" + self.status)
        print("Name: \t" + self.server_name)
        print("User: \t" + self.username)
        print("Path: \t" + self.path)
        print("Image: \t" + self.image)
        print("Port: \t" + self.port)



