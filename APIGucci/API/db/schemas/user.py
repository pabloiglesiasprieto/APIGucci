def user_schema(user) -> dict:
    # El id en base de datos es _id
    return {"id": str(user["_id"]),
            "name": user["name"],
            "surname": user["surname"],
            "age": user["age"]}


def users_schema(users) -> list:
    return [user_schema(user) for  user in users]