from aenum import Enum

# ENCRYPTION
BLOCK_SIZE = 16  # aes data block size in bytes
SESSION_KEY_SIZES = [128, 192, 256]  # key for aes can be 128, 192 or 256 bits long

PARM_ALG_TYPE_LEN = 4  # length of an algorithm type parameter in bits
PARM_SESS_KEY_SIZE_LEN = 2  # length of a session key size parameter in bits
PARM_BLOCK_SIZE_LEN = 8  # length of a block size parameter in bits
PARM_CIPHER_MODE_LEN = 2  # length of a cipher mode parameter in bits
PARM_LEN = (PARM_ALG_TYPE_LEN + PARM_SESS_KEY_SIZE_LEN + PARM_BLOCK_SIZE_LEN + PARM_CIPHER_MODE_LEN) // 8  # length of
# a parameters message header in bytes
FILE_PERCENT_LEN = 8  # length of a percent size parameter in file message in bits

# COMMUNICATION
SOCKET_BUFSIZE = BLOCK_SIZE * 1536  # maximum amount of data to be received at once by socket
SOCKET_HEAD_TYPE_LEN = 4  # length of a message type parameter in socket message header in bytes
SOCKET_HEAD_SIZE_LEN = 4  # # length of a message length parameter in socket message header in bytes
SOCKET_HEADLEN = SOCKET_HEAD_TYPE_LEN + SOCKET_HEAD_SIZE_LEN  # length of a socket message header (message type,
# message length) in bytes
SOCKET_HEADFORMAT = '4sL'  # formatting of a socket message header, 4s - 4 chars (bytes); L - unsigned long

# SHARED
BLOCK_CIPHER_MODE = Enum(value='BlockCipherMode', names={'ECB': 'ECB', 'CBC': 'CBC', 'CFB': 'CFB', 'OFB': 'OFB'})
TMP_DIRECTORY_PATH = 'tmp'

# LOGGING
LOGS_DIRECTORY_PATH = 'logs'
LOGS_FILENAME_PREFIX = f'debug_'
LOGS_FILENAME_EXTENSION = '.log'
