# config

In the **/config** folder there are several files
+ **.env**
+ **utils.py**
+ **settings.py**
+ **config.py**


## .env
Here you find the following Information:
+ **API-TOKENs**
+ **GUILD-ID`s**
+ **Database Connections** (username, password,...)
+ **Bot-Prefix**

## utils.py
Here you find 2 functions 
+ **has_premium_access()**
+ **has_test_access()**

These functions return the GuildID for "**Premium**" or "**Test**" **Guild / Server**.

## settings.py
Here you find the Logger configuration
The variable is "**LOGGING_CONFIG**".

It's an **JSON**,
under the Node "**loggers**" you can add another logger.
This is useful for Debugging in general so you can see in which file the Error was raised.


## config.py
this file gets the data from the .env
with "os.getenv()"