import json

from flask import Flask,request,jsonify
from MethodCalls import MethodCalls
from flask_cors import CORS  # Import CORS
MethodCalls = MethodCalls()
app = Flask(__name__)
CORS(app)


@app.route('/createUser')
def createUserCall():
    name = request.args.get('name')
    email = request.args.get('email')
    print("name,email",name,email)
    if name is None or email is None:
        return {
            'status': False,
            'msg': f'name or email is empty'
        }
    response = MethodCalls.createUser(name=name,email=email)
    return response

@app.route('/login')
def loginUser():
    name = request.args.get('name')
    email = request.args.get('email')
    print("name,email",name,email)
    if name is None or email is None:
        return {
            'status': False,
            'msg': f'name or email is empty'
        }
    response = MethodCalls.loginUser(name=name,email=email)
    return response, 200


@app.route('/createPost',methods=['POST'])
def createPostCall():
    data = request.form.get('data')
    name = request.form.get('name')
    email = request.form.get('email')
    image = request.files.getlist('image')
    if not all([data, name, email]):
        return {
            'status': False,
            'msg': 'Missing required fields'
        }
    response = MethodCalls.createPost(data=data,image=image,name=name,email=email)
    return response

@app.route('/getAllPost',methods=['GET'])
def getAllPostCall():
    email = request.args.get('email')
    name = request.args.get('name')
    if not all([name, email]):
        return {
            'status': False,
            'msg': 'Missing required fields'
        }
    response = MethodCalls.getAllPost()
    return jsonify(response)

@app.route('/likePost',methods=['POST'])
def likePostCall():
    data = request.get_json()
    post_id = data.get('post_id')
    name = data.get('name')
    email = data.get('email')
    print("post_id,email,name",post_id,email,name)
    if not all([post_id,name,email]):
        return {
            'status': False,
            'msg': 'Missing required fields (post_id,name,email,like)'
        }
    response = MethodCalls.likePostCall(post_id=post_id,name=name)
    return response

@app.route('/commentsPost',methods=['POST'])
def commentsPost():
    data = request.get_json()
    post_id = data.get('post_id')
    name = data.get('name')
    comment_context = data.get('comment_context')
    if not all([post_id,name,comment_context]):
        return {
            'status': False,
            'msg': 'Missing required fields (post_id,name,email,like)'
        }
    response = MethodCalls.commentsPost(post_id=post_id, name=name,comment_context=comment_context)
    return response


@app.route('/updateProfile',methods=['POST'])
def updateProfileCall():
    data = request.get_json()
    name = data.get('name')
    new_name = data.get('new_name')
    email = data.get('email')
    if not all([name,email,new_name]):
        return {
            'status': False,
            'msg': 'Missing required fields (post_id,name,email,like)'
        }
    response = MethodCalls.updateProfileCall(email=email, name=name,new_name=new_name)
    return response



if __name__ == "__main__":
    app.run(debug=True,port=5000)
