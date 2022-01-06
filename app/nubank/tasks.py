from .wrapper.entrypoint import get_data

def get_nubank_data(userList):
    users = userList.split(',')
    print(f'Requested Users: {users}')
    for user in users:
        print(f'Executin schedule for {user}')

        get_data(user)

        print(f'Finished schedule for {user}')


