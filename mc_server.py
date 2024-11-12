from docker.models.containers import Container
import docker, os, time

containers_path = os.getcwd() + "/containers/"


client = docker.from_env()
class MCServer(Container):

    def __init__(self, username:str, server_name:str):

        self.username = username
        "user that owns the server"

        self.server_name = server_name
        "name of the minecraft server in the dashboard"

        self.full_name = self.username + '.' + self.server_name
        "name of the docker container"

        container_attrs = client.containers.get(self.full_name).attrs
        super().__init__(attrs=container_attrs, client=client)



    def __str__(self):
        return self.full_name
        
    # properties

    @property
    def image(self) -> str:
        "the image name of the container"
        return super().image.tags[0]

    @property
    def path(self):
        "path to the folder, where the servers data is stored"
        return containers_path + self.username + '/' + self.server_name
    
    @property
    def status(self) -> str:
        "current state of the server"
        return client.containers.get(self.full_name).status
    
    @property
    def port(self) -> str:
        return self.attrs['HostConfig']['PortBindings']['25565/tcp'][0]['HostPort']
    
    @property
    def env(self) -> list:
        return self.attrs['Config']['Env']
    
    # methods
    def start(self):
        super().start()
        print("\nstarting server: " + self.full_name)

    def stop(self):
        super().stop()
        print("\nstopping server: " + self.full_name)
    
    def print(self):
        print('\n' + 15 * '#' + "  " + self.full_name + "  " + 15 * '#')
        print("Status: \t" + self.status)
        print("Name: \t" + self.server_name)
        print("User: \t" + self.username)
        print("Path: \t" + self.path)
        print("Image: \t" + self.image)
        print("Port: \t" + self.port)



