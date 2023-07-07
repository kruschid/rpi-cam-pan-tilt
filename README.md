## Prerequisites

### docker

```sh
# docker
sudo curl -fsSL https://get.docker.com | bash
sudo usermod -aG docker $USER
echo "Log out and log back in to use docker without sudo"
exit
```

### 64bit raspberry pi os

```sh
# raspberry pi os 64bit:
# https://www.raspberrypi.com/documentation/computers/configuration.html#raspi-config-cli
sudo raspi-config nonint do_legacy 0 # enable legacy camera interface for opencv
sudo raspi-config nonint do_i2c 0 # enable ic2
```

### 32 bit

```sh
# raspbian:
echo -e "\ndtparam=i2c_arm=on\nstart_x=1\ngpu_mem=128\n" | sudo tee -a /boot/config.txt
```

Modifies `/boot/config.txt` as follows:

```ini
dtparam=i2c_arm=on    # servo hat requires i2c
start_x=1             # essential for camera
gpu_mem=128           # at least for the cam, or maybe more if you wish
```
