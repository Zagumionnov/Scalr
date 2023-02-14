import flask
from app import database
from app.defines import MAX_TASK_NUMBER

blueprint = flask.Blueprint("tasks", __name__, url_prefix='/tasks')


@blueprint.route('/', methods=['GET'])
def get_tasks():
    """ View to get all tasks.

    :return: response with payload which contains json
    """
    tasks = database.Task.select()
    return flask.jsonify({
        "data": [task.to_response(flask.request.url_root + blueprint.url_prefix.lstrip('/')) for task in tasks]
    }), 200


@blueprint.route('/', methods=['POST'])
def create_task():
    """ View to create task.

    :return: response with payload which contains json
    """
    if database.Task.select().count() == MAX_TASK_NUMBER:
        return flask.jsonify({"error": "the maximum number of tasks has been reached"}), 400
    if "data" not in flask.request.json:
        return flask.jsonify({"error": "data is required"}), 400
    if not (attributes := flask.request.json["data"].get('attributes')):
        return flask.jsonify({"error": "data.attributes is required"}), 400

    try:
        task = database.Task.create(
            title=attributes.get('title'),
            command=attributes.get('command'),
            image=attributes.get('image'),
            description=attributes.get('description'),
        )
    except Exception:
        return flask.jsonify({
            "error": "Make sure 'title', 'command', 'image' and 'description' is in the attributes"
        }), 400

    return flask.jsonify({"data": task.to_response(flask.request.url_root + blueprint.url_prefix.lstrip('/'))}), 201


@blueprint.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """ View to get specific task.

    :return: response with payload which contains json
    """
    try:
        task = database.Task.get(id=task_id)
    except Exception:
        return flask.jsonify({"error": "task not exists"}), 400
    return flask.jsonify({
        "data": task.to_response(flask.request.url_root + blueprint.url_prefix.lstrip('/'))
    }), 200


@blueprint.route('/<int:task_id>', methods=['Delete'])
def delete_task(task_id):
    """ View to delete task.

    :return: successful response
    """
    task = database.Task.get(id=task_id)
    if task.status == task.Status.running:
        return flask.jsonify({"error": "running task can't be deleted"}), 400
    task.delete_instance()

    return flask.jsonify({}), 204


@blueprint.route('/<int:task_id>', methods=['Patch'])
def update_task(task_id):
    """ View to update task.

    :return: successful response
    """
    data = {}
    if title := flask.request.json.get('title'):
        data.update({'title': title})
    if description := flask.request.json.get('description'):
        data.update({'description': description})
    if not data:
        return flask.jsonify({"error": "invalid value"}), 400
    try:
        query = database.Task.update(data).where(database.Task.id == task_id)
        query.execute()
    except Exception:
        return flask.jsonify({"error": "task not exists"}), 400

    return flask.jsonify({
        "data": database.Task.get(id=task_id).to_response(flask.request.url_root + blueprint.url_prefix.lstrip('/'))
    }), 200


@blueprint.route('/<int:task_id>/logs', methods=['GET'])
def get_task_logs(task_id):
    """ View to get task logs.

    :return: response with payload which contains json
    """
    try:
        task = database.Task.get(id=task_id)
    except Exception:
        return flask.jsonify({"error": "task not exists"}), 400
    return flask.jsonify({"logs": task.logs}), 200
