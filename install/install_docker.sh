echo "0. Kernel ver.:"
uname -r

echo "1. Prerequestities"

echo "1.1 Updating apt sources"
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates

echo "1.2 Add the new GPG key."
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 \
--recv-keys 58118E89F3A912897C070ADBF76221572C52609D

echo "1.3 Determine where APT will search for packages. (ubuntu 16)"
echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" | \
     sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update

echo "1.3 Verify that APT is pulling from the right repository."
apt-cache policy docker-engine


echo "2. Ubuntu 16 Prerequestities"

echo "2.1 Install linux-image-extra-* packages"
sudo apt-get install linux-image-extra-$(uname -r) linux-image-extra-virtual


echo "3. Install Docker"

echo "3.1. Install Docker"
sudo apt-get install docker-engine

echo "3.2 Start the 'docker' daemon."
sudo service docker start

echo "3.3 Verify docker is installed correctly."
sudo docker run hello-world

echo "### DONE. Additional config at \
      https://docs.docker.com/engine/installation/linux/\
      ubuntulinux/#/optional-configurations"
