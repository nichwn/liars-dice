"""

Parses the configuration file to be used by other modules.

"""
import ConfigParser
import os.path

# Accessing file locations from a string in Python appears to always be
# relative to the module which started the program, even if the project root
# is in the file path. Hence the following file location finding:
current_dir = os.path.abspath(os.path.dirname(__file__))
config_location = os.path.join(current_dir, "config.ini")

config = ConfigParser.ConfigParser({"host": "localhost", "port": 9637})
config.read(config_location)

host = config.get("Client", "host")

port = int(config.get("Shared", "port"))