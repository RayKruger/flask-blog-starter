from flask import Blueprint, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

from ..database import db
from ..models import Post

import requests
import json

posts = Blueprint("posts", __name__)


@posts.route("/", methods=("GET", "POST"))
def index():      
    posts = Post.query.all()
       
    if request.method == "POST":
        
        ##if button clicked find entered tag(s)
        tag = request.form["tag"]        
        flash("filter applied: "+str(tag)) 
        
        ##display query in a flash message
        ##filter by date
        n=2
        query = """query($input:Int!){
                      posts(first:$input) {
                        edges {
                          node {
                            title
                            createdAt
                          }
                        }
                      }
                    }"""  
        variables = {'input': n}         
        url = 'http://127.0.0.1:5000/graphql'
        r = requests.post(url, json={'query': query,'variables': variables})       
        flash("Query result: "+str(r.text))
        json_data = json.loads(r.text)
        
    return render_template("index.html", posts=posts)


@posts.route("/<int:post_id>")
def post(post_id):
    post = Post.query.get(post_id)
    if not post:
        abort(404)
    return render_template("post.html", post=post)


@posts.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        tag = request.form["tag"]
        
        if not title:
            flash("Title is required!")
        else:
            new_post = Post(title=title, content=content,taggg=tag)
            db.session.add(new_post)
            db.session.commit()
                
            return redirect(url_for("posts.index"))
    return render_template("create.html")


@posts.route("/<int:post_id>/edit", methods=("GET", "POST"))
def edit(post_id):
    post = Post.query.get(post_id)
    if not post:
        abort(404)

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            post.title = title
            post.content = content

            db.session.commit()

            return redirect(url_for("posts.index"))

    return render_template("edit.html", post=post)


@posts.route("/<int:post_id>/delete", methods=("POST",))
def delete(post_id):
    post = Post.query.get(post_id)
    if not post:
        abort(404)

    db.session.delete(post)
    db.session.commit()

    flash('"{}" was successfully deleted!'.format(post.id))
    return redirect(url_for("posts.index"))
