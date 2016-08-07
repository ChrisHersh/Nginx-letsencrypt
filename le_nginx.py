import re
from os import listdir
from os.path import isfile, join
import subprocess
import argparse


# Add any server_name entries here that you do not want to register a cert for
# _ is excluded by default to prevent the certbot command from failing
exclude_list = ['_']


args = {}


def main(parser):
    process_args(parser)

    if(args.renew):
        renew()
    else:

        nginx_path = "/etc/nginx/sites-enabled"
        config_files = [join(nginx_path, f) for f in listdir(nginx_path) if isfile(join(nginx_path, f))]

        server_names = get_all_config_server_names(config_files)


        if len(server_names) > 100:
            print("Sadly Let's Encrypt doesn't support more than 100 domains per cert, and this script doesn't support multiple certs yet\nHave a good day without your certs")
            exit(0)

        stop_nginx()
        cert_cmd = build_cert_command()
        obtain_cert(cert_cmd)
        start_nginx()


def renew():



def create_args():
    parser = argparse.ArgumentParser(description='Automatically obtain certs for subdomains in nginx configs')
    parser.add_argument('--renew', dest='renew', action='store_true',
            help='If this flag is set the script will run in renew mode. Renew mode will issue a renew command instead of register, as such it will not automatically scrape the nginx config. When run normally this script will produce a txt file with the subdomains it finds, without this file this mode will fail.\n')

    parser.add_argument('--email', dest='email', action='store',
            default='', type=str,
            help='This is the email to be used in the registration process, if left blank the user will be prompted to enter it later.\n')
    return parser
    

def process_args(parser):
    args = parser.parse_args()


def stop_nginx():
    try:
        print("Stopping nginx for standalone webserver")
        execute(["sudo", "nginx", "-s", "stop"])
    except:
        print("Could not stop nginx. One possible cause is nginx was already stopped")


def start_nginx():
    try:
        print("Attempting to start nginx again")
        execute(["sudo", "nginx"])
    except:
        print("Could not start nginx. Please run `sudo nginx` manually")


def obtain_cert(cert_cmd):
    try:
        print("Attempting to obtain certs")
        print("Using following command: {}".format(''.join(elem+" " for elem in command_string_list)))
        execute(cert_cmd)
    except:
        print("Something happened while trying to obtain certificate. You can try to run the above command to try to find out why")


# Builds the command array for the cert bot command 
def build_cert_command(server_names):
    email = get_user_email()

    command_string_list= ["sudo", "certbot", "certonly","--standalone", "--expand", "--agree-tos", "--email", email]

    server_names_command = []
    for name in server_names:
        server_names_command.append("-d")
        server_names_command.append(name)

    command_string_list += server_names_command
    return command_string_list


def get_user_email():
    email = ""
    if email == "":
        email = input("We need your email to continue:\n")


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


def get_all_config_server_names(config_names):
    server_names = []

    for name in config_names:
        server_names = server_names + get_config_server_names(name)
        
    #flatten list of server names and remove any in the exclusion list
    server_names = [name for name in server_names if name not in exclude_list]

    with open("server_names.txt") as f:
        for x in server_names:
            f.write(x)

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
    parser = create_args()
    main(parser)
