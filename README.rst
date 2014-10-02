helga-reviews
=============

A helga command to query reviewboard pending reviews targeted at a user, group
or channel (using a channel-to-group mapping).

Settings
--------

**REVIEWS_REVIEWBOARD_URL** ReviewBoard URL

**REVIEWS_MAX_RESULTS_CHANNEL** Maximum results to returnn in a channel (Default 5)

**REVIEWS_MAX_RESULTS_PRIVMSG** Maximum results to returnn in a private message (Default 10)

**REVIEWS_CHANNEL_GROUP_MAPPING** A dictionary of channel -> reviewboard group that sets the
default lookup group

License
-------

Copyright (c) 2014 Shaun Duncan

Licensed under an `MIT`_ license.

.. _`MIT`: https://github.com/shaunduncan/helga-reviews/blob/master/LICENSE
