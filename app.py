from flask import Flask, request, jsonify, send_from_directory
from models import PlaceBubbleTag, PlaceFeed, PlaceFeedTag, User, db, PlaceBubble
import os

app = Flask(__name__, static_folder='public')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Serve static files from the 'public' directory
@app.route('/public/<path:filename>')
def serve_public_file(filename):
    return send_from_directory(app.static_folder, filename)

# 새로운 버블을 생성하는 엔드포인트
@app.route('/bubbles', methods=['POST'])
def create_bubble():
    data = request.json
    new_bubble = PlaceBubble(
        image_url=data['image_url'],
        title=data['title'],
        size_level=data['size_level'],
        pos_x=data['pos_x'],
        pos_y=data['pos_y'],
        pos_z=data['pos_z']
    )
    db.session.add(new_bubble)
    db.session.commit()
    return jsonify(new_bubble.to_json()), 201

# 모든 버블을 가져오는 엔드포인트
@app.route('/bubbles', methods=['GET'])
def get_bubbles():
    bubbles = PlaceBubble.query.all()
    return jsonify({'bubbles': [bubble.to_json() for bubble in bubbles]}), 200

# 특정 ID의 버블을 가져오는 엔드포인트
@app.route('/bubbles/<int:id>', methods=['GET'])
def get_bubble(id):
    bubble = PlaceBubble.query.get_or_404(id)
    return jsonify(bubble.to_json()), 200

# 특정 ID의 버블을 업데이트하는 엔드포인트
@app.route('/bubbles/<int:id>', methods=['PUT'])
def update_bubble(id):
    data = request.json
    bubble = PlaceBubble.query.get_or_404(id)
    bubble.image_url = data.get('image_url', bubble.image_url)
    bubble.title = data.get('title', bubble.title)
    bubble.size_level = data.get('size_level', bubble.size_level)
    bubble.pos_x = data.get('pos_x', bubble.pos_x)
    bubble.pos_y = data.get('pos_y', bubble.pos_y)
    bubble.pos_z = data.get('pos_z', bubble.pos_z)
    db.session.commit()
    return jsonify(bubble.to_json()), 200

# 특정 ID의 버블을 삭제하는 엔드포인트
@app.route('/bubbles/<int:id>', methods=['DELETE'])
def delete_bubble(id):
    bubble = PlaceBubble.query.get_or_404(id)
    db.session.delete(bubble)
    db.session.commit()
    return jsonify({'message': 'Bubble deleted successfully'}), 200

# 특정 버블에 태그를 생성하는 엔드포인트
@app.route('/bubbles/<int:bubble_id>/tags', methods=['POST'])
def create_tag(bubble_id):
    bubble = PlaceBubble.query.get_or_404(bubble_id)
    data = request.json
    new_tag = PlaceBubbleTag(
        bubble_id=bubble.id,
        content=data['content'],
        is_advertisement=data.get('is_advertisement', False),
        size_level=data['size_level']
    )
    db.session.add(new_tag)
    db.session.commit()
    return jsonify(new_tag.to_json()), 201

# 특정 버블의 모든 태그를 가져오는 엔드포인트
@app.route('/bubbles/<int:bubble_id>/tags', methods=['GET'])
def get_tags(bubble_id):
    bubble = PlaceBubble.query.get_or_404(bubble_id)
    return jsonify([tag.to_json() for tag in bubble.tags]), 200

# 특정 버블의 특정 태그를 가져오는 엔드포인트
@app.route('/bubbles/<int:bubble_id>/tags/<int:tag_id>', methods=['GET'])
def get_tag(bubble_id, tag_id):
    tag = PlaceBubbleTag.query.filter_by(bubble_id=bubble_id, id=tag_id).first_or_404()
    return jsonify(tag.to_json()), 200

# 특정 버블의 특정 태그를 업데이트하는 엔드포인트
@app.route('/bubbles/<int:bubble_id>/tags/<int:tag_id>', methods=['PUT'])
def update_tag(bubble_id, tag_id):
    tag = PlaceBubbleTag.query.filter_by(bubble_id=bubble_id, id=tag_id).first_or_404()
    data = request.json
    tag.content = data.get('content', tag.content)
    tag.is_advertisement = data.get('is_advertisement', tag.is_advertisement)
    tag.size_level = data.get('size_level', tag.size_level)
    db.session.commit()
    return jsonify(tag.to_json()), 200

# 특정 버블의 특정 태그를 삭제하는 엔드포인트
@app.route('/bubbles/<int:bubble_id>/tags/<int:tag_id>', methods=['DELETE'])
def delete_tag(bubble_id, tag_id):
    tag = PlaceBubbleTag.query.filter_by(bubble_id=bubble_id, id=tag_id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    return jsonify({'message': 'Tag deleted successfully'}), 200

# 특정 버블에 피드를 생성하는 엔드포인트
@app.route('/bubbles/<int:bubble_id>/feeds', methods=['POST'])
def create_feed(bubble_id):
    bubble = PlaceBubble.query.get_or_404(bubble_id)
    data = request.json
    new_feed = PlaceFeed(
        bubble_id=bubble.id,
        user_id=data['user_id'],
        content=data['content'],
        media_url=data['media_url'],
        media_type=data['media_type'],
        is_advertisement=data.get('is_advertisement', False),
        view_count=data.get('view_count', 0),
        like_count=data.get('like_count', 0),
        is_liked=data.get('is_liked', False)
    )
    db.session.add(new_feed)
    db.session.commit()
    return jsonify(new_feed.to_json()), 201

# 특정 버블의 모든 피드를 가져오는 엔드포인트
@app.route('/bubbles/<int:bubble_id>/feeds', methods=['GET'])
def get_feeds(bubble_id):
    bubble = PlaceBubble.query.get_or_404(bubble_id)
    feeds = sorted(bubble.feeds, key=lambda feed: feed.like_count, reverse=True)
    return jsonify([feed.to_json() for feed in feeds]), 200

# 특정 버블의 상위 4개 피드를 가져오는 엔드포인트
@app.route('/bubbles/<int:bubble_id>/feeds/top4', methods=['GET'])
def get_feed_top4_in_bubble(bubble_id):
    bubble = PlaceBubble.query.get_or_404(bubble_id)
    feeds = sorted([feed for feed in bubble.feeds if feed.like_count > 100], key=lambda feed: feed.like_count, reverse=True)
    return jsonify([feed.to_json() for feed in feeds[:4]]), 200

# 특정 버블의 특정 피드를 가져오는 엔드포인트
@app.route('/bubbles/<int:bubble_id>/feeds/<int:feed_id>', methods=['GET'])
def get_feed(bubble_id, feed_id):
    feed = PlaceFeed.query.filter_by(bubble_id=bubble_id, id=feed_id).first_or_404()
    return jsonify(feed.to_json()), 200

# 특정 버블의 특정 피드를 업데이트하는 엔드포인트
@app.route('/bubbles/<int:bubble_id>/feeds/<int:feed_id>', methods=['PUT'])
def update_feed(bubble_id, feed_id):
    feed = PlaceFeed.query.filter_by(bubble_id=bubble_id, id=feed_id).first_or_404()
    data = request.json
    feed.content = data.get('content', feed.content)
    feed.media_url = data.get('media_url', feed.media_url)
    feed.media_type = data.get('media_type', feed.media_type)
    feed.is_advertisement = data.get('is_advertisement', feed.is_advertisement)
    feed.view_count = data.get('view_count', feed.view_count)
    feed.like_count = data.get('like_count', feed.like_count)
    feed.is_liked = data.get('is_liked', feed.is_liked)
    db.session.commit()
    return jsonify(feed.to_json()), 200

# 특정 버블의 특정 피드를 삭제하는 엔드포인트
@app.route('/bubbles/<int:bubble_id>/feeds/<int:feed_id>', methods=['DELETE'])
def delete_feed(bubble_id, feed_id):
    feed = PlaceFeed.query.filter_by(bubble_id=bubble_id, id=feed_id).first_or_404()
    db.session.delete(feed)
    db.session.commit()
    return jsonify({'message': 'Feed deleted successfully'}), 200

# 특정 피드에 태그를 생성하는 엔드포인트
@app.route('/feeds/<int:feed_id>/tags', methods=['POST'])
def create_feed_tag(feed_id):
    feed = PlaceFeed.query.get_or_404(feed_id)
    data = request.json
    new_tag = PlaceFeedTag(
        feed_id=feed.id,
        content=data['content'],
        is_advertisement=data.get('is_advertisement', False)
    )
    db.session.add(new_tag)
    db.session.commit()
    return jsonify(new_tag.to_json()), 201

# 모든 피드를 가져오는 엔드포인트
@app.route('/feeds', methods=['GET'])
def get_all_feeds():
    feeds = PlaceFeed.query.order_by(PlaceFeed.like_count.desc()).all()
    return jsonify([feed.to_json() for feed in feeds]), 200

# 특정 피드를 가져오는 엔드포인트
@app.route('/feeds/<int:feed_id>', methods=['GET'])
def get_feed_by_id(feed_id):
    feed = PlaceFeed.query.get_or_404(feed_id)
    return jsonify(feed.to_json()), 200

@app.route('/feeds/<int:feed_id>/like', methods=['POST'])
def toggle_like_feed(feed_id):
    feed = PlaceFeed.query.get_or_404(feed_id)
    if feed.is_liked:
        feed.like_count -= 1
    else:
        feed.like_count += 1
    feed.is_liked = not feed.is_liked
    db.session.commit()
    return jsonify(feed.to_json()), 200

# 특정 피드의 모든 태그를 가져오는 엔드포인트
@app.route('/feeds/<int:feed_id>/tags', methods=['GET'])
def get_feed_tags(feed_id):
    feed = PlaceFeed.query.get_or_404(feed_id)
    return jsonify([tag.to_json() for tag in feed.tags]), 200

# 특정 피드의 특정 태그를 가져오는 엔드포인트
@app.route('/feeds/<int:feed_id>/tags/<int:tag_id>', methods=['GET'])
def get_feed_tag(feed_id, tag_id):
    tag = PlaceFeedTag.query.filter_by(feed_id=feed_id, id=tag_id).first_or_404()
    return jsonify(tag.to_json()), 200

# 특정 피드의 특정 태그를 업데이트하는 엔드포인트
@app.route('/feeds/<int:feed_id>/tags/<int:tag_id>', methods=['PUT'])
def update_feed_tag(feed_id, tag_id):
    tag = PlaceFeedTag.query.filter_by(feed_id=feed_id, id=tag_id).first_or_404()
    data = request.json
    tag.content = data.get('content', tag.content)
    tag.is_advertisement = data.get('is_advertisement', tag.is_advertisement)
    db.session.commit()
    return jsonify(tag.to_json()), 200

# 특정 피드의 특정 태그를 삭제하는 엔드포인트
@app.route('/feeds/<int:feed_id>/tags/<int:tag_id>', methods=['DELETE'])
def delete_feed_tag(feed_id, tag_id):
    tag = PlaceFeedTag.query.filter_by(feed_id=feed_id, id=tag_id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    return jsonify({'message': 'Tag deleted successfully'}), 200

# 새로운 사용자를 생성하는 엔드포인트
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(
        username=data['username'],
        profile_image_url=data['profile_image_url'],
        is_sponsor=data.get('is_sponsor', False)
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_json()), 201

# 모든 사용자를 가져오는 엔드포인트
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_json() for user in users]), 200

# 특정 ID의 사용자를 가져오는 엔드포인트
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_json()), 200

# 특정 ID의 사용자를 업데이트하는 엔드포인트
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.username = data.get('username', user.username)
    user.profile_image_url = data.get('profile_image_url', user.profile_image_url)
    user.is_sponsor = data.get('is_sponsor', user.is_sponsor)
    db.session.commit()
    return jsonify(user.to_json()), 200

# 특정 ID의 사용자를 삭제하는 엔드포인트
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

vr_action = None

@app.route('/action-vr', methods=['POST'])
def action_vr():
    global vr_action
    data = request.json
    vr_action = data
    return jsonify({'message': 'Action VR'}), 200

@app.route('/action-vr', methods=['GET'])
def get_action_vr():
    global vr_action
    if not vr_action:
        return jsonify({'action': 'none', 'id': 0}), 200
    return jsonify(vr_action), 200

@app.route('/action-vr/reset', methods=['POST'])
def reset_action_vr():
    global vr_action
    vr_action = None
    return jsonify({'message': 'Action VR reset'}), 200

def init_db():
    import json
    with open('data.json', 'r') as file:
        data = json.load(file)
    for user in data['users']:
        new_user = User(
            id=user['id'],
            username=user['username'],
            profile_image_url=user['profile_image_url'],
            is_sponsor=user['is_sponsor']
        )
        db.session.add(new_user)
    for bubble in data['bubbles']:
        new_bubble = PlaceBubble(
            id=bubble['id'],
            image_url=bubble['image_url'],
            title=bubble['title'],
            size_level=bubble['size_level'],
            pos_x=bubble['pos_x'],
            pos_y=bubble['pos_y'],
            pos_z=bubble['pos_z']
        )
        db.session.add(new_bubble)
    for bubble_tag in data['bubble_tags']:
        new_bubble_tag = PlaceBubbleTag(
            bubble_id=bubble_tag['bubble_id'],
            content=bubble_tag['content'],
            is_advertisement=bubble_tag['is_advertisement'],
            size_level=bubble_tag['size_level']
        )
        db.session.add(new_bubble_tag)
    for feed in data['feeds']:
        new_feed = PlaceFeed(
            bubble_id=feed['bubble_id'],
            user_id=feed['user_id'],
            content=feed['content'],
            media_url=feed['media_url'],
            media_type=feed['media_type'],
            is_advertisement=feed['is_advertisement'],
            view_count=feed['view_count'],
            like_count=feed['like_count'],
            is_liked=feed['is_liked']
        )
        db.session.add(new_feed)
        db.session.commit()
        for tag in feed['tags']:
            new_feed_tag = PlaceFeedTag(
                feed_id=new_feed.id,
                content=tag
            )
            db.session.add(new_feed_tag)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
