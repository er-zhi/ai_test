def calculate_discount(price, discount_percent):
    result = price - price * discount_percent / 100
    if result < 0:
        return 0
    return result

def process_order(items):
    total = 0
    for item in items:
        total += calculate_discount(item['price'], item['discount'])
    # TODO: add tax calculation
    return total

class UserManager:
    def __init__(self):
        self.users = {}

    def add_user(self, name, email):
        self.users[email] = {"name": name, "email": email}
        return True

    def get_user(self, email):
        return self.users[email]  # potential KeyError

    def delete_user(self, email):
        del self.users[email]  # potential KeyError
        return True
