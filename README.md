# Raspberry GPIO Sockets
Communicate with Raspberry GPIO over UDP and TCP Sockets. Explores using UDP as push stream of changes to inputs and outputs on the Raspberry. TCP Connection enables the remote client to control output state changes from the client software.

Companion Swift app on https://github.com/matzpersson/raspberry-swift-gpio-remote.git

# Installation
Download or Clone Python scripts from this repo and copy files to Linux or OSX server. I haven't tested this on windows. You will need to have atleast Python 2.7.

# Configuration
Configure GPIO pin setup by modifying the pinmap_modelb.conf file to suit your needs.

# Usage
Launch with: python simulated.py. As the name suggests, the python script has a little simulator that pulls and drops input states. Once the script is running, it will start a logger which will enable you to monitor states of pin, when clients connects and when services start.

#Copyright
Copyright 2016 Headstation. (http://headstation.com) All rights reserved. It is free software and may be redistributed under the terms specified in the LICENSE file (Apache License 2.0). 
