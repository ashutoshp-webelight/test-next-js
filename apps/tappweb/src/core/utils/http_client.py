from typing import Any, Dict, List, Optional, Union

from aiohttp.client import ClientSession

from app.app.exceptions import RequestFailedException


class HTTPClient:
    def __init__(self, base_url: str, headers: Dict[str, str] = None) -> None:
        self.base_url = base_url
        self.headers = headers

    async def get(
        self, url: Optional[str] = None, headers: Dict[str, str] = None, params: Dict[str, str] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Send a GET request to the specified URL with the specified headers and parameters.

        :param url: (str, optional): The URL to send the request to. Defaults to None.
        :param headers: (dict, optional): A dictionary of headers to include in the request. Defaults to None.
        :param params: (dict, optional): A dictionary of parameters to include in the request. Defaults to None.
        :return: Union[Dict[str, Any], List[Dict[str, Any]]]: The response from the server, which can be either a
        dictionary or a list of dictionaries depending on the API endpoint being accessed.
        """
        async with ClientSession(base_url=self.base_url, headers=self.headers) as session:
            async with session.get(url if url else self.base_url, headers=headers, params=params) as response:
                if response.status in [200, 201, 203, 204]:
                    return await response.json()
                else:
                    raise RequestFailedException

    async def post(
        self,
        url: Optional[str] = None,
        headers: Dict[str, str] = None,
        params: Dict[str, str] = None,
        json: Dict[str, str] = None,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Submit a POST request to the specified URL with the given headers and payload.

        :param url: (str, optional): The URL to send the request to. Defaults to None.
        :param headers: (dict, optional): A dictionary of HTTP headers to include in the request. Defaults to None.
        :param params: (dict, optional): A dictionary of query parameters to include in the request URL.
        Defaults to None.
        :param json: (dict, optional): A dictionary containing the payload data to send with the request.
        Defaults to None.
        :return: Union[Dict[str, Any], List[Dict[str, Any]]]: The JSON response from the server.
        """
        async with ClientSession(base_url=self.base_url, headers=self.headers) as session:
            async with session.post(
                url if url else self.base_url, headers=headers, params=params, json=json
            ) as response:
                if response.status in [200, 201, 203, 204]:
                    return await response.json()
                else:
                    raise RequestFailedException

    async def put(
        self, url: Optional[str] = None, headers: Dict[str, str] = None, params: Dict[str, str] = None, json: str = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Sends a PUT request to the specified URL with the provided headers, parameters, and JSON data.

        :param url: (Optional[str]): The URL to send the request to. Defaults to None.
        :param headers: (Dict[str, str]): The headers to include in the request. Defaults to None.
        :param params: (Dict[str, str]): The query parameters to include in the request. Defaults to None.
        :param json: (str): The JSON data to include in the request body. Defaults to None.
        :return: Union[Dict[str, Any], List[Dict[str, Any]]]: A dictionary or list of dictionaries containing the
        response data.
        """
        async with ClientSession(base_url=self.base_url, headers=self.headers) as session:
            async with session.put(
                url if url else self.base_url, headers=headers, params=params, json=json
            ) as response:
                if response.status in [200, 201, 203, 204]:
                    return await response.json()
                else:
                    raise RequestFailedException

    async def delete(
        self, url: Optional[str] = None, headers: Dict[str, str] = None, params: Dict[str, str] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Deletes a resource at the specified URL.

        :param url: The URL of the resource to delete. If not specified, the URL of the current instance will be used.
        :param headers: A dictionary of HTTP headers to include with the request.
        :param params: A dictionary of query string parameters to include with the request.
        :return: A dictionary or list of dictionaries representing the deleted resource(s).
        """
        async with ClientSession(base_url=self.base_url, headers=self.headers) as session:
            async with session.delete(url if url else self.base_url, headers=headers, params=params) as response:
                if response.status in [200, 201, 203, 204]:
                    return await response.json()
                else:
                    raise RequestFailedException
