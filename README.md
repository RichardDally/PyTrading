## PyTrading project

PyTrading is a sandbox stock market project written in Python 3.  
This project has an educational purpose to learn how financial markets work. 

### Continuous Integration and code quality

| GNU/Linux     | Windows       | Static analysis  | Code coverage |
|:-------------:|:-------------:|:-------------:|:-------------:|
| [![Build Status](https://travis-ci.org/RichardDally/PyTrading.svg?branch=master)](https://travis-ci.org/RichardDally/PyTrading)  | [![Build status](https://ci.appveyor.com/api/projects/status/lt43ryv8akxftw90/branch/master?svg=true)](https://ci.appveyor.com/project/RichardDally/pytrading/branch/master) | [![Codacy Badge](https://api.codacy.com/project/badge/Grade/4a222cf711354f8dab9e797759b03ea5)](https://www.codacy.com/manual/RichardDally/PyTrading?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=RichardDally/PyTrading&amp;utm_campaign=Badge_Grade)|[![codecov](https://codecov.io/gh/RichardDally/PyTrading/branch/master/graph/badge.svg)](https://codecov.io/gh/RichardDally/PyTrading)|



### How to generate .proto files

Download `protoc` (e.g. [protoc v28.3 for Windows 64 bits](https://github.com/protocolbuffers/protobuf/releases/download/v28.3/protoc-28.3-win64.zip))

To generate Protobuf "_pb2.py" files:
````commandline
cd pytrading\protobuf
protoc --python_out=. *.proto
````

### Lexicon

- An **order** is composed of a price, a quantity, a way (buy or sell) and the instrument you want to trade (e.g. Apple stock)
- A **deal** is generated when there is a match between two orders on same price and same instrument (**order book**'s last price is updated)
- An **order book** hosts every incoming orders waiting to be executed (most interesting price comes first)

### High level architecture
- `TradingServer` is composed of two servers: a matching engine and a feeder.
  - `MatchingEngine` accepts orders from clients and try to match them.
  - `Feeder` streams continuously order books content (full snapshot).
- `TradingClient` connects two client sockets: an ordersender and a feedhandler.
  - `OrderSender` sends order according to algorithm implemented in `main_loop_hook`
  - `FeedHandler` receives order book updates (e.g. price modified, executed order etc..)

### Communication
`TradingServer` and `TradingClient` communicates via TCP/IP serialized messages.  
Two serializations are available: plain text (pipe separated) and Protobuf.

### Where to start
[`TradingSandbox`](tools/trading_sandbox.py) module gives a good example to start in local, take a look in `main_loop_hook` implementation.
 
### Requirements
- MongoDB
- Protobuf
