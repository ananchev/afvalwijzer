# Telegram notifier for mijnafvalwijzer.nl
Send Telegram message reminders a day ahaead of trash bin collection (gft, paper or pmt) as published on [https://mijnafvalwijzer.nl](https://mijnafvalwijzer.nl). 
* Written in Python and intended to run on Docker
* Telegram's personal bots feature is used, without need of third-party middleware or private data exposure


# Install and run
## Create Telegram bot and configure telegram_send
1. Use this [https://telegram.me/BotFather](https://telegram.me/BotFather) to open your Telegram client and start a chat with the BotFather. Send the message `/newbot` and follow the instructions.
2. Open a terminal and run `python -m pip install telegram-send` to install telegram_send
3. Continue in the terminal by running `telegram-send --configure --config telegram-send.conf`. This will trigger the authentication process required to send messages via the bot. 
4. Keep the `telegram-send.conf` file secure as it can be used by anyone to control your bot. When (re)creating the docker image, it is required in the app root directory together with the Dockerfile. Once the image is created, it can be removed or stored elsewhere. 


## Create the Docker image
```console
docker build -t afvalwijzer .
```

## Run the image
Use the following Docker run command to spin and run a container from the image. 
Few clarifications:
* The environment variable URL is in the format `https://mijnafvalwijzer.nl/nl/<postcode>/<huisnummer>/<toevoeging>`. You can directly copy this from the browser's address bar when you have searched for the collection dates for your address.
* The run command is using single file mapping for the app logfile from within the container to the host. In order this to work when running container first time, make sure to create an empty `afvalwizer.log` in the app folder on the docker host.

```console
docker run \
        --name afvalwijzer \
        --net=host \
        -e URL=<mijnafvlwijzer url for address> \
        -v /etc/localtime:/etc/localtime:ro \
        -v /etc/timezone:/etc/timezone:ro \
        -v <app directory on docker host>/afvalwijzer.log:/app/afvalwijzer.log \
        --restart=always \
        -d \
        afvalwijzer:latest
```

### Export image to file
Generate image tar file to copy and load into a remote Docker host
```console
docker save -o afvalwijzer.tar afvalwijzer
```

### Load tar image
Once image copied to the host, it can be loaded with the command below
```console
docker load -i afvalwijzer.tar
```
