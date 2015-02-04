

settings = dict(

    # Defaults the user may wish to override
    default_instance_size='m1.small',
    default_ami='ami-9a562df2',  # Ubuntu 14.04 LTS

    sizes=['m3.large', 'm3.xlarge', 'm3.2xlarge', 'm1.small', 'm1.medium', 'm3.medium', 'm1.large', 'm1.xlarge', 'c3.large',
           'c3.xlarge', 'c3.2xlarge', 'c3.4xlarge', 'c3.8xlarge', 'c1.medium', 'c1.xlarge', 'm2.xlarge',
           'm2.2xlarge', 'm2.4xlarge', 'hi1.4xlarge', 'hs1.8xlarge', 't1.micro', 't2.small', 't2.micro'],

    # Defaults required by the user
    AWS_KEY_ID=None,            # String
    AWS_SECRET_KEY=None,        # String
    REGION=None,                # String
    base_security_group=None,   # List of string(s) Ex: ['web_security']
    default_ssh_key=None,       # String


)


