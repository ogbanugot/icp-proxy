### README: FastAPI Reverse Proxy for Ensuring Idempotency in ICP Canisters

---

#### Overview

This project is a FastAPI-based reverse proxy designed to interface with Internet Computer Protocol (ICP) canisters. Its primary purpose is to ensure that all replicas of a canister receive the same response for identical requests, thereby achieving idempotency. The proxy forwards incoming HTTP requests to specified backend services and returns consistent responses to the ICP canisters.

#### Features

- **Path-Based Routing**: Routes requests to different backend services based on the URL path, allowing flexible integration with various backends.
- **Configurable via JSON**: Utilizes a configuration file (`conf.json`) to define routing rules and backend services, allowing easy updates and modifications without altering the proxy code.
- **Ensures Idempotency for ICP Canisters**: Caches responses based on unique request identifier ("Idempotency-Key") to ensure that all replicas of an ICP canister receive the same response for identical requests.
- **Simple Setup and Deployment**: Minimal dependencies and straightforward setup make it easy to run locally or deploy in cloud environments.
- **Supports Multiple HTTP Methods**: Capable of forwarding all standard HTTP methods such as GET, POST, PUT, DELETE, etc., ensuring broad compatibility with various backend services.

#### How It Works

1. **Request Handling**: The FastAPI application receives incoming HTTP requests from ICP canisters.
2. **Path Matching**: It checks the request path against the entries in the `conf.json` configuration file to determine the appropriate backend service.
3. **Request Forwarding with Idempotency**: If a match is found, the proxy forwards the request to the designated backend. It uses a unique key, such as the "Idempotency-Key" from the request headers, to cache the response.
4. **Response Relay**: The response from the backend service is cached and returned to the ICP canister. If the same request is received again (with the same "Idempotency-Key"), the proxy returns the cached response, ensuring consistent behavior across all replicas of the canister.

This proxy setup is particularly useful for ensuring consistent responses across all replicas of an ICP canister, maintaining the integrity and idempotency required in distributed environments.

#### Configuration File

The routing configuration is defined in a JSON file named `proxy_conf.json`. This file specifies which backend service each path should be routed to.

**Example `conf.json`:**

```json
{
    "/<route 1>": "https://<path to service>",
    "/<route 2>": "https://<path to service>",
}
```

- **Key**: The request path that the proxy should listen for.
- **Value**: The URL of the backend service to forward the request to.

#### Installation

**Install Dependencies**:

   Make sure you have Python 3.7+ installed. Install the required dependencies using pip:

   ```bash
   pip install fastapi uvicorn httpx
   ```

#### Running the Application

To start the FastAPI reverse proxy, run the following command:

```bash
uvicorn main:app --port 8080 --reload
```

- `main` refers to the Python file name (`main.py`).
- `app` refers to the FastAPI application instance created in that file.
- `--reload` enables auto-reload for code changes (useful during development).

#### Making Requests

You can make HTTP requests to your FastAPI reverse proxy using tools like `curl`, Postman, or any HTTP client library.

**Example Request:**

```bash
curl -X POST "http://localhost:8000/<route 1>" \
     -H "Content-Type: application/json" \
     -d '{"field 1": "value 1"}'
```

This request will be forwarded to the backend service as specified in the `proxy_conf.json` file.

#### Customization

To modify the routing behavior:

1. **Update `proxy_conf.json`**: Add, remove, or modify entries to change which backend services are used for different paths.
2. **Restart the FastAPI App**: After making changes to the configuration file, restart the FastAPI app to apply the new settings.

#### Troubleshooting

- **Invalid Backend URL**: Ensure all URLs in `proxy_conf.json` are correct and reachable.
- **CORS Issues**: If using in a browser environment, configure appropriate CORS settings for the backend services.
- **Logs**: Check the terminal output for error messages or use logging in FastAPI for more detailed logs.

---

#### Deploy on fly.io
Based on this https://fly.io/docs/languages-and-frameworks/dockerfile/

The launch command is optional if there is a `fly.toml` file already
```commandline
fly launch --no-deploy
```
deploy app
```commandline
fly deploy --ha=false
```
scale the memory
```commandline
flyctl scale memory 2048 -a termitebk
```
scale the vm
```commandline
fly scale vm shared-cpu-2x --vm-memory 4096 -a termitebk
```