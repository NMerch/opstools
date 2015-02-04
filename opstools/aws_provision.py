#!/usr/bin/python
__author__ = 'Nadir Merchant'

import sys
import time
import getopt
import textwrap
import boto.ec2

from boto.exception import EC2ResponseError
from opstools.conf import settings


def main(*argv):

    # Ensure required settings are present
    validate_settings()

    key = settings.settings['AWS_KEY_ID']
    secret_key = settings.settings['AWS_SECRET_KEY']
    region = settings.settings['REGION']

    # Default values
    name = None
    persist_storage = False
    seed = 1
    zone = None
    _bootstrap = settings.settings['callback']
    security_groups = settings.settings['base_security_group']
    instance_size = settings.settings['default_instance_size']
    num_of_instances = settings.settings['num_of_instances']
    ssh_key = settings.settings['default_ssh_key']
    ami = settings.settings['ami']


    try:
        opts, args = getopt.getopt(argv[0], "bhs:g:n:x:a:v:z:k:")
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    # Connect to AWS
    conn = boto.ec2.connect_to_region(region,
                                      aws_access_key_id=key,
                                      aws_secret_access_key=secret_key)

    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        if opt == '-s':
            if validate_instance_size(arg):
                instance_size = arg
        if opt == '-g':
            groups = validate_group(conn, arg)
            security_groups.extend(groups)
        if opt == '-n':
            name = arg
        if opt == '-x':
            num_of_instances = int(arg)
        if opt == '-a':
            if validate_ami(conn, arg):
                ami = arg
        if opt == '-p':
            persist_storage = True
        if opt == '-v':
            seed = int(arg)
        if opt == '-z':
            zone = arg
        if opt == '-b':
            _bootstrap = True
        if opt == '-k':
            ssh_key = arg

    provision(conn, instance_size, security_groups, num_of_instances, name, persist_storage, ssh_key,
              zone, ami, seed, _bootstrap)


def provision(conn, instance_size, security_groups, num_of_instances, name, persist_storage, ssh_key,
              zone=None, ami=settings.settings['default_ami'], seed=1, _bootstrap=None):

    original_name = name

    print('Provisioning Instance...')

    reservation = conn.run_instances(
        ami,
        key_name=ssh_key,
        instance_type=instance_size,
        security_groups=security_groups,
        min_count=num_of_instances,
        max_count=num_of_instances,
        placement=zone)

    # Bootstrap instance(s) and print results
    for instance in xrange(0, num_of_instances):

        if name:
            name = increment_hostname(original_name, (instance + seed))

        # Get a reference to the next instance
        instance = reservation.instances[instance]

        # Check up on its status every so often
        status = instance.update()
        while status == 'pending':
            count = 0
            time.sleep(10)  # seconds
            status = instance.update()
            count += 1
            if count > 18:  # Wait for 3 minutes before giving up on the instance. TODO instance should be killed here
                break

        # Set EBS delete_on_termination to true so EBS does not persist after instance is destroyed.
        if not persist_storage:
            for num in range(0, 5):
                try:
                    instance.modify_attribute('blockDeviceMapping', {'/dev/sda': True})
                    break
                except:
                    time.sleep(10)  # 10 Seconds

        # Print status and start bootstrapping once status returns running
        if status == "running":
            if name:
                instance.add_tag('Name', name)  # If name is present and instance is running a tag can be added
            private_ip = instance.private_ip_address
            public_ip = instance.ip_address
            print('Hostname: %s' % str(name))
            print('Public IP Address: %s' % public_ip)
            print('Private IP Address: %s' % private_ip)
            print('Instance status: %s' % status + '\n')

            # TODO: Kill and re-provision if instances is not up after 5mins
            # If name and environment aren't present skip bootstrapping
            if name and _bootstrap:
                _bootstrap(name, public_ip, private_ip)

    return reservation


def print_help():
    print textwrap.dedent("""
        Provisions and optionally bootstraps a given number of EC2 instances.
        If node name (-n) and -b are not used instances will be provisioned but not bootstrapped.

        Most defaults can be overidden in settings.py

        USAGE:
        -n:  Sets the hostname of the instance. This is also the name that will appear in AWS name field.
             If provisioning multiple instances name will increment by one per node starting the 1 or the value provided
             by -v.  '%s' will be replaced with the value.  Ex: web-%s.example.com will be web-1.example.com.

        -a:  Default: ami-9a562df2  :: AMI ID to provision. Default is Public Ubuntu 14.04 LTS.
        -s:  Default: m1.small      :: Instance size. If specified size is invalid default will be used.
        -g:  Default: None          :: Add additional security groups separated by comma. If group does not exist it will be created.
        -x:  Default: 1             :: Sets the number of instances to provision.
        -p:  Default: No            :: If used EBS volume will persists on termination of the EC2 instance.
        -v:  Default: 1             :: Sets the seed number for the hostname incrementation
        -z:  Default: Chosen by AWS :: Sets the availability zone to launch the instance(s)
        -k:  Default: None          :: Name of SSH key on AWS account to use for the provisioned instance.
        -b:  Default: None          :: Python function to be executed after provisioning.  Function will be passed
                                       instances hostname, public IP addr and private IP addr.
        """)


def validate_settings():
    required_settings = ['AWS_KEY_ID', 'AWS_SECRET_KEY', 'REGION', 'base_security_group', 'default_ssh_key']

    for setting in required_settings:
        if not settings.settingsp[setting]:
            raise NotImplementedError('Settings error.  Settings.py must provide the following settings: %s. '
                                      'See documentation for details' % required_settings)


# Create security group if it is not already present
def validate_group(conn, arg):
    groups = arg.split(',')
    for group in groups:
        try:
            conn.create_security_group(group, group)
            print 'Created group: %s' % group
        except EC2ResponseError:
            pass
    return groups


# Ensure provided size is valid
def validate_instance_size(instance):
    """ Ensure provided EC2 type (size) is valid """
    if instance in settings.settings['sizes']:
        return True
    else:
        print instance + ' is not a valid instance size using m1.small'
        return False


def increment_hostname(name, value):
    try:
        return name % str(value)
    except TypeError:
        return name


def validate_ami(conn, arg):
    """ Returns true if provided AMI ID is available to the provided AWS connection."""
    try:
        conn.get_image(arg)
        return True
    except EC2ResponseError:
        print(arg + ' is not a valid AMI ID, using default image')
        return False


if __name__ == "__main__":
    main(sys.argv[1:])
