import click

from api.models import User


def validate_username(ctx, param, value):
    if User.query.filter(User.username == value).first():
        raise click.BadParameter('User with this name already exists')
    return value


@click.command('create-superuser')
@click.option('--username', prompt=True, required=True, callback=validate_username)
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True)
def create_superuser(username, password):
    """
    Создает нового супервользователя.
    :param username:
    :param password:
    :return:
    """

    user = User(username=username, password=password)
    user.is_admin = True
    user.save()
