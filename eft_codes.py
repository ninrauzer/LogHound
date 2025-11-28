"""
eft_codes.py
------------
Contiene los códigos de respuesta EFT Classic (KB Globalscape) y sus descripciones.
Define el diccionario de códigos estándar SFTP/FTP utilizados en el análisis de logs.

Fuente: https://kb.globalscape.com/Knowledgebase/10142/File-Transfer-Status-and-Error-Codes
"""

# Códigos FTP/FTPS
EFT_CODES = {
    # 100 Series - Requested action initiated
    110: "Restart marker reply",
    120: "Service ready in nn minutes",
    125: "Data connection already open; transfer starting",
    150: "File status okay; about to open data connection",
    
    # 200 Series - Requested action completed successfully
    200: "Command okay",
    202: "Command not implemented, superfluous at this site",
    211: "System status, or system help reply",
    212: "Directory status",
    213: "File status",
    214: "Help message",
    215: "NAME system type",
    220: "Service ready for new user",
    221: "Service closing control connection",
    225: "Data connection open; no transfer in progress",
    226: "Closing data connection (file transfer successful)",
    227: "Entering Passive Mode",
    230: "User logged in, proceed",
    250: "Requested file action okay, completed",
    257: "PATHNAME created",
    
    # 300 Series - Further information needed
    331: "User name okay, need password",
    332: "Need account for login",
    350: "Requested file action pending further information",
    
    # 400 Series - Temporary errors
    421: "Service not available, closing control connection",
    425: "Cannot open data connection",
    426: "Connection closed; transfer aborted",
    450: "Requested file action not taken (file busy)",
    451: "Requested action aborted: local error in processing",
    452: "Requested action not taken (insufficient storage)",
    
    # 500 Series - Permanent errors
    500: "Syntax error, command unrecognized",
    501: "Syntax error in parameters or arguments",
    502: "Command not implemented",
    503: "Bad sequence of commands",
    504: "Command not implemented for that parameter",
    530: "Not logged in (invalid credentials)",
    532: "Need account for storing files",
    550: "Requested action not taken (file unavailable/not found/no access)",
    552: "Requested file action aborted (storage allocation exceeded)",
    553: "Requested action not taken (file name not allowed)",
}

# HTTP/HTTPS codes
HTTP_CODES = {
    400: "Bad Request (malformed header or query)",
    401: "Unauthorized (login failed)",
    403: "Forbidden (permission denied)",
    404: "Not Found (file/folder does not exist)",
    406: "Not Acceptable (bad header value)",
    408: "Request Time-out (socket timeout)",
    411: "Length Required (invalid file length)",
    412: "Precondition Failed (session timeout)",
    413: "Request Entity Too Large (quota exceeded)",
    414: "Request-URI Too Large (URI exceeds max length)",
    500: "Internal Server Error (disk full or abort)",
    501: "Not Implemented (unimplemented request method)",
}

# SFTP codes
SFTP_CODES = {
    -1: "Undefined or unknown error",
    0: "Operation completed successfully",
    1: "End of file reached",
    2: "File does not exist",
    3: "Insufficient privileges",
    4: "Operation failed for other reason",
    5: "Badly formatted message (protocol error)",
    6: "Connection not established (timeout)",
    7: "Connection to server lost",
    8: "Timeout occurred",
}

# Códigos Winsock (Network Socket)
WINSOCK_CODES = {
    10054: "WSAECONNRESET - Connection reset by peer",
    10060: "WSAETIMEDOUT - Connection timed out",
    10061: "WSAECONNREFUSED - Connection refused",
    10066: "WSAENOTEMPTY - Directory not empty",
    10068: "WSAEUSERS - User quota exceeded",
    11001: "WSAHOST_NOT_FOUND - Host not found",
}

# Diccionario combinado para búsqueda rápida
ALL_CODES = {**EFT_CODES, **HTTP_CODES, **SFTP_CODES, **WINSOCK_CODES}
