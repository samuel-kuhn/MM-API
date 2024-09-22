import docker, shutil, os, json
import container_information as CI
client = docker.from_env()
containers_path = os.getcwd() + "/containers/"
import logging

logger = logging.getLogger('exception_logging')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('errors.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', datefmt='%d/%b/%Y %H:%M:%S'))
logger.addHandler(file_handler)



def start(username, server_name):
    try: 
        container = client.containers.get(f'{username}.{server_name}')
        container.start()
    except Exception as exception:
        logger.exception(exception)
        return "something went wrong here"


def stop(username, server_name):
    try: 
        container = client.containers.get(f'{username}.{server_name}')
        container.stop()
    except Exception as exception:
        logger.exception(exception)
        return "something went wrong here"

    

def create(start_options:dict, environment:dict):
    image = start_options['image'] if 'image' in start_options else "itzg/minecraft-server"
    username=start_options['username']
    server_name=start_options['server_name']
    volume=[f'{containers_path}{username}/{server_name}:/data']
    name=f"{username}.{server_name}"
    port_binding={'25565/tcp': start_options['port']}
    try: 
        client.containers.create(image=image, name=name, ports=port_binding,
                environment=environment, volumes=volume)
    except Exception as exception:
        logger.exception(exception)
        return "something went wrong here"



def edit(username, server_name, start_options, environment):
    try: 
        container = client.containers.get(f'{username}.{server_name}')
        container.stop()
        container.remove()
        create(start_options=start_options, environment=environment)
    except Exception as exception:
        logger.exception(exception)
        return "something went wrong here"


def reset(username, server_name):
    stop(username, server_name)
    path = CI.full_path(username, server_name)
    try:
        shutil.rmtree(f"{path}/world")
        shutil.rmtree(f"{path}/world_nether")
        shutil.rmtree(f"{path}/world_the_end")
    except Exception as exception:
        logger.exception(exception)
        pass


def delete(username, server_name):
    try: 
        stop(username, server_name)
        container = client.containers.get(f'{username}.{server_name}')
        container.remove()
        shutil.rmtree(CI.full_path(username, server_name))
    except Exception as exception:
        logger.exception(exception)
        return "something went wrong here"


def exec(username, server_name, command):
    try: 
        container = client.containers.get(f'{username}.{server_name}')
        container.exec_run("mc-send-to-console " + command)
    except Exception as exception:
        logger.exception(exception)
        return "something went wrong here"


