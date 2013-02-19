"""
Signals relating to questions and answers.
"""
from django.dispatch import Signal

# Sent just before a answer will be posted (after it's been approved and
# moderated; this can be used to modify the answer (in place) with posting
# details or other such actions. If any receiver returns False the answer will be
# discarded and a 403 (not allowed) response. This signal is sent at more or less
# the same time (just before, actually) as the Answer object's pre-save signal,
# except that the HTTP request is sent along with this signal.
answer_will_be_posted = Signal(providing_args=["answer", "request"])

# Sent just after a answer was posted. See above for how this differs
# from the Answer object's post-save signal.
answer_was_posted = Signal(providing_args=["answer", "request"])

# TODO, see django.contrib.comments
# Sent after a comment was "flagged" in some way. Check the flag to see if this
# was a user requesting removal of a comment, a moderator approving/removing a
# comment, or some other custom user flag.
#comment_was_flagged = Signal(providing_args=["comment", "flag", "created", "request"])
