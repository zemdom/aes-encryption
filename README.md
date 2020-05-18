# aes-encryption

Peer-to-peer encypted communicator to send files and messages over TCP. Uses ```janus``` sync/async queues to pass data, ```PyQt5``` for GUI, ```PyCryptodome``` for AES and ```asyncio``` for connection over TCP/IP.


## Architecture

![image](https://user-images.githubusercontent.com/49080434/82188781-af5d7f00-98ee-11ea-89f2-37179d58dbe7.png)   

**One peer uses both client and server sockets - client socket is opened each time a message is sent.**  


## Communication protocol

#### Message header

```message header (8B) = message type (4B) + message length (4B) (unsigned long)```

#### Message types

* INIT - initialize connection - send address on which sender is listening
* PKEY - send public key
* SKEY - send session key encrypted with private key
* PARM - send AES parameters encrypted with private key 
* TEXT - send a batch of text data encypted with AES algorithm
* FILE - send file data encrypted with AES algorithm:
    * INIT - initialize sending file - send filename
    * PARM - send size of a file in bytes
    * DATA - send a batch of file data
    * QUIT - signalize end of file data sending
* QUIT - signalize end of connection

#### Parameters message format

```parameters (18B) = algorithm type (1bit) + key size (2bits) + block size (8bit) + cipher mode (2bits) + padding (3 bits) + initial vector (16B)```  
* key size - 128, 192 or 256 bit  
* cipher mode - ECB, CBC, CFB or OFB
