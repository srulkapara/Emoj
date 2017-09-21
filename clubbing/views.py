from django.shortcuts import render
from django.http import HttpResponse
from clubbing.models import *

import random, datetime, string, json
# Create your views here.


COOKIE_NAME = "UserID"

def push_some_initial_values():
    RIDDLE2TITLE = {":)" : 'happy', ":(": 'sad'}
    USERS = ['1', '2']
    now = datetime.datetime.now()
    for the_title in RIDDLE2TITLE.values():
        if Title.objects.filter(text=the_title).count() == 0:
            Title(text=the_title).save()
    for the_user in USERS:
        if User.objects.filter(cookie_id=the_user).count() == 0:
            User(cookie_id=the_user, first_seen=now, last_seen=now).save()
    for the_riddle in RIDDLE2TITLE.keys():
        if Riddle.objects.filter(unicode_chars=the_riddle).count() == 0:
            title_obj = Title.objects.filter(text=RIDDLE2TITLE[the_riddle]).get()
            first_user = User.objects.all()[0]
            Riddle(phraser=first_user, title=title_obj, unicode_chars=the_riddle, seconds_spent=10).save()


def get_random_cookie():
    pool = string.digits + string.ascii_letters
    return ''.join(random.choice(pool) for _x in range(20))

def log_user(request):
    existing_cookie = request.COOKIES.get(COOKIE_NAME)
    now = datetime.datetime.now()
    if existing_cookie and User.objects.filter(cookie_id=existing_cookie).exists():
        rec = User.objects.filter(cookie_id=existing_cookie).get()
        print('Found %s (%s attempts)!'%(existing_cookie, rec.page_count))
        rec.last_seen = now
        rec.page_count += 1
        rec.save()
        return existing_cookie
    else:
        new_cookie = get_random_cookie()
        campaign_id, campaign_source, referrer = '', '', None # TODO
        User(
            cookie_id=new_cookie, first_seen=now, last_seen=now,
            campaign_id=campaign_id, campaign_source=campaign_source, referrer=referrer
        ).save()
        return new_cookie

def wrap_with_cookie(resp, cookie):
    resp.set_cookie(COOKIE_NAME, cookie)
    return resp

def find_hint(shown_riddle_id):
    shown_riddle = ShownRiddle.objects.get(id=shown_riddle_id)
    log_user(shown_riddle.solver) # no change for cookie
    riddle = shown_riddle.riddle_shown
    now = datetime.datetime.now()
    hints_in_order = [{'category': riddle.title.category}] + [
        {'letter_%s'%l: [
            # get indices
            ind for (ind, letter) in enumerate(riddle.title.text) if letter == l
        ]} for l in set(riddle.title.text)
    ]
    if shown_riddle.hints_used:
        already_served = json.loads(shown_riddle.hints_used)
        next_k, next_v = next((k for k in hints_in_order if k not in already_served), (None, None))
        if next_k:
            already_served[next_k] = now
            shown_riddle.hints_used = json.dumps(already_served)
            shown_riddle.save()
            return {next_k: next_v}
        else:
            # No more hints available
            return {}
    else:
        next_k, next_v = hints_in_order[0]
        shown_riddle.hints_used = json.dumps({next_k: now})
        shown_riddle.save()
        return {next_k: next_v}


def get_hint(request):
    hint = find_hint(request.shown_riddle_id)
    return HttpResponse(hint)

def get_initial_page(request):
    # This a dev-env hack, just to put some stuff in DB so we can query (usually on empty DB)
    push_some_initial_values()
    guess_me = random.choice([x.unicode_chars for x in Riddle.objects.all()])
    return wrap_with_cookie(HttpResponse(guess_me), log_user(request))


