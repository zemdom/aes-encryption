from encryption.rsa_key import SenderRSAKey
from encryption.session_key import SenderSessionKey, RecipientSessionKey


class KeyHandler:
    def __init__(self):
        self.access_key = None
        self.rsa_key = None

        self.recipient_public_key = None
        self.sender_session_key = None

        self.recipient_encrypted_session_key = None
        self.sender_private_key = None
        self.recipient_session_key = None

    def handle_pretransmission(self):
        """access_key needs to be set before calling"""
        if self.access_key:
            self.rsa_key = SenderRSAKey(self.access_key)
            self.rsa_key.create()

    def handle_transmission(self):
        """recipient_public_key needs to be set before calling"""
        if self.recipient_public_key:
            self.sender_session_key = SenderSessionKey(self.recipient_public_key)
            self.sender_session_key.create()

    def handle_posttransmission(self):
        """recipient_encrypted_session_key and sender_private_key need to be set before calling"""
        if self.recipient_encrypted_session_key and self.sender_private_key:
            self.recipient_session_key = RecipientSessionKey(self.sender_private_key)
