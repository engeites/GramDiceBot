
class DataProcesser:
    def __init__(self, data):
        self.user_id = data.from_user.id
        self.chat_id = data.chat.id
        self.username = data.from_user.username
        self.first_name = data.from_user.first_name
        self.last_name = data.from_user.last_name

    def get_data(self):
        return [self.user_id, self.first_name, self.last_name, self.username, self.chat_id]
