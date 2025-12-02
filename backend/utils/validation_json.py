from functools import wraps
from flask import request, jsonify
from pydantic import BaseModel, ValidationError
from typing import Type, Optional
import uuid

def validate_json(model: Type[BaseModel], optional: bool = False):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            try:
                json_data = request.get_json()

                if optional and (json_data is None or json_data == {}):
                    kwargs['validated_data'] = None
                    return func(*args, **kwargs)
                
                if json_data is None:
                    return jsonify({
                        'error': 'Request must certain valid JSON data',
                        'details': {'expected': model.schema()}
                    }), 400

                validated_data = model(**json_data)
                kwargs['validated_data'] = validated_data
                return func(*args, **kwargs)
            except ValidationError as e:
                return jsonify({
                    'error': 'Request must certain valid JSON data',
                    'details': e.errors()
                }), 422
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        return decorated_function
    return decorator




def validate_uuid(uuid_string: str) -> bool:
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False