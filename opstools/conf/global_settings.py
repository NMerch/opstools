def bootstrap_callback():
    raise NotImplementedError('bootstap_callback(name, public_ip, private_ip) funciton must be provided in settings.py'
                              ' to use -b bootstrap option')

settings = dict(
    num_of_instances=1,
    callback=bootstrap_callback,
)
