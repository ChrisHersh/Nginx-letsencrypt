import argparse
import create_cert
import renew


# Entry point, determines if it should renew or create certs
def main(parser):
    args = process_args(parser)

    if args.renew:
        renew()
    else:
        create_cert(args.email)


# Create the args for the help and later processing
def create_args():
    parser = argparse.ArgumentParser(description='Automatically obtain certs for subdomains in nginx configs')

    parser.add_argument('--renew', dest='renew', action='store_true',
                        help='If this flag is set the script will run in renew mode. '
                             'Renew mode will issue a renew command instead of register, '
                             'as such it will not automatically scrape the nginx config. '
                             "Certbot's renew will use the same configuration"
                             "as the previous registration command")

    parser.add_argument('--email', dest='email', action='store',
                        default='', type=str,
                        help='This is the email to be used in the registration process, '
                             'if left blank the user will be prompted to enter it later.\n')
    return parser


# Parse the args into a variable for later use
def process_args(parser):
    args = parser.parse_args()
    return args


# Create the args then start the main method
if __name__ == "__main__":
    args_parser = create_args()
    main(args_parser)
