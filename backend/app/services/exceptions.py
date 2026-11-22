class SocialError(Exception):
    pass


class SelfFollowError(SocialError):
    pass


class UserNotFoundError(SocialError):
    pass


class BlockedError(SocialError):
    pass


class AlreadyFollowingError(SocialError):
    pass
