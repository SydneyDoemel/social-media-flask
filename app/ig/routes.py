from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import current_user, login_required
from ..apiauthhelper import token_required
from flask_cors import CORS, cross_origin
from app.ig.forms import PostForm
from app.models import Post, db, User


ig = Blueprint('ig', __name__, template_folder='igtemplates')


@ig.route('/posts/create', methods=["GET","POST"])
@login_required
def createPost():
    form = PostForm()
    if request.method == "POST":
        if form.validate():
            title = form.title.data
            img_url = form.img_url.data
            caption = form.caption.data

            post = Post(title, img_url, caption, current_user.id)
            post.save()
            flash('Successfully created post.', 'success')
        else:
            flash('Invalid form. Please fill out the form correctly.', 'danger')
    return render_template('createpost.html', form=form)

@ig.route('/posts')
def getAllPosts():
    if current_user.is_authenticated:
        posts = current_user.get_followed_posts()
    else:
        posts = Post.query.order_by(Post.date_created.desc()).all()
    return render_template('feed.html', posts=posts)


@ig.route('/posts/<int:post_id>')
def getSinglePost(post_id):
    post = Post.query.get(post_id)
    # post = Post.query.filter_by(id=post_id).first()
    return render_template('singlepost.html', post=post)

@ig.route('/posts/update/<int:post_id>', methods=["GET", "POST"])
@login_required
def updatePost(post_id):
    form = PostForm()
    # post = Post.query.get(post_id)
    post = Post.query.filter_by(id=post_id).first()
    if current_user.id != post.user_id:
        flash('You are not allowed to update another user\'s posts.', 'danger')
        return redirect(url_for('ig.getSinglePost', post_id=post_id))
    if request.method=="POST":
        if form.validate():
            title = form.title.data
            img_url = form.img_url.data
            caption = form.caption.data

            post.updatePostInfo(title,img_url,caption)
            post.saveUpdates()
            flash('Successfully updated post.', 'success')
            return redirect(url_for('ig.getSinglePost', post_id=post_id))
        else:
            flash('Invalid form. Please fill out the form correctly.', 'danger')
    return render_template('updatepost.html', form=form,  post=post)


@ig.route('/posts/delete/<int:post_id>')
@login_required
def deletePost(post_id):
    post = Post.query.get(post_id)
    if current_user.id != post.user_id:
        flash('You are not allowed to delete another user\'s posts.', 'danger')
        return redirect(url_for('ig.getSinglePost', post_id=post_id))
    post.delete()
    flash('Successfully delete post.', 'success')
    return redirect(url_for('ig.getAllPosts'))


@ig.route('/follow/<int:user_id>')
@login_required
def followUser(user_id):
    user = User.query.get(user_id)
    current_user.follow(user)
    return redirect(url_for('index'))

@ig.route('/unfollow/<int:user_id>')
@login_required
def unfollowUser(user_id):
    user = User.query.get(user_id)
    current_user.unfollow(user)
    return redirect(url_for('index'))





################# API ROUTES #####################
@ig.route('/api/posts')
def getAllPostsAPI():
    # args = request.args
    # pin = args.get('pin')
    # print(pin, type(pin))
    # if pin == '1234':

        posts = Post.query.order_by(Post.date_created.desc()).all()

        my_posts = [p.to_dict() for p in posts]
        return {'status': 'ok', 'total_results': len(posts), "posts": my_posts}
    # else:
    #     return {
    #         'status': 'not ok',
    #         'code': 'Invalid Pin',
    #         'message': 'The pin number was incorrect, please try again.'
    #     }

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
    data = request.json # this is coming from POST request Body

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
    data = request.json # this is coming from POST request Body

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
    data = request.json # this is coming from POST request Body
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
    data = request.json # this is coming from POST request Body
    username=data['unfollow']
    user2 = User.query.filter_by(username=username).first()
    user1 = User.query.filter_by(id=user.id).first()
    user1.unfollow(user2)
   
    return {
        'status': 'ok',
        'message': "Userr unfollowed"
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
    # else:
    #     return {
    #         'status': 'not ok',
    #         'code': 'Invalid Pin',
    #         'message': 'The pin number was incorrect, please try again.'
    #     }



@ig.route('/api/posts/user/<int:users_id>')
def getMyPostsAPI(users_id):
    users_id = User.query.filter_by(id=users_id).first()
    users_id=users_id.id
    # posts = Post.query.filter_by(user_id=users_id.id).order_by(Post.date_created.desc()).all()
    posts = Post.query.filter_by(user_id=users_id).all()
    my_posts = [p.to_dict() for p in posts]
    print(my_posts)
    
    
    return {'status': 'ok', 'total_results': len(posts), "posts": my_posts}
    # else:
    #     return {
    #         'status': 'not ok',
    #         'code': 'Invalid Pin',
    #         'message': 'The pin number was incorrect, please try again.'
    #     }