from flask import Flask, jsonify, request 
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120))
    done = db.Column(db.Integer)

    def __repr__(self):
        return "%s, %s, %s" % (self.id, self.description, self.done)

db.create_all()
CORS(app)

@app.route('/api/task', methods=['GET'])
def get_all_tasks():

    filter_by = request.query_string
    
    if filter_by:
        filtro = filter_by.decode('utf-8').split('=')
        task_list = db.session.query(Task).filter(Task.description.like('%%%s%%' % filtro[1])).all()
    else:
        task_list = Task.query.all()

    task_json = [{k:v for (k,v) in S.__dict__.items() if not k in ("_sa_instance_state")} for S in task_list]
    return jsonify(task_json)

@app.route('/api/task', methods=['POST'])
def add_task():
    add_dict = request.get_json()
    add_dict['done'] = 0

    ObjectAdd = Task(**add_dict)

    db.session.add(ObjectAdd)
    db.session.commit()

    task_json = [{k:v for (k,v) in S.__dict__.items() if not k in ("_sa_instance_state")} for S in [ObjectAdd]]
    return jsonify(task_json)

@app.route("/api/task/<id>", methods=['PUT'])
def update_task(id):
    
    ObjectUpd = Task.query.filter_by(id=id).first()
    update_task = request.get_json()
    
    if not 'done' in update_task:
        return  jsonify({'message' : 'Erro na validação de estrutura'})

    if not ObjectUpd:
        return  jsonify({'message' : 'Registro não encontrado'})

    ObjectUpd.done = int(update_task['done'])
    db.session.commit()
    result = [{k:v for (k,v) in S.__dict__.items() if not k in ("_sa_instance_state")} for S in [ObjectUpd]]

    return jsonify({"reuslt": result})

@app.route("/api/task/<id>", methods=['DELETE'])
def delete_task(id):
    ObjectDel = Task.query.filter_by(id=id).first()
    
    if not ObjectDel:
        return  jsonify({'message' : 'Registro não encontrado'})

    db.session.delete(ObjectDel)
    db.session.commit()
    return jsonify({"result": "success"})

if __name__ == '__main__':
    app.run(debug=True)
    