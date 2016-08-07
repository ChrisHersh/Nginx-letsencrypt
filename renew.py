from common import execute


# For completeness sake, method to issue a renew to certbot
def renew():
    renew_cmd = build_renew_command()
    execute(renew_cmd)


# Build the fairly simple renew command for nginx
def build_renew_command():
    renew_commands = ['sudo', 'certbot', 'renew', '--standalone',
                      '--pre-hook', 'sudo nginx -s stop',
                      '--post-hook', 'sudo nginx']

    return renew_commands

