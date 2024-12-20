import json
import logging
from typing import Annotated, Dict

from fastapi import APIRouter, Depends
from fastapi import Request, HTTPException, Response
import requests
from sqlalchemy.orm import Session

from database import get_db
from db_service import fetch_one_log, create_new_log, CacheRes
from depend import get_proxy_config

router = APIRouter()


@router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(
        request: Request,
        full_path: str,
        proxy_config: Annotated[Dict, Depends(get_proxy_config)],
        db: Session = Depends(get_db),
):
    path = "/" + full_path
    backend_url = None

    # Find the corresponding backend URL from the configuration
    for route, url in proxy_config.items():
        if path.startswith(route):
            backend_url = url + path
            break

    if not backend_url:
        logging.debug(f"No route found for path: {path}")
        raise HTTPException(status_code=404, detail="No route found for the given path")

    # Extract the "Idempotency-Key" from the request header
    idempotency_key = request.headers.get("Idempotency-Key")
    if idempotency_key:
        # Check if the response for this key is already cached
        result = fetch_one_log(db, idempotency_key)
        if result:
            logging.debug(f"Returning cached response for Idempotency-Key: {idempotency_key}")
            cached_response = result.response
            return Response(content=cached_response["content"], media_type=cached_response["media_type"])
    media_type = "application/json"

    try:
        logging.debug(f"Forwarding request to {backend_url}")
        # Forward the request to the appropriate backend
        response = requests.request(
            method=request.method,
            url=backend_url,
            headers=dict(request.headers),
            data=await request.body(),
            params=request.query_params
        )

        logging.debug(f"Received response with status code: {response.status_code}")

        # Check for compression
        response_content = response.content

        # Determine how to handle the response based on its content type
        content_type = response.headers.get("Content-Type", "")

        if "application/json" in content_type:
            # Handle JSON responses
            try:
                json_data = json.loads(response_content)
                response_content = json.dumps(json_data)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decoding error: {e}")
                result = fetch_one_log(db, idempotency_key)
                if result:
                    logging.debug(f"Returning cached response for Idempotency-Key: {idempotency_key}")
                    cached_response = result.response
                    return Response(content=cached_response["content"], media_type=cached_response["media_type"])

                response_json = json.dumps({
                    "content": response_content,
                    "media_type": media_type
                })
                result = create_new_log(db, CacheRes(
                    id=idempotency_key,
                    response=response_json
                ))
                if result:
                    print("Successfully cached result")
                return Response(content=response_content, media_type=media_type)

        elif "text/" in content_type or content_type == "":
            # Handle plain text or unspecified content types as text
            response_content = response_content.decode('utf-8')
            media_type = "text/plain" if content_type == "" else content_type
        else:
            # Handle binary data
            media_type = content_type

        # Cache the response if idempotency key was provided
        if idempotency_key:
            result = fetch_one_log(db, idempotency_key)
            if result:
                logging.debug(f"Returning cached response for Idempotency-Key: {idempotency_key}")
                cached_response = result.response
                return Response(content=cached_response["content"], media_type=cached_response["media_type"])

            response_json = json.dumps({
                    "content": response_content,
                    "media_type": media_type
                })
            result = create_new_log(db, CacheRes(
                id=idempotency_key,
                response=response_json
            ))
            if result:
                print("Successfully cached result")
        return Response(content=response_content, media_type=media_type)

    except Exception as e:
        response_content = str(f"Error while forwarding request: {str(e)}")
        logging.error(response_content)
        result = fetch_one_log(db, idempotency_key)
        if result:
            logging.debug(f"Returning cached response for Idempotency-Key: {idempotency_key}")
            cached_response = result.response
            return Response(content=cached_response["content"], media_type=cached_response["media_type"])

        response_json = json.dumps({
            "content": response_content,
            "media_type": media_type
        })
        result = create_new_log(db, CacheRes(
            id=idempotency_key,
            response=response_json
        ))
        if result:
            print("Successfully cached result")
        return Response(content=response_content, media_type=media_type)