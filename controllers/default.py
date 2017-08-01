# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

if 0:
    from gluon import db, current, auth, LOAD
    response = current.response
    request = current.request

from collections import OrderedDict
from operator import itemgetter


def index():
    """
    Present main index page.

    Send dictionary of document records to the view views/default/index.html
    """
    docrows = db(db.docs.id > 0).select()
    doclist = sorted(docrows.as_list(), key=itemgetter('name'))
    docs_with_genres = sorted([d for d in doclist if d["genres"]],
                              key=itemgetter('name'))
    docs_with_figures = [d for d in doclist if d["figures"]]
    genres = sorted(list(set([db.genres[genre].genre for doc in docs_with_genres
                             for genre in doc["genres"]])))
    figures = sorted(list(set([db.biblical_figures[figure].figure for doc in docs_with_figures
                              for figure in doc["figures"]])))
    genre_rows = OrderedDict()
    for g in genres:
        gid = db.genres(db.genres.genre == g).id
        genre_rows[g] = [d for d in docs_with_genres if gid in d["genres"]]

    figure_rows = OrderedDict()
    for f in figures:
        fid = db.biblical_figures(db.biblical_figures.figure == f).id
        figure_rows[f] = [d for d in docs_with_figures if fid in d["figures"]]

    return {'docrows': doclist,
            'genrerows': genre_rows,
            'figurerows': figure_rows}


def page():
    """
    """
    pagelabel = request.args[0]
    pagerow = db(db.pages.page_label == pagelabel).select().first()
    return {'body': pagerow['body'],
            'title': pagerow['title']}


def listing():
    """
    Present a plugin_listandedit widget for creating and editing db records.

    URL Arguments
    ---------

        0:  The name of the db table to be manipulated by the widget.

    """

    widget = LOAD('plugin_listandedit', 'widget.load',
                  args=request.args,
                  vars=request.vars,
                  ajax=False)
    return {'widget': widget}


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

'''
def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
'''
