from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from starlette.requests import Request
from tortoise.contrib.fastapi import register_tortoise
from models import *

from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from emails import send_email, verify_token

app = FastAPI()



@post_save(User)
async def validate_user(
    sender: "Type[User]",
    instance: User,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str]
) -> None:
    if created:
        await send_email([instance.email], instance)

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models" : ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
@app.post("/registration")
async def user_registration(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    # await send_email(user_info["email"])
    return{
        "status" : "ok",
        "data" : f"Hello {new_user.username}, thanks for registering with us. Please check your email inbox and click on the link to confirm your registration."

    }

@app.get('/verification', response_class=HTMLResponse)
async def email_verification(request: Request, token: str):
    user = await verify_token(token)

    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return{
            "status" : "ok",
            "data" : f"Hello {user.username}, your account has been successfully verified"}



 