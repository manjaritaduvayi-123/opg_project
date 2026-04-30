from db import users

all_users = list(users.find())

print("Users in DB:")
for user in all_users:
    print(user)