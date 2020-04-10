from encryption.keys.session_key import SenderSessionKey, RecipientSessionKey


class SenderKeyHandler:
    def __init__(self, public_key):
        self.public_key = public_key

        self.session_key_handler = None

    def create_session_key(self, recipient_public_key):
        self.session_key_handler = SenderSessionKey(recipient_public_key)
        self.session_key_handler.create()


class ReceiverKeyHandler:
    def __init__(self, private_key):
        self.private_key = private_key
        self.sender_session_key_handler = RecipientSessionKey(self.private_key)
