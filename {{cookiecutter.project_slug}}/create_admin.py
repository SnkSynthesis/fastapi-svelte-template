from databases import Database
from getpass import getpass
from backend.crud.user_crud import UserCRUD, UserIn
from backend.configuration import config
import asyncio

async def main():
    async with Database(config.db_url) as db:
        user_crud = UserCRUD(db)
        user_crud.metadata_create_all(config.db_url)

        username = input("Admin username: ")
        password = getpass(prompt="Admin password: ")
        if getpass(prompt="Confirm admin password: ") != password:
            print("Passwords do not match!")
            print("Try again. Exiting...")
            exit()

        print("Passwords match!")

        await user_crud.create(UserIn(username=username, password=password))
        tasks = []
        for scope in config.scopes.keys():
            tasks.append(asyncio.create_task(user_crud.add_scope(username, scope)))
        
        await asyncio.gather(*tasks)

        print(f"Admin user, {username}, successfully created!")
        print("Exiting...")

asyncio.run(main())