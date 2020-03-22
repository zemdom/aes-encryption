BLOCK_SIZE = 16  # aes data block size in bytes

SOCKET_BUFSIZE = 4096  # maximum amount of data to be received at once by socket
SOCKET_HEADSIZE = 8  # size of a socket message header (message type, message length) in bytes
SOCKET_HEADFORMAT = '4sL'  # formatting of a socket message header
