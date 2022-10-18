from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import current_user, login_required
from ..apiauthhelper import token_required
from flask_cors import CORS, cross_origin
from app.models import Post, db, User


ig = Blueprint('ig', __name__, template_folder='igtemplates')



@ig.route('/api/posts')
def getAllPostsAPI():
        posts = Post.query.order_by(Post.date_created.desc()).all()
        my_posts = [p.to_dict() for p in posts]
        return {'status': 'ok', 'total_results': len(posts), "posts": my_posts}
  

@ig.route('/api/posts/<int:post_id>')
def getSinglePostsAPI(post_id):
    post = Post.query.get(post_id)
    if post:
        return {
            'status': 'ok',
            'total_results': 1,
            "post": post.to_dict()
            }
    else:
        return {
            'status': 'not ok',
            'message': f"A post with the id : {post_id} does not exist."
        }


@ig.route('/api/posts/create', methods=["POST"])
@token_required
def createPostAPI(user):
    data = request.json 

    title = data['title']
    caption = data['caption']
    img_url = data['imgUrl']

    post = Post(title, img_url, caption, user.id)
    post.save()

    return {
        'status': 'ok',
        'message': "Post was successfully created."
    }

@ig.route('/api/posts/delete/<int:post_id>', methods=["POST"])
@token_required
def delPostAPI(user, post_id):
    
    delpost = Post.query.filter_by(id=post_id).first()
    delpost.delete()
    

    return {
        'status': 'ok',
        'message': "Post was successfully DELETED."
    }

@ig.route('/api/posts/update', methods=["POST"])
@token_required
def updatePostAPI(user):
    data = request.json 

    post_id = data['postId']

    post = Post.query.get(post_id)
    if post.user_id != user.id:
        return {
            'status': 'not ok',
            'message': "You cannot update another user's post!"
        }

    title = data['title']
    caption = data['caption']
    img_url = data['imgUrl']

    post.updatePostInfo(title, img_url, caption)
    post.saveUpdates()

    return {
        'status': 'ok',
        'message': "Post was successfully updated."
    }

@ig.route('/api/follow', methods=["POST"])
@cross_origin()
@token_required
def ApifollowUser(user):
    data = request.json 
    users_id=data['users_id']
    user2 = User.query.filter_by(id=users_id).first()
    user1 = User.query.filter_by(id=user.id).first()
    if user1 != user2:
        user1.follow(user2)
        return {
            'status': 'ok',
            'message': "User followed"
        }
    else:
        return {
        'status': 'ok',
        'message': "Cannot follow this user"
    }

@ig.route('/api/unfollow', methods=["POST"])
@cross_origin()
@token_required
def ApiunfollowUser(user):
    data = request.json 
    username=data['unfollow']
    user2 = User.query.filter_by(username=username).first()
    user1 = User.query.filter_by(id=user.id).first()
    user1.unfollow(user2)
   
    return {
        'status': 'ok',
        'message': "User unfollowed"
    }

@ig.route('/api/followers/<int:user_id>')
def getFollowers(user_id):
    this_user = User.query.filter_by(id=user_id).first()
    followers_lst = this_user.followers.all()
    
    new_follow_lst=[]
    for each in followers_lst:
        if each not in new_follow_lst:
            new_follow_lst.append([each.username, each.id])
    print(new_follow_lst)
    return {
        'status': 'Ok',
        'followers':new_follow_lst
       
    }
@ig.route('/api/following/<int:user_id>')
def getFollowing(user_id):
    this_user = User.query.filter_by(id=user_id).first()
    following_lst = this_user.following.all()
    
    new_following_lst=[]
    for each in following_lst:
        if each not in new_following_lst:
            new_following_lst.append([each.username, each.id])
    print(new_following_lst)
    return {
        'status': 'Ok',
        'following':new_following_lst
       
    }
@ig.route('/api/posts/myfeed/<int:user_id>')
def getMyFeedPostsAPI(user_id):
    this_user = User.query.filter_by(id=user_id).first()
    following_lst = this_user.following.all()
    new_following_lst=[]
    for each in following_lst:
        if each not in new_following_lst:
            new_following_lst.append(each.username)
    print(new_following_lst)
    posts = Post.query.order_by(Post.date_created.desc()).all()
    my_posts = [p.to_dict() for p in posts]
    print(my_posts)
    my_feed=[]
    for each in my_posts:
        if each['author'] in new_following_lst:
            print('appending')
            my_feed.append(each)
    print(my_feed)
    return {'status': 'ok', 'total_results': len(posts), "posts": my_feed}
   
 



@ig.route('/api/posts/user/<int:users_id>')
def getMyPostsAPI(users_id):
    users_id = User.query.filter_by(id=users_id).first()
    users_id=users_id.id
    posts = Post.query.filter_by(user_id=users_id).all()
    my_posts = [p.to_dict() for p in posts]
    print(my_posts)
    
    
    return {'status': 'ok', 'total_results': len(posts), "posts": my_posts}
   
@ig.route('/api/userid/<string:user_name>')
def getUserId(user_name):
    print(user_name)
    users_id = User.query.filter_by(username=user_name).first()
    this_id=users_id.id
    print(this_id)
    return {'status': 'ok', 'username':user_name, "id": this_id}
    