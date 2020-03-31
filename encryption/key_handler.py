from encryption.rsa_key import SenderRSAKey
from encryption.session_key import SenderSessionKey, RecipientSessionKey


class SenderKeyHandler:
    def __init__(self, public_key):
        self.public_key = public_key
        self.recipient_public_key = None

        self.session_key = None
        self.encrypted_session_key = None

    def generate_sender_rsa_key(self, access_key):
        self.rsa_key = SenderRSAKey(access_key)
        self.rsa_key.create()

    def generate_sender_session_key(self, recipient_public_key):
        self.sender_session_key = SenderSessionKey(recipient_public_key)
        self.sender_session_key.create()

    def handle_posttransmission(self):
        """recipient_encrypted_session_key and sender_private_key need to be set before calling"""
        if self.recipient_encrypted_session_key and self.sender_private_key:
            self.recipient_session_key = RecipientSessionKey(self.sender_private_key)


class ReceiverKeyHandler:
    def __init__(self, private_key):
        self.private_key = private_key

        self.sender_encrypted_session_key = None
        self.sender_session_key = None
