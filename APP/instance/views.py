from . import instance
from flask import request, jsonify, make_response
from ..util.authorize import user_auth
from ..models import Image, Instance, User
from .. import db
from datetime import datetime
import json
import docker
import time


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
            if image.id == 1 or image.id == 2 or image.id == 4:
                # Ubuntu or CentOs or caffe, just open ssh and upload
                container = client.containers.run(image_name, detach=True, cpu_period=100000, cpu_quota=cpu * 100,
                                                  mem_limit=str(memory) + "m", oom_kill_disable=True,
                                                  ports={'8000/tcp': None, '8001/tcp': None},
                                                  memswap_limit=-1, name=instance_name)
            elif image.id == 3:
                # TensorFlow cpu version, open ssh, jupyter and dashboard
                container = client.containers.run(image_name, detach=True, cpu_period=100000, cpu_quota=cpu * 100,
                                                  mem_limit=str(memory) + "m", oom_kill_disable=True,
                                                  ports={'8000/tcp': None, '8080/tcp': None, '8888/tcp': None},
                                                  memswap_limit=-1, name=instance_name)
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
            new_instance.created_time = datetime.now()
            new_instance.cpu_num = cpu
            new_instance.memory_num = memory
            new_instance.user = user
            new_instance.image = Image.query.filter_by(id=image_id).first()
            db.session.add(new_instance)
            db.session.commit()
            return jsonify({'iid': new_instance.id}), 200
        else:
            return jsonify({'message': 'create fail'}), 400


@instance.route('/get_instance', methods=['GET'])
@user_auth
def get_instance():
    if request.method == 'GET':
        kind = request.args.get('kind')
        username = request.args.get('username')
        iid = request.args.get('iid')
        return_list = []
        if username is not None:
            if kind == 'all':
                instances = Instance.query.all()
            else:
                instances = User.query.filter_by(username=username).first().instances
        elif iid is not None:
            instances = Instance.query.filter_by(id=iid)
        for i in instances:
            ins_dict = dict()
            ins_dict['iid'] = i.id
            ins_dict['aid'] = i.image.id
            ins_dict['instancename'] = i.instance_name.split('_')[1]
            ins_dict['appname'] = i.image.image_name
            ins_dict['createtime'] = str(i.created_time)
            ins_dict['username'] = i.user.username
            ins_dict['status'] = i.status
            ins_dict['cpu'] = i.cpu_num
            ins_dict['memory'] = i.memory_num
            ins_dict['nodes'] = i.container_num
            return_list.append(ins_dict)
        return jsonify({'instances': return_list}), 200

@instance.route('/get_proxy', methods=['GET'])
@user_auth
def get_instance_proxy():
    iid = request.args.get('iid')
    ins = Instance.query.filter_by(id=iid).first_or_404()
    ins_name = ins.instance_name
    container = client.containers.get(ins_name)
    try:
        if container is not None:
            proxys = []
            print container.attrs['NetworkSettings']['Ports']
            for k, v in container.attrs['NetworkSettings']['Ports'].items():
                if v is None:
                    continue
                port = k.split('/')[0]
                hostport = v[0]['HostPort']
                if hostport is None:
                    continue
                if port == '8000':
                    proxy_name = 'ssh'
                elif port == '8001':
                    proxy_name = 'upload'
                elif port == '8080':
                    proxy_name = 'jupyter-web'
                elif port == '8888':
                    proxy_name = 'tensorboard'
                proxys.append({'proxy_name': proxy_name, 'proxy_url': hostport})
            return jsonify({'proxys': proxys}), 200
    except docker.errors.NotFound:
        print "container does not exists"
        return jsonify({'message_e': 'fail to get proxy cause container not exist'}), 400
    except docker.errors.APIError:
        print "get proxy fail"
        return jsonify({'message_e': 'get proxy fail'}), 400   


@instance.route('/del_instance', methods=['GET', 'POST'])
@user_auth
def del_instance():
    if request.method == 'GET':
        message_e = 'only post method is supported'
        return jsonify({'message': message_e}), 400
    else:
        iid = json.loads(request.get_data())['iid']
        ins = Instance.query.filter_by(id=iid).first_or_404()
        if ins is not None:
            ins_name = ins.instance_name
            try:
                container = client.containers.get(ins_name)
                if container is not None:
                    container.remove(force=True)
                    db.session.delete(ins)
                    db.session.commit()
                    return jsonify({'message': 'delete success'}), 200
                else:
                    print "container not exist"
                    return jsonify({'message_e': 'delete fail'}), 400
            except docker.errors.NotFound:
                print "container does not exists"
                return jsonify({'message_e': 'delete fail,container does not exists'}), 400
            except docker.errors.APIError:
                print "container delete fail"
                return jsonify({'message_e': 'delete fail'}), 400
        else:
            print "instance not exist"
            return jsonify({'message_e': 'delete fail'}), 400


@instance.route('/stop_instance', methods=['GET', 'POST'])
@user_auth
def stop_instance():
    if request.method == 'GET':
        message_e = 'only post method is supported'
        return jsonify({'message_e': message_e}), 400
    else:
        iid = json.loads(request.get_data())['iid']
        ins = Instance.query.filter_by(id=iid).first()
        if ins is not None and ins.status == 0:
            ins_name = ins.instance_name
            result_code = 0
            try:
                container = client.containers.get(ins_name)
                if container is not None:
                    container.stop()       
                    ins.status = 1
                    db.session.add(ins)
                    db.session.commit()
                    result_code = 1
                else:
                    print "container not exist"
                    return jsonify({'message_e': 'delete fail'}), 400
            except docker.errors.NotFound:
                print "container does not exists"
                return jsonify({'message_e': 'delete fail,container does not exists'}), 400
            except docker.errors.APIError:
                print "container delete fail"
                return jsonify({'message_e': 'delete fail'}), 400
            if result_code == 1:
                return jsonify({'message': 'stop success'}), 200
            else:
                return jsonify({'message_e': 'delete fail'}), 400
        else:
            print "instance not exist"
            return jsonify({'message_e': 'stop fail'}), 400


@instance.route('/recover_instance', methods=['GET', 'POST'])
@user_auth
def recover_instance():
    if request.method == 'GET':
        message_e = 'only post method is supported'
        return jsonify({'message': message_e}), 400
    else:
        ins_name = json.loads(request.get_data())['instancename']
        ins = Instance.query.filter_by(instance_name=ins_name).first_or_404()
        if ins is not None and ins.status == 1:
            ins_name = ins.instance_name
            try:
                container = client.containers.get(ins_name)
                if container is not None:
                    container.start()
                    ins.status = 0
                    db.session.add(ins)
                    db.session.commit()
                    return jsonify({'message': 'recover success', 'iid': ins.id}), 200
                else:
                    print "container not exist"
                    return jsonify({'message_e': 'delete fail'}), 400
            except docker.errors.NotFound:
                print "container does not exists"
                return jsonify({'message_e': 'delete fail,container does not exists'}), 400
            except docker.errors.APIError:
                print "container delete fail"
                return jsonify({'message_e': 'delete fail'}), 400
        else:
            print "instance not exist"
            return jsonify({'message_e': 'recover fail'}), 400




