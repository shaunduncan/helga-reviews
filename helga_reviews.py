from rbtools.api.client import RBClient
from rbtools.api.errors import APIError

from helga import settings, log
from helga.plugins import command


REVIEWBOARD_URL = getattr(settings, 'REVIEWS_REVIEWBOARD_URL', None)
MAX_RESULTS_CHANNEL = getattr(settings, 'REVIEWS_MAX_RESULTS_CHANNEL', 5)
MAX_RESULTS_PRIVMSG = getattr(settings, 'REVIEWS_MAX_RESULTS_PRIVMSG', 10)
CHANNEL_GROUP_MAPPING = getattr(settings, 'REVIEWS_CHANNEL_GROUP_MAPPING', {})


logger = log.getLogger(__name__)


def get_open_reviews(args):
    """
    get open reviews to a specified user, group, etc.
    """
    args['status'] = 'pending'
    if 'max_results' not in args:
        args['max_results'] = 100

    client = RBClient(REVIEWBOARD_URL)
    root = client.get_root()

    if not root:
        logger.error(u'Could not get RBClient root')
        return None

    try:
        req = root.get_review_requests(**args)
    except APIError:
        logger.exception(u'Error querying API')
        return None

    ret = {'total': req.total_results, 'reviews': []}
    review_fmt = u"[{user}] {summary} ({url}/r/{id})"

    for review in req:
        ret['reviews'].append(review_fmt.format(user=review.get_submitter().username,
                                                summary=review.summary,
                                                url=REVIEWBOARD_URL,
                                                id=review.id))

    return ret


def get_reviews(for_type, for_arg, limit=MAX_RESULTS_CHANNEL):
    """
    Return a list of reviews for a user or group
    """
    kwargs = {'max_results': limit}

    if for_type == 'user':
        kwargs['to_users'] = for_arg
    else:
        kwargs['to_groups'] = for_arg

    reviews = get_open_reviews(kwargs)

    if not reviews:
        return u"Error getting reviews for {for_type} '{for_arg}'".format(for_type=for_type, for_arg=for_arg)

    responses = []

    if reviews['total'] < 1:
        return u"Found {n} pending reviews for {type} '{arg}'".format(
            n=reviews['total'], type=for_type, arg=for_arg
        )
    elif reviews['total'] < limit:
        responses.append(u"Found {n} pending reviews for {type} '{arg}':".format(
            n=reviews['total'], type=for_type, arg=for_arg
        ))
    else:
        responses.append(u"Found {n} pending reviews for {type} '{arg}'. First {m}:".format(
            n=reviews['total'], type=for_type, arg=for_arg, m=limit
        ))

    responses.extend(reviews['reviews'])
    return responses


@command('reviews', help='Query pending review requests. Usage: helga reviews [me|user <user>|group <group>]')
def reviews(client, channel, nick, message, cmd, args):
    max_results = MAX_RESULTS_CHANNEL if channel.startswith('#') else MAX_RESULTS_PRIVMSG

    if args:
        for_type = args[0]
        for_arg = nick if for_type == 'me' else args[1]

        if for_type == 'me':
            for_type = 'user'
    elif channel.startswith('#'):
        # Requesting group reviews
        if channel not in CHANNEL_GROUP_MAPPING:
            return u"Sorry {nick}, but I don't know the reviewboard group for {channel}".format(
                nick=nick, channel=channel
            )
        for_type = 'group'
        for_arg = CHANNEL_GROUP_MAPPING[channel]
    else:
        # Requesting my reviews
        for_type = 'user'
        for_arg = nick

    return get_reviews(for_type, for_arg, limit=max_results)
