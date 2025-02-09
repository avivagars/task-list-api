from flask import Blueprint, request, make_response, jsonify
from app import db
from app.models.goal import Goal
from app.models.task import Task
from app.routes.task_routes import validate_data, validate_post


goal_bp = Blueprint('goal_bp', __name__, url_prefix='/goals')


@goal_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()

    if "title" not in request_body:
        return make_response({"details": "Invalid data"}), 400

    new_goal = Goal(
        title=request_body["title"],
    )

    db.session.add(new_goal)
    db.session.commit()

    return make_response({"goal":
                          Goal.to_dict(new_goal)
                          }), 201


@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_task_ids_to_goal(goal_id):
    goal = Goal.query.get(goal_id)
    request_body = request.get_json()

    task_ids = request_body["task_ids"]
    task_list = [Task.query.get(task) for task in task_ids]

    for task in task_list:
        task.goal_id = goal.goal_id
        db.session.add(task)
        db.session.commit()

    return make_response({
        "id": goal.goal_id,
        "task_ids": task_ids
    }, 200)


@goal_bp.route("", methods=["GET"])
def get_all_goals():
    goals = Goal.query.all()

    goal_response = [{"id": goal.goal_id, "title": goal.title}
                     for goal in goals]

    return jsonify(goal_response)


@goal_bp.route("/<goal_id>", methods=["GET"])
def get_one_goal(goal_id):
    goal = Goal.query.get(goal_id)
    validate_data(goal)

    return make_response({"goal":
                          Goal.to_dict(goal)
                          }), 200


@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_task_from_goal(goal_id):
    goal = Goal.query.get(goal_id)
    validate_data(goal)

    tasks = [Task.to_dict(task) for task in goal.tasks]

    return make_response(jsonify({
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": tasks
    })), 200


@goal_bp.route("/<goal_id>", methods=["PUT"])
def edit_goal(goal_id):
    goal = Goal.query.get(goal_id)
    request_body = request.get_json(goal_id)

    if not goal:
        return make_response({"details": "Id not found"}), 400

    goal.title = request_body["title"]

    db.session.commit()

    return make_response({"goal":
                          Goal.to_dict(goal)
                          }), 201


@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = Goal.query.get(goal_id)
    validate_data(goal)

    db.session.delete(goal)
    db.session.commit()

    return make_response({
        f"details": f'Goal {goal_id} \"{goal.title}\" successfully deleted'
    }), 200
