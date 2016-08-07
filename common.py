import subprocess


# This file is intended to hold any common
#   functions that both create_cert and renew will use


# executes the command that was passed in
def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    print(popen.stdout.read())

    popen.stdout.close()
    return_code = popen.wait()
    if return_code != 0:
        raise subprocess.CalledProcessError(return_code, cmd)