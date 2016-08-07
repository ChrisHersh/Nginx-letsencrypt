import re
from os import listdir
from os.path import isfile, join
from common import execute


# Add any server_name entries here that you do not want to register a cert for
# _ is excluded by default to prevent the certbot command from failing
exclude_list = ['_']


# Starts process of creating the cert
def create_cert(email):
    nginx_path = "/etc/nginx/sites-enabled"
    config_files = [join(nginx_path, f) for f in listdir(nginx_path) if isfile(join(nginx_path, f))]

    server_names = get_all_config_server_names(config_files)

    if len(server_names) > 100:
        print("Sadly Let's Encrypt doesn't support more than 100 domains per cert,"
              " and this script doesn't support multiple certs yet\n"
              "Have a good day without your certs")
        exit(0)

    stop_nginx()
    cert_cmd = build_cert_command(server_names, email)
    obtain_cert(cert_cmd)
    start_nginx()


# Stops nginx so certbot can obtain the certs using the standalone mode
def stop_nginx():
    try:
        print("Stopping nginx for standalone webserver")
        execute(["sudo", "nginx", "-s", "stop"])
    except:
        print("Could not stop nginx. "
              "One possible cause is nginx was already stopped")


# Starts nginx again after attempting to obtain the certbot
def start_nginx():
    try:
        print("Attempting to start nginx again")
        execute(["sudo", "nginx"])
    except:
        print("Could not start nginx. Please run `sudo nginx` manually")


# Attempts to obtain the cert using certbot
def obtain_cert(cert_cmd):
    try:
        print("Attempting to obtain certs")
        print("Using following command: {}"
              .format(''.join(elem+" " for elem in cert_cmd)))
        execute(cert_cmd)
    except:
        print("Something happened while trying to obtain certificate. "
              "You can try to run the above command to try to find out why")


# Builds the command array for the cert bot command
def build_cert_command(server_names, email):
    email = get_user_email(email)

    command_string_list = ["sudo", "certbot", "certonly", "--standalone", 
            '--keep-until-expiring', "--expand", "--agree-tos", 
            "-q", "--email", email]

    server_names_command = []
    for name in server_names:
        server_names_command.append("-d")
        server_names_command.append(name)

    command_string_list += server_names_command
    return command_string_list


# checks if the email was already given, asks for it if not
def get_user_email(email):
    if email == "":
        email = input("We need your email to continue:\n")
    return email


# Get all server_names from all config files
def get_all_config_server_names(config_names):
    server_names = []

    for name in config_names:
        server_names = server_names + get_config_server_names(name)

    # flatten list of server names and remove any in the exclusion list
    server_names = [name for name in server_names if name not in exclude_list]

    return server_names


# Get all server_names within a single config file
def get_config_server_names(config_name):

    names = []
    server_name_regex = r"\s*server_name.+;"

    with open(config_name) as config:
        for line in config.readlines():
            if re.match(server_name_regex, line):
                names = names + get_server_names(line)
    return names


# Get server_names on a single line
def get_server_names(line):
    line = line.replace("server_name", "")
    line = line.replace(";", "")
    line = re.sub(r"\s+", " ", line).strip()
    line = line.split(" ")
    return line
