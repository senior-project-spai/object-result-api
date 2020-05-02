# fastapi
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, AnyUrl

# SQL
import mysql.connector

# Image
from PIL import Image, ImageDraw
from io import BytesIO
import base64

# S3 compatible storage
import s3

from config import MYSQL


def image_to_data_uri(img):
    '''
    Convert ``Image`` to ``Data URI``

    Args:
        ``img`` (PIL.Image)

    Returns
        ``str``: Data URI string
    '''
    buffered = BytesIO()
    # Save image to buffer
    img.save(buffered, 'JPEG')
    # Encode buffer to base64
    img_base64 = base64.b64encode(buffered.getvalue())
    data_uri_byte = bytes("data:image/jpeg;base64,",
                          encoding='utf-8') + img_base64
    data_uri_string = data_uri_byte.decode('utf-8')
    return data_uri_string


# Initialize FastAPI
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'])


class PositionModel(BaseModel):
    top: int
    right: int
    bottom: int
    left: int


class ImageModel(BaseModel):
    path: AnyUrl
    data_uri: str


class ObjectModel(BaseModel):
    id: int
    name: str
    probability: float
    position: PositionModel
    image: ImageModel


@app.get("/_api/object/{object_id_str}", response_model=ObjectModel)
def get_object_result(object_id_str: str):

    # Path parameter condition
    if object_id_str == 'latest':
        object_id = None
    else:
        # Get specific result by id
        object_id = int(object_id_str)

    # SQL query
    if object_id:
        query_object_result = ("SELECT id, name, probability, image_path, "
                               "       position_top, position_right, position_bottom, position_left "
                               "FROM object "
                               "WHERE id=%(object_id)s "
                               "LIMIT 1;")
    else:
        query_object_result = ("SELECT id, name, probability, image_path, "
                               "       position_top, position_right, position_bottom, position_left "
                               "FROM object "
                               "ORDER BY id DESC "
                               "LIMIT 1;")

    # Connect to database
    cnx = mysql.connector.connect(**MYSQL)
    # Create DictCursor
    cursor = cnx.cursor(dictionary=True)
    # Execute SQL query
    cursor.execute(query_object_result, {'object_id': object_id})
    # Store value
    object_result_row = cursor.fetchone()
    # Close cursor
    cursor.close()
    # Close connection
    cnx.close()

    # Return 404 if result not found
    if object_result_row is None:
        raise HTTPException(
            status_code=404, detail="Specified object was not found")

    # Get image
    object_image = Image.open(s3.get_file_stream(
        object_result_row['image_path']))

    # Draw box if all positions are not None
    if all([object_result_row['position_left'],
            object_result_row['position_top'],
            object_result_row['position_right'],
            object_result_row['position_bottom']]):
        draw = ImageDraw.Draw(object_image)
        # Define corner
        lt_corner = (object_result_row['position_left'],
                     object_result_row['position_top'])
        rb_corner = (object_result_row['position_right'],
                     object_result_row['position_bottom'])
        # Draw rectangle with red outline
        draw.rectangle([lt_corner, rb_corner], outline="red", width=2)

    return {
        'id': object_result_row['id'],
        'name': object_result_row['name'],
        'probability': object_result_row['probability'],
        'position': {
            'top': object_result_row['position_top'],
            'right': object_result_row['position_right'],
            'bottom': object_result_row['position_bottom'],
            'left': object_result_row['position_left'],
        },
        'image': {
            'path': object_result_row['image_path'],
            'data_uri': image_to_data_uri(object_image)
        }
    }
