def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name="admin").exists())

def is_moderator(user):
    return user.is_authenticated and user.groups.filter(name__in=["admin", "moderator"]).exists()

def is_authenticated(user):
    return user.is_authenticated