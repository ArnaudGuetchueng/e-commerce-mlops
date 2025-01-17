"""Routes to predict product categories."""

from io import BytesIO
from typing import Any, List

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

import app.api.dependencies as deps
from app import models, schemas
from datascience.classification import predict_prdtypecode
from datascience.src.data import CATEGORIES_DIC

router = APIRouter()


@router.post("/", response_model=List[schemas.PredictionResult])
async def predict_category(
    *,
    designation: str | None = None,
    description: str | None = None,
    image: UploadFile | None = None,
    limit: int | None = None,
    # Authentication and access management, do not delete!
    _current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Predict the category of the product.

    Raises:
        HTTPException: 400 if image extension is invalid.
        HTTPException: 400 if image format is invalid.
        HTTPException: 400 if limit is not a positive int.
        HTTPException: 400 if not enough data is provided.

    Returns:
        Prediction results with category id, probabilities and category label.
    """
    image_data = None
    if image is not None:
        extension = (
            False
            if image.filename is None
            else image.filename.split(".")[-1] in ("jpg", "jpeg")
        )
        if extension is False:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Invalid image extension. Image must be in JPEG or JPG format.",
            )
        try:
            # Open the image with PIL
            image_data = np.asarray(Image.open(BytesIO(await image.read())))
        except UnidentifiedImageError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image format. Image must be in JPEG or JPG format.",
            ) from exc

    if limit is not None and limit <= 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Invalid value for limit. Must be a positive integer.",
        )

    # Check if we have data. We need either text data or an image to do a prediction
    if designation is None and description is None and image is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="You must provide either designation/description or an image to get a result.",
        )

    # Get the predictions from model
    predictions = predict_prdtypecode(designation, description, image_data)
    # Since the predictions are sorted by probabilities descending, we just need to return
    # the {limit} first elements of the list
    result = [(i[0], i[1], CATEGORIES_DIC[i[0]]) for i in predictions[0][:limit]]

    return [
        schemas.PredictionResult(prdtypecode=i[0], probabilities=i[1], label=i[2])
        for i in result
    ]
