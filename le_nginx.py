import re
from os import listdir
from os.path import isfile, join
import subprocess

def main():
    nginx_path = "/etc/nginx/sites-enabled"
    config_files = [join(nginx_path, f) for f in listdir(nginx_path) if isfile(join(nginx_path, f))]

    server_names = get_all_config_server_names(config_files)

    print(server_names)
    if len(server_names) > 100:
        print("Sadly Let's Encrypt doesn't support more than 100 domains per cert, and this script doesn't support multiple certs yet\nHave a good day without your certs")
        exit(0)

    email = ""
    if email == "":
        email = input("We need your email to continue:\n")

    print("Stopping nginx for standalone webserver")
    execute(["sudo", "nginx", "-s", "stop"])

    command_string_list = ["sudo", "certbot", "certonly","--standalone", "--agree-tos", "--email", email]

    server_names_command = []
    for name in server_names:
        server_names_command.append("-d")
        server_names_command.append(name)

    command_string_list += server_names_command
    print("Attempting to obtain certs")
    print("Using following command: {}".format(''.join(elem+" " for elem in command_string_list)))
    execute(command_string_list)

    print("Attempting to start nginx again")
    execute(["sudo", "nginx"])
    

    #print(get_all_config_server_names(config_files)) 


def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    print(popen.stdout.read())
    #istdout_lines = iter(popen.stdout.readline, "")
    #for stdout_line in stdout_lines:
    #    yield stdout_line

    popen.stdout.close()
    return_code = popen.wait()
    if return_code != 0:
        raise subprocess.CalledProcessError(return_code, cmd)


def flatten_list(lumpy_list):
    flat_list = [item for sublist in lumpy_list for item in sublist]
    return flat_list

def get_all_config_server_names(config_names):
    server_names = []

    for name in config_names:
        server_names = server_names + get_config_server_names(name)

    return server_names

def get_config_server_names(config_name):

    names = []
    servername_regex = r"\s*server_name.+;"

    with open(config_name) as config:
        for line in config.readlines():
            if re.match(servername_regex, line):
                names = names + get_server_names(line)
    return names


def get_server_names(line):
    line = line.replace("server_name", "")
    line = line.replace(";", "")
    line = re.sub(r"\s+", " ", line).strip()
    line = line.split(" ")
    return line


if __name__ == "__main__":
    main()
