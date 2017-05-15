# unnamed-hosting

A Docker-based virtual hosting.
- An image for each language/framework.
- An image for a database server.
- Route requests between images.
- Web interface to handle them all.


## Installation
Install Docker by `sh running install/install_docker.sh`.
To run the web interface, run `doscker-compose up` from `web_interface` dir.
To run the hosting, run `sudo python3 daemon2.py` from `hosting_daemon2` dir.
