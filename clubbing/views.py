from django.shortcuts import render
from django.http import HttpResponse
from clubbing.models import *

import random, datetime, string, json

COOKIE_NAME = "EmojUserID"

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
            Riddle(riddler=first_user, title=title_obj, unicode_chars=the_riddle, seconds_spent=10).save()


def get_random_cookie():
    pool = string.digits + string.ascii_letters
    return ''.join(random.choice(pool) for _x in range(20))

def get_user(request):
    existing_cookie = request.COOKIES.get(COOKIE_NAME)
    now = datetime.datetime.now()
    if existing_cookie and User.objects.filter(cookie_id=existing_cookie).exists():
        rec = User.objects.filter(cookie_id=existing_cookie).get()
        rec.last_seen = now
        rec.page_count += 1
        rec.save()
        return rec
    else:
        new_cookie = get_random_cookie()
        campaign_id, campaign_source, referrer = '', '', None # TODO
        new_user = User(
            cookie_id=new_cookie, first_seen=now, last_seen=now,
            campaign_id=campaign_id, campaign_source=campaign_source, referrer=referrer
        )
        new_user.save()
        return new_user

def wrap_with_cookie(resp, user_obj):
    resp.set_cookie(COOKIE_NAME, user_obj.cookie_id)
    return resp

def find_hint(shown_riddle_id):
    shown_riddle = ShownRiddle.objects.get(id=shown_riddle_id)
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


def text_match(s1, s2):
    return s1 and s2 and s1.lower() == s2.lower()

##############################
# actual ajax/views functions
##############################


def load_hint(request):
    hint = find_hint(request.srid)
    return wrap_with_cookie(HttpResponse(hint), get_user(request))

def load_specific_riddle(request, uuid):
    # This a dev-env hack, just to put some stuff in DB so we can query (usually on empty DB)
    push_some_initial_values()
    now = datetime.datetime.now()
    the_riddle = Riddle.loadFromUUID(uuid)
    solver = get_user(request)
    shown = ShownRiddle(
        solver=solver, riddle_shown=the_riddle, time_shown=now, hints_used=''
    )
    shown.save()
    return wrap_with_cookie(
        HttpResponse(json.dumps({"riddle": the_riddle.unicode_chars, "srid": shown.id})),
        get_user(request)
    )

def load_some_riddle(request):
    # This a dev-env hack, just to put some stuff in DB so we can query (usually on empty DB)
    push_some_initial_values()
    uuid = random.choice(Riddle.objects.all()).getUUID()
    return load_specific_riddle(request, uuid)

def load_some_title(request):
    # This a dev-env hack, just to put some stuff in DB so we can query (usually on empty DB)
    push_some_initial_values()
    now = datetime.datetime.now()
    riddler = get_user(request)
    title = random.choice(Title.objects.all())
    shown=ShownTitle(
        riddler=riddler, title_shown=title, time_shown=now
    )
    shown.save()
    return {"stid": shown.id, "title": title.text, "category": title.category}

def submit_riddle(request, stid, chosen_chars, more_chars_considered=None):
    # This a dev-env hack, just to put some stuff in DB so we can query (usually on empty DB)
    push_some_initial_values()
    now = datetime.datetime.now()
    shown_title = ShownTitle.objects.get(id=stid)
    riddler = get_user(request)
    rid = Riddle(
        riddler=riddler,
        title=shown_title.title_shown,
        seconds_spent=(now-shown_title.time_shown).total_seconds(),
        unicode_chars=chosen_chars,
        more_chars_considered=more_chars_considered,
    )
    rid.save()
    return {"link": rid.getUUID()}

def submit_solution(request, srid, guess):
    # This a dev-env hack, just to put some stuff in DB so we can query (usually on empty DB)
    push_some_initial_values()
    now = datetime.datetime.now()
    shown_riddle = ShownRiddle.objects.get(id=srid)
    if text_match(shown_riddle.riddle_shown.title.text == guess):
        # Create a shareable-link for a friend, with a new fake-riddle
        riddle_copy = Riddle(
            riddler=shown_riddle.solver,
            title=shown_riddle.riddle_shown.title.text,
            seconds_spent=(now-shown_riddle.time_shown).total_seconds(),
            unicode_chars=shown_riddle.riddle.unicode_chars,
            reshared=shown_riddle.riddle_shown
        )
        riddle_copy.save()
        return {"success": 1, "share_link": riddle_copy.getUUID()}
    else:
        return {"success": 0}
