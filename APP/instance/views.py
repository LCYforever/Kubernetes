from . import instance
from flask import request, jsonify, make_response
from ..util.authorize import user_auth
from ..models import Image, Instance, User
from .. import db
import json
import docker

client = docker.from_env()


@instance.route('/create', methods=['POST'])
@user_auth
def create_instance():
    if request.method == 'GET':
        message_e = 'only post method is supported'
        return jsonify({'message': message_e})
    else:
        data = request.get_data()
        json_data = json.loads(data)
        user_name = json_data['username']
        image_id = json_data['aid']
        instance_name = user_name + "_" + json_data['instancename']
        param = json_data['param']
        json_param = json.loads(param)
        cpu = json_param['cpu']
        memory = json_param['memory']
        image = Image.query.filter_by(id=image_id).first_or_404()
        image_name = image.image
        try:
            container = client.containers.run(image_name, detach=True, cpu_period=100000,
                                              cpu_quota=cpu*100, mem_limit=str(memory)+"m",
                                              ports={'8000/tcp': None}, memswap_limit=-1, name=instance_name)
        except docker.errors.ContainerError:
            print 'the container exits with a non-zero exit code and detach is False.'
            return jsonify({'message': 'create fail'}), 400
        except docker.errors.ImageNotFound:
            print 'the images is not exist'
            return jsonify({'message': 'create fail'}), 400
        except docker.errors.APIError:
            print 'the server return an error'
            return jsonify({'message': 'create fail'}), 400
        if container:
            new_instance = Instance()
            user = User.query.filter_by(username=user_name).first()
            new_instance.user_id = user.id
            new_instance.image_id = image_id
            new_instance.instance_name = instance_name
            new_instance.cpu_num = cpu
            new_instance.memory_num = memory
            new_instance.user = user
            new_instance.image = Image.query.filter_by(id=image_id).first()
            db.session.add(new_instance)
            db.session.commit()
            return jsonify({'iid': new_instance.id}), 200
        else:
            return jsonify({'message': 'create fail'}), 400


@instance.route('/get_ins_list', methods=['GET'])
@user_auth
def get_instance_list():
    if request.method == 'GET':
        kind = request.args.get('kind')
        username = request.args.get('username')
        return_list = []
        if kind == 'all':
            instances = Instance.query.all()
        else:
            instances = User.query.filter_by(username=username).first().instances
        for i in instances:
            ins_dict = dict()
            ins_dict['iid'] = i.id
            ins_dict['instancename'] = i.instance_name.split('_')[1]
            ins_dict['appname'] = i.image.image_name
            ins_dict['createtime'] = str(i.created_time)
            ins_dict['username'] = i.user.username
            ins_dict['status'] = i.status
            return_list.append(ins_dict)
        return jsonify({'instances': return_list})





