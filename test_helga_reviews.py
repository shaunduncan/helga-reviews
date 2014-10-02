from mock import Mock, patch

import helga_reviews


class FakeRBResponse(object):
    def __init__(self, results):
        self.results = results

    @property
    def total_results(self):
        return len(self.results)

    def __iter__(self):
        return iter(self.results)


@patch('helga_reviews.RBClient')
def test_get_open_reviews_no_root(client):
    client.return_value = client
    client.get_root.return_value = None
    assert helga_reviews.get_open_reviews({}) is None


@patch('helga_reviews.RBClient')
def test_get_open_reviews(client):
    mock_review = Mock(summary='Fix A Bug', id=12345)
    mock_review.get_submitter.return_value = Mock(username='foo')

    client.return_value = client
    client.get_root.return_value = client
    client.total_results = 10
    client.get_review_requests.return_value = FakeRBResponse([mock_review])

    helga_reviews.REVIEWBOARD_URL = u'http://example.com'

    resp = helga_reviews.get_open_reviews({})
    client.get_review_requests.assert_called_with(status='pending', max_results=100)

    assert resp['total'] == 1
    assert resp['reviews'] == [u'[foo] Fix A Bug (http://example.com/r/12345)']


@patch('helga_reviews.get_open_reviews')
def test_get_reviews_calls_with_correct_args(get_open_reviews):
    helga_reviews.get_reviews('user', 'foobar', limit=5)
    get_open_reviews.assert_called_with({'max_results': 5, 'to_users': 'foobar'})

    get_open_reviews.reset_mock()

    helga_reviews.get_reviews('group', 'bargroup', limit=25)
    get_open_reviews.assert_called_with({'max_results': 25, 'to_groups': 'bargroup'})


@patch('helga_reviews.get_open_reviews')
def test_get_reviews_no_reviews(get_open_reviews):
    get_open_reviews.return_value = {'total': 0}
    resp = helga_reviews.get_reviews('user', 'me')
    assert resp == u"Found 0 pending reviews for user 'me'"


@patch('helga_reviews.get_open_reviews')
def test_get_reviews_under_total_limit(get_open_reviews):
    get_open_reviews.return_value = {'total': 3, 'reviews': ['foo', 'bar', 'baz']}
    resp = helga_reviews.get_reviews('user', 'me')
    assert resp == [u"Found 3 pending reviews for user 'me':", 'foo', 'bar', 'baz']


@patch('helga_reviews.get_open_reviews')
def test_get_reviews_over_limit(get_open_reviews):
    get_open_reviews.return_value = {'total': 25, 'reviews': ['foo', 'bar', 'baz']}
    resp = helga_reviews.get_reviews('user', 'me', limit=3)
    assert resp == [u"Found 25 pending reviews for user 'me'. First 3:", 'foo', 'bar', 'baz']


@patch('helga_reviews.get_reviews')
def test_reviews_with_args(get_reviews):
    helga_reviews.reviews(Mock(), '#bots', 'me', 'foo', 'bar', ['user', 'blah'])
    get_reviews.assert_called_with('user', 'blah', limit=helga_reviews.MAX_RESULTS_CHANNEL)

    get_reviews.reset_mock()

    # Handles 'me'
    helga_reviews.reviews(Mock(), '#bots', 'foo', 'bar', 'baz', ['me'])
    get_reviews.assert_called_with('user', 'foo', limit=helga_reviews.MAX_RESULTS_CHANNEL)


@patch('helga_reviews.get_reviews')
def test_reviews_has_correct_limit(get_reviews):
    helga_reviews.reviews(Mock(), '#bots', 'me', 'foo', 'bar', ['user', 'blah'])
    get_reviews.assert_called_with('user', 'blah', limit=helga_reviews.MAX_RESULTS_CHANNEL)

    get_reviews.reset_mock()

    # Handles privmsg limit
    helga_reviews.reviews(Mock(), 'foo', 'foo', 'bar', 'baz', ['me'])
    get_reviews.assert_called_with('user', 'foo', limit=helga_reviews.MAX_RESULTS_PRIVMSG)


def test_reviews_no_group_mapping():
    resp = helga_reviews.reviews(Mock(), '#bots', 'me', 'foo', 'bar', [])
    assert resp == u"Sorry me, but I don't know the reviewboard group for #bots"


@patch('helga_reviews.get_reviews')
def test_reviews_mapped_group(get_reviews):
    helga_reviews.CHANNEL_GROUP_MAPPING['#bots'] = 'blah'
    helga_reviews.reviews(Mock(), '#bots', 'me', 'foo', 'bar', [])
    get_reviews.assert_called_with('group', 'blah', limit=helga_reviews.MAX_RESULTS_CHANNEL)


@patch('helga_reviews.get_reviews')
def test_reviews_for_me_via_privmsg(get_reviews):
    helga_reviews.reviews(Mock(), 'me', 'me', 'foo', 'bar', [])
    get_reviews.assert_called_with('user', 'me', limit=helga_reviews.MAX_RESULTS_PRIVMSG)
