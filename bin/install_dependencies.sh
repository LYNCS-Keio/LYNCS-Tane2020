#!/bin/bash


echo -n "password : "
read -s password


#install pip3
ret=0
which pip3 2>&1 > /dev/null ; ret=$?

if [ ! "$ret" = "0" ]; then
    echo "install pip3"
    ret=0    
    echo "$password" | sudo -S apt install python3-pip ; ret=$?
    if [ ! "$ret" = 0 ]; then
        echo "installation Failed!"
    else
        echo "pip3 installed!"
    fi
else
    echo "pip3 already installed!"
fi


#install pipenv
ret=0
which pipenv 2>&1 > /dev/null ; ret=$?

if [ ! "$ret" = "0" ]; then
    echo "install pipenv"
    ret=0
    echo "$password" | sudo -S pip3 install pipenv ; ret=$?
    if [ ! "$ret" = 0 ]; then
        echo "installation Failed!"
    else
        echo "pipenv installed!"
    fi
else
    echo "pipenv already installed!"
fi


#install dependencies for pyenv
echo "install dependencies for pyenv"
ret=0
echo "$password" | sudo -S apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl git ; ret=$?
if [ ! "$ret" = 0 ]; then
    echo "installation Failed!"
else
    echo "dependencies installed!"
fi


#install pyenv
ret=0
which pyenv 2>&1 > /dev/null ; ret=$?

if [ ! "$ret" = "0" ]; then
    echo "install pyenv"
    echo "Download pyenv..."
    ret=0
    echo "$password" | sudo -S git clone https://github.com/pyenv/pyenv.git ~/.pyenv ; ret=$?

    if [ ! "$ret" = 0 ]; then
        echo "Download Failed!"
    else
        echo "Download Success"
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
        echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
        echo 'eval "$(pyenv init -)"' >> ~/.profile
        echo "pyenv installed!"
    fi

else
    echo "pipenv already installed!"
fi
