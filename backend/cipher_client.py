import os
import threading
import time
from typing import Any

import httpx
import requests
from dotenv import load_dotenv

load_dotenv()


TOKEN_URL = "https://phenomics.va.ornl.gov/auth/oauth2/token"
BASE_URL = "https://phenomics.va.ornl.gov/web"


class CipherAPIError(RuntimeError):
    pass


class CipherClient:
    """Small CIPHER Web API client with OAuth2 client-credentials token caching."""

    def __init__(self) -> None:
        self.client_id = os.environ["CIPHER_CLIENT_ID"]
        self.client_secret = os.environ["CIPHER_CLIENT_SECRET"]
        self.base_url = os.getenv("CIPHER_BASE_URL", BASE_URL).rstrip("/")
        self.token_url = os.getenv("CIPHER_TOKEN_URL", TOKEN_URL)
        self.timeout = float(os.getenv("CIPHER_TIMEOUT_SECONDS", "30"))
        self._token: str | None = None
        self._token_expires_at = 0.0
        self._token_lock = threading.Lock()

    def _get_token(self) -> str:
        # Keep a 30-second safety margin on the nominal 5-minute token lifetime.
        if self._token and time.time() < self._token_expires_at - 30:
            return self._token

        with self._token_lock:
            if self._token and time.time() < self._token_expires_at - 30:
                return self._token

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.token_url,
                    auth=(self.client_id, self.client_secret),
                    data={"grant_type": "client_credentials"},
                    headers={"Accept": "application/json"},
                )
            self._raise_for_status(response, "requesting CIPHER access token")
            payload = response.json()
            self._token = payload["access_token"]
            self._token_expires_at = time.time() + int(payload.get("expires_in", 300))
            return self._token

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Accept": "application/json",
        }

    @staticmethod
    def _clean_params(params: dict[str, Any] | None) -> dict[str, Any]:
        if not params:
            return {}
        clean: dict[str, Any] = {}
        for key, value in params.items():
            if value is None:
                continue
            if isinstance(value, bool):
                clean[key] = str(value).lower()
            else:
                clean[key] = value
        return clean

    @staticmethod
    def _raise_for_status(response: httpx.Response, action: str) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body = response.text[:2000]
            raise CipherAPIError(
                f"CIPHER error while {action}: HTTP {response.status_code}: {body}"
            ) from exc

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}{path}",
                headers=self._headers(),
                params=self._clean_params(params),
            )
        self._raise_for_status(response, f"GET {path}")
        return response.json()

    def _post_search(
        self,
        path: str,
        request: dict[str, Any] | None,
        filters: list[dict[str, Any]] | None,
    ) -> Any:
        # In the uploaded OpenAPI 3.1 document, `request` is an object-valued
        # query parameter. The default query serialization is form+explode,
        # so its properties become ordinary query parameters.
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}{path}",
                headers={**self._headers(), "Content-Type": "application/json"},
                params=self._clean_params(request),
                json=filters or [],
            )
        self._raise_for_status(response, f"POST {path}")
        return response.json()

    def search_phenotypes(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        is_validated: bool | None = None,
        has_algorithm_code: bool | None = None,
        has_publication: bool | None = None,
        has_attachment: bool | None = None,
        sort_field: str | None = None,
        sort_order: str | None = None,
        filters: list[dict[str, Any]] | None = None,
    ) -> Any:
        request = {
            "query": query,
            "limit": max(1, min(limit, 50)),
            "offset": max(0, offset),
            "isValidated": is_validated,
            "hasAlgorithmCode": has_algorithm_code,
            "hasPublication": has_publication,
            "hasAttachment": has_attachment,
            "sortField": sort_field,
            "sortOrder": sort_order,
        }
        return self._post_search("/api/search/phenotypes", request, filters)

    def get_phenotype(self, phenotype_id: str, revision: str = "latest") -> Any:
        return self._get(f"/api/phenotype/{phenotype_id}", {"revision": revision})

    def query_phenotypes(
        self,
        phenotype_fullname: str | None = None,
        ids: list[int] | None = None,
        uqids: list[str] | None = None,
        limit: int = 10,
        offset: int = 0,
        exact: bool | None = None,
    ) -> Any:
        return self._get(
            "/api/phenotype/query",
            {
                "phenotype_fullname": phenotype_fullname,
                "ids": ids,
                "uqids": uqids,
                "limit": max(1, min(limit, 50)),
                "offset": max(0, offset),
                "exact": exact,
            },
        )

    def compare_phenotypes(
        self,
        base_id: int,
        compare_ids: list[int],
        fields: list[str] | None = None,
        review: bool = False,
    ) -> Any:
        return self._get(
            f"/api/phenotype/comparison/{base_id}",
            {
                "compareId": compare_ids,
                "fields": fields or [],
                "review": review,
            },
        )

    def search_variables(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        filters: list[dict[str, Any]] | None = None,
    ) -> Any:
        request = {"query": query, "limit": max(1, min(limit, 50)), "offset": max(0, offset)}
        return self._post_search("/api/search/variables", request, filters)

    def search_dictionaries(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        has_algorithm_component: bool | None = None,
        filters: list[dict[str, Any]] | None = None,
    ) -> Any:
        request = {
            "query": query,
            "limit": max(1, min(limit, 50)),
            "offset": max(0, offset),
            "hasAlgorithmComponent": has_algorithm_component,
        }
        return self._post_search("/api/search/dictionaries", request, filters)

    def get_dictionary(
        self,
        uqid: str,
        include_variables: bool = True,
        limit: int = 100,
    ) -> Any:
        return self._get(
            f"/api/data-dictionary/{uqid}",
            {"includeVariables": include_variables, "limit": max(1, min(limit, 500))},
        )

    def get_field_values(self, enum_type: str) -> Any:
        return self._get(f"/api/field/{enum_type}")
