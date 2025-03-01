# ABOUT THIS REPO
This microservice is used as an endpoint (see [Project Summary](#project-summary)) to send messages to Telegram by means of [Telegram Bot API](https://core.telegram.org/bots/api).

An encoded message is taken from the dedicated RabbitMQ queue and sent to the required Telegram chat via the bot API.

The Telegram bot functionality is implemented with the [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/) package.

# DEPENDENCIES
- [RabbitMQ](https://www.rabbitmq.com/)
- MySQL database
- [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/)

# SETUP
- Install the dependencies listed in ```requirements.txt```
- Make copy of the ```config.example.ini``` and name it ```config.ini```
- Fill the database connection requisites in the ```DATABASE``` section of the ```config.ini``` file
- Fill the RabbitMQ connection requisites in the ```RABBIT``` section of the ```config.ini``` file 
- Change the queue name in the ```APP``` section of the ```config.ini``` file if necessary

# PROJECT SUMMARY
This project is a set of microservices for distribution of an initial message with all kinds of services:
Telegram, E-mail or any other service as deemed necessary, including plain HTTP requests.

The idea of the project is to allow a user to set up a project with desirable endpoints and to send a message only once
to distribute it, including any media attached thereto.

The project utilizes [RabbitMQ](https://www.rabbitmq.com/) for message distribution.

The project consists of a receiver microservice to encode initial text and attachments into JSON
and a dispatcher microservice to push the message into project-related queues for further processing:

```
                                              --> endpoint microservice #1
                                              |    
incoming message --> receiver --> dispatcher ---> endpoint microservice #2
                                              |
                                              --> endpoint microservice #3 
```

The final distribution is performed by endpoint microservices, each implemented depending on capabilities of the
system used. Use of [RabbitMQ](https://www.rabbitmq.com/) allows to deploy as many clones of an endpoint microservice as
required in case if such channel is used extensively.

[Dashboard]()

Other microservices:

- [Receiver]()
- [Dispatcher]()
- [SMTP BZ Sender]()
- [Telegram Sender]()