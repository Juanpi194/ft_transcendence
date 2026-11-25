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


class NotFollowingError(SocialError):
    pass


class FollowRequestNotFoundError(SocialError):
    pass


class FollowAlreadyAcceptedError(SocialError):
    pass


class AccountAlreadyPublicError(SocialError):
    pass


class AccountAlreadyPrivateError(SocialError):
    pass


class SelfBlockError(SocialError):
    pass


class AlreadyBlockedError(SocialError):
    pass


